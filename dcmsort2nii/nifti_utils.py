import os
import numpy as np
import nibabel as nib   
from typing import List, Tuple  

def split_4d_to_3d(dcm_file: str, nifti_file: str) -> List[Tuple[str, str]]:
    """Split 4D NIfTI, return [(dcm_file, nifti_file[i] ) for i in range(nifti_file.shape[3])]
    
    Args:
        dcm_file (str): Path to the DICOM files[0]
        nifti_file (str): Path to the NIfTI file
        
    Returns:
        List[Tuple[str, str]]: List of tuples of DICOM file and NIfTI file
    """
    
    try:
        img = nib.load(nifti_file)
        data = np.asanyarray(img.dataobj)
        
        if len(data.shape) == 3:
            return [(dcm_file, nifti_file)]
        
        elif len(data.shape) == 4:
            # split 4D to 3D
            output_files = []
            output_dir = os.path.dirname(nifti_file)
            base_name = os.path.splitext(os.path.splitext(os.path.basename(nifti_file))[0])[0]

            for i in range(data.shape[3]):
                vol_data = data[:, :, :, i]
                img_3d = nib.Nifti1Image(vol_data, img.affine, img.header)
                new_file = os.path.join(output_dir, f'{base_name}_vol_{i:04d}.nii.gz')
                nib.save(img_3d, new_file)
                output_files.append(new_file)
            
            os.remove(nifti_file)

            new_mappings = [(dcm_file, new_file) for new_file in output_files]
            return new_mappings
        
    except Exception as e:
        print(f"Error splitting file {nifti_file}: {e}")
        return []
