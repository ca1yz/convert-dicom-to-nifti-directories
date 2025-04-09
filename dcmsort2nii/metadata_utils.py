import os
import pydicom
import hashlib
from collections import defaultdict
from typing import Union

def create_sequence_name(metadata: dict, sequence_key: str) -> str:
    series_desc = metadata['SeriesDescription'].replace(' ', '_').replace('/', '_').replace('\\', '_')
    return f"{series_desc}_{sequence_key[:8]}" 

def analyze_dicom_sequences(folder_path: str) -> dict:
    """
    Analyze DICOM files in a folder and group them by relevant metadata.
    
    Args:
        folder_path (str): Path to the folder containing DICOM files
        
    Returns:
        dict: Dictionary with sequence information
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return None
    
    # Dictionary to store sequence information
    sequences = defaultdict(list)
    sequence_names = {}
    
    # Count total files and non-DICOM files
    total_files = 0
    non_dicom_files = 0
    
    # Process each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        total_files += 1
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Try to read the file as DICOM
        try:
            dicom_data = pydicom.dcmread(file_path, force=False)
            
            # Create a unique key based on important sequence parameters
            sequence_key = create_sequence_key(dicom_data)
            
            # Store file in the appropriate sequence
            sequences[sequence_key].append(file_path)
            sequence_names[sequence_key] = create_sequence_name(extract_metadata(dicom_data), sequence_key)

        except Exception:
            non_dicom_files += 1
            continue
    
    return {
        'sequences': sequences,
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
    """
    Extract relevant metadata from a DICOM dataset.
    
    Args:
        dicom_data: DICOM dataset
        
    Returns:
        dict: Dictionary of metadata values
    """
    return {
        'SeriesInstanceUID': str(getattr(dicom_data, 'SeriesInstanceUID', 'Unknown')),
        'SeriesDescription': str(getattr(dicom_data, 'SeriesDescription', 'Unknown')),
        'Modality': str(getattr(dicom_data, 'Modality', 'Unknown')),
        'SequenceName': str(getattr(dicom_data, 'SequenceName', 'Unknown')),
        'ProtocolName': str(getattr(dicom_data, 'ProtocolName', 'Unknown')),
        'ImageType': str(getattr(dicom_data, 'ImageType', 'Unknown')),
        'ScanningSequence': str(getattr(dicom_data, 'ScanningSequence', 'Unknown')),
        'SequenceVariant': str(getattr(dicom_data, 'SequenceVariant', 'Unknown')),
        'Rows': str(getattr(dicom_data, 'Rows', 'Unknown')),
        'Columns': str(getattr(dicom_data, 'Columns', 'Unknown')),
        'SliceThickness': str(getattr(dicom_data, 'SliceThickness', 'Unknown')),
        'RepetitionTime': str(getattr(dicom_data, 'RepetitionTime', 'Unknown')),
        'EchoTime': str(getattr(dicom_data, 'EchoTime', 'Unknown')),
    } 

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
