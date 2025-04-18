import os
import pydicom
import hashlib
from collections import defaultdict
from typing import Union
import re # Need re for sanitization

def sanitize_filename(name):
    """Removes or replaces characters unsuitable for filenames."""
    # Remove characters like / \ : * ? " < > |
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    # Replace spaces with underscores (optional)
    name = name.replace(' ', '_')
    # Limit length (optional)
    # max_len = 100
    # name = name[:max_len]
    return name

def create_sequence_name(metadata: dict, sequence_key: str) -> str:
    """Creates a descriptive filename using multiple DICOM tags."""
    try:
        # Extract required fields with defaults
        # patient_id = metadata.get('PatientID', 'NoPatientID')
        study_date = metadata.get('StudyDate', 'NoStudyDate')
        series_num = metadata.get('SeriesNumber', 'NoSeriesNum')
        series_desc = metadata.get('SeriesDescription', 'NoSeriesDesc')

        # Sanitize components
        # patient_id = sanitize_filename(str(patient_id))
        study_date = sanitize_filename(str(study_date))
        series_num = sanitize_filename(str(series_num)).zfill(4) # Pad series number
        series_desc = sanitize_filename(str(series_desc))

        # Combine (ensure no leading/trailing underscores if components are missing)
        parts = [part for part in [study_date, series_num, series_desc] if part and not part.startswith('No')]
        if not parts: # Fallback if all key info is missing
             return f"UnknownSequence_{sequence_key[:8]}"
        
        return "_".join(parts)

    except Exception as e:
        print(f"Warning: Error creating sequence name for key {sequence_key}: {e}")
        return f"ErrorSequence_{sequence_key[:8]}"

def analyze_dicom_sequences(folder_path: str) -> dict:
    """
    Analyze DICOM files in a folder and group them by relevant metadata.
    Skips files that are missing SeriesInstanceUID.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
        
    Returns:
        dict: Dictionary with sequence information
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return {'sequences': {}, 'sequence_names': {}, 'total_files': 0, 'non_dicom_files': 0} 
    
    sequences = defaultdict(list)
    sequence_names = {}
    total_files = 0
    non_dicom_files = 0
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        total_files += 1
        
        if os.path.isdir(file_path):
            continue
        
        try:
            dicom_data = pydicom.dcmread(file_path, stop_before_pixels=True, force=True)
            
            # Ensure SeriesInstanceUID exists AND is not empty/None before proceeding
            series_uid = getattr(dicom_data, 'SeriesInstanceUID', None)
            if not series_uid:
                 print(f"Warning: Skipping file {filename} in {folder_path} - Missing or empty SeriesInstanceUID. File will not be converted.")
                 non_dicom_files += 1
                 continue

            sequence_key = create_sequence_key(dicom_data) # Now guaranteed to have a valid UID
            
            # Add file to sequence
            sequences[sequence_key].append(file_path)

            # Only create sequence name if it doesn't exist for this key yet
            if sequence_key not in sequence_names:
                try:
                    metadata_for_name = extract_metadata(dicom_data) 
                    # Use SeriesDescription if available, otherwise fallback
                    series_desc = metadata_for_name.get('SeriesDescription', 'UnknownSeries')
                    if series_desc == 'UnknownSeries':
                         print(f"Warning: Using fallback name for sequence {sequence_key} in {folder_path} - Missing SeriesDescription")
                         sequence_names[sequence_key] = f"UnknownSequence_{sequence_key[:8]}"
                    else:
                         sequence_names[sequence_key] = create_sequence_name(metadata_for_name, sequence_key)

                except Exception as name_err:
                     print(f"Warning: Error generating name for sequence {sequence_key} from file {filename} in {folder_path}: {name_err}. Using fallback.")
                     sequence_names[sequence_key] = f"ErrorSequence_{sequence_key[:8]}" 

        except Exception as read_err:
            # print(f"Warning: Skipping non-DICOM or problematic file {filename} in {folder_path}: {read_err}") 
            non_dicom_files += 1
            continue
            
    # Ensure sequence_names has keys for all sequences found
    # This is usually guaranteed by the logic above, but as a safeguard:
    for key in sequences:
        if key not in sequence_names:
             print(f"Warning: Fallback name needed post-loop for sequence {key} in {folder_path}.")
             sequence_names[key] = f"FallbackSequence_{key[:8]}"

    return {
        'sequences': dict(sequences), 
        'sequence_names': sequence_names,
        'total_files': total_files,
        'non_dicom_files': non_dicom_files
    }

def create_sequence_key(dicom_data: pydicom.dataset.Dataset) -> str:
    """
    Create a unique key for a DICOM sequence based on its metadata.
    
    Args:
        dicom_data: DICOM dataset
        
    Returns:
        str: MD5 hash key representing the sequence
    """
    key_elements = [
        str(getattr(dicom_data, 'SeriesInstanceUID', 'Unknown')),
    ]
    
    # Create a hash-based key to group similar sequences
    return hashlib.md5('|'.join(key_elements).encode()).hexdigest()

def extract_metadata(dicom_data: pydicom.dataset.Dataset) -> dict:
    metadata = {}
    metadata['PatientID'] = getattr(dicom_data, 'PatientID', None)
    metadata['StudyDate'] = getattr(dicom_data, 'StudyDate', None)
    metadata['SeriesNumber'] = getattr(dicom_data, 'SeriesNumber', None)
    metadata['SeriesDescription'] = getattr(dicom_data, 'SeriesDescription', None)
    metadata['SeriesInstanceUID'] = getattr(dicom_data, 'SeriesInstanceUID', None) # Keep UID
    # Add other essential fields if needed
    return metadata

def extract_all_metadata(dicom_data: Union[pydicom.dataset.Dataset, str]) -> dict:
    """Extract metadata from DICOM file"""
    try:
        if isinstance(dicom_data, str):
            dicom_data = pydicom.dcmread(dicom_data)

        metadata = {}
        
        for elem in dicom_data:
            if (elem.VR not in ['OB', 'OW', 'OF', 'OD', 'UN', 'SQ'] and 
                not isinstance(elem.value, bytes)):
                try:
                    if elem.VR == 'PN':
                        metadata[elem.name] = str(elem.value).replace('^', ' ').strip()
                    elif elem.VR == 'DS':
                        try:
                            if isinstance(elem.value, (list, tuple)):
                                metadata[elem.name] = [float(x) for x in elem.value]
                            else:
                                metadata[elem.name] = float(elem.value)
                        except:
                            metadata[elem.name] = str(elem.value)
                    elif isinstance(elem.value, (list, tuple)):
                        metadata[elem.name] = [str(x).strip() for x in elem.value]
                    else:
                        metadata[elem.name] = str(elem.value).strip()
                except Exception:
                    continue
                    
        return metadata
    except Exception as e:
        return {}
