import os
import tempfile
import shutil
import dicom2nifti
from typing import List, Tuple  
from metadata_utils import analyze_dicom_sequences
from exception import ConversionError, suppress_stdout_stderr

def convert_single_folder(dicom_dir: str, output_dir: str) -> List[Tuple[str, str]]:
    """Convert a single folder of DICOM files, which may contain multiple sequences, to NIfTI format.
    
    Args:
        dicom_dir (str): Path to the DICOM directory
        output_dir (str): Path to the output directory
        
    Returns:
        List[Tuple[str, str]]: mapping of first DICOM file to output file path
    """
    
    result = analyze_dicom_sequences(dicom_dir)
    mapping = []

    # Convert sequences
    for sequence_key, dicom_files in result['sequences'].items():
        sequence_name = result['sequence_names'][sequence_key]
        
        try:
            conversion_result = convert_sequence_to_nifti(dicom_files, output_dir, sequence_name)
            mapping.append((conversion_result['first_dicom_file'], conversion_result['output_file']))
        except Exception as e:
            # print(f"Error converting sequence {sequence_name}: {e}")
            # do not raise error, otherwise the loop breaks. Option to collect all errors and raise them at the end.
            pass

    return mapping


def convert_sequence_to_nifti(dicom_files: list, output_dir: str, sequence_name: str) -> dict:
    """
    Convert a sequence of DICOM files to NIfTI format.
    
    Args:
        dicom_files (list): List of DICOM file paths
        output_dir (str): Directory to save the NIfTI file
        sequence_name (str): Name to use for the output file
        
    Returns:
        dict: Conversion result information
    """
    try:
        # Create a temporary directory to organize the DICOM files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy DICOM files to the temporary directory
            copy_files_to_temp_dir(dicom_files, temp_dir)
            
            # Create output filename
            output_file = os.path.join(output_dir, f"{sequence_name}.nii.gz")

            with tempfile.TemporaryDirectory() as temp_output_dir:  
                # Convert to NIfTI using a temporary output directory
                try:
                    # Suppress stdout/stderr during conversion
                    with suppress_stdout_stderr():
                        dicom2nifti.convert_directory(temp_dir, temp_output_dir, compression=True, reorient=True)

                    # Move the output file to the final destination
                    shutil.move(os.path.join(temp_output_dir, os.listdir(temp_output_dir)[0]), output_file)

                except Exception as e:
                    raise ConversionError(f"dicom2nifti.convert_directory failed converting {len(dicom_files)} files: {dicom_files[0]}")

            return {
                'first_dicom_file': dicom_files[0],
                'output_file': output_file,
            }
    
    except Exception as e:
        raise e

def copy_files_to_temp_dir(dicom_files, temp_dir):
    """
    Copy DICOM files to a temporary directory with sequential naming.
    
    Args:
        dicom_files (list): List of DICOM file paths
        temp_dir (str): Temporary directory path
    """
    for i, file_path in enumerate(dicom_files):
        shutil.copy2(file_path, os.path.join(temp_dir, f"file_{i:06d}.dcm")) 

