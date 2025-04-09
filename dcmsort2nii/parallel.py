import os
import argparse
import pandas as pd
import concurrent.futures
from tqdm import tqdm
from post_processing import split_4d_to_3d
from conversion import convert_single_folder
from metadata_utils import extract_all_metadata

def process_root_dir(dicom_root_dir: str, 
                        output_root_dir: str, 
                        num_workers: int = 32, 
                        error_log: bool = False, 
                        split: bool = True):
    """Process directory and create mapping CSV"""

    error_logger = pd.DataFrame(columns=['DicomFile', 'Error'])
    
    print("Scanning directories...")
    # Get all leaf directories
    dicom_dirs = []
    for dirpath, dirnames, _ in os.walk(dicom_root_dir):
        if not dirnames:
            dicom_dirs.append(dirpath)
    
    total_dirs = len(dicom_dirs)
    print(f"Found {total_dirs} DICOM directories to process")
    
    # Create output directories
    output_dirs = [os.path.join(output_root_dir, os.path.relpath(d, dicom_root_dir)) 
                  for d in dicom_dirs]
    for d in output_dirs:
        os.makedirs(d, exist_ok=True)
    
    # Convert DICOM to NIfTI using concurrent.futures
    tasks = list(zip(dicom_dirs, output_dirs))
    results = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_task = {executor.submit(convert_single_folder, d, o): (d, o) for d, o in tasks}
        for future in tqdm(concurrent.futures.as_completed(future_to_task), total=len(tasks), desc="Converting DICOM to NIfTI"):
            try:
                result = future.result()
                results.extend(result)
            except Exception as e:
                dicom_dir, output_dir = future_to_task[future]
                # print(f'Processing {dicom_dir} generated an exception: {exc}')
                if error_log:
                    error_logger.loc[len(error_logger)] = [dicom_dir, str(e)]
    
    # Process results and handle 4D splits
    if split:
        new_mappings = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_result = {executor.submit(split_4d_to_3d, *r): r for r in results}
            for future in tqdm(concurrent.futures.as_completed(future_to_result), total=len(results), desc="Splitting 4D files"):
                try:
                    result = future.result()
                    new_mappings.extend(result)
                except Exception as e:
                    pass
    else:
        new_mappings = results

    mapping_df = pd.DataFrame(new_mappings, columns=['FirstDicomFile', 'NiftiFile'])

    # Extracting DICOM metadata...
    total_rows = len(mapping_df)
    metadata_results = {}
    
    # Extract metadata using concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_index = {executor.submit(extract_all_metadata, row['FirstDicomFile']): i 
                          for i, row in mapping_df.iterrows()}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_index), 
                          total=total_rows, desc="Extracting metadata"):
            index = future_to_index[future]
            try:
                metadata = future.result()
                metadata_results[index] = metadata
            except Exception as e:
                pass
    
    # Convert metadata results to DataFrame
    metadata_df = pd.DataFrame.from_dict(metadata_results, orient='index')
    metadata_df.index = metadata_results.keys()
    metadata_df = metadata_df.reindex(range(len(mapping_df)))
    
    final_df = pd.concat([mapping_df, metadata_df], axis=1)
    
    # Save to excel
    print("Saving excel file...")
    excel_path = os.path.join(output_root_dir, 'nifti_dicom_mapping.xlsx')
    final_df.to_excel(excel_path, index=False)
    print(f"Excel saved to: {excel_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert DICOM to NIfTI with mapping.')
    parser.add_argument('dicom_root_dir', type=str, 
                       help='Root directory containing DICOM files')
    parser.add_argument('-o', '--output_root_dir', type=str, 
                       help='Output directory for NIfTI files')
    parser.add_argument('-e', '--error_log', type=bool, default=False, 
                       help='whether to log errors')
    parser.add_argument('-s', '--split', type=bool, default=True, 
                       help='whether to split 4D NIfTI files')
    parser.add_argument('--threads', type=int, default=0, 
                       help='Number of threads (default: all available)')
    
    args = parser.parse_args()
    
    if not args.dicom_root_dir:
        args.dicom_root_dir = input('Enter DICOM root directory: ')
    if not args.output_root_dir:
        args.output_root_dir = input('Enter output directory: ')
    if args.threads == 0:
        args.threads = os.cpu_count()
    
    os.makedirs(args.output_root_dir, exist_ok=True)
    
    process_root_dir(args.dicom_root_dir, 
                                   args.output_root_dir, 
                                   args.threads,
                                   args.error_log,
                                   args.split)
