import os
import uuid
import shutil
import tempfile
import pandas as pd
import concurrent.futures
import pyarrow.parquet as pq
from tqdm import tqdm
from typing import List, Dict, Any
from nifti_utils import split_4d_to_3d
from conversion import convert_sequence_to_nifti
from dicom_utils import extract_all_metadata, analyze_dicom_sequences

def process_sequence_and_save(
    dicom_files: List[str],
    output_dir: str,
    sequence_name: str,
    temp_results_dir: str,
    split: bool,
    log_debug: bool
) -> Dict[str, Any]:
    """
    Converts a single DICOM sequence, optionally splits, extracts metadata,
    and saves the result(s) to a temporary Parquet file.

    Returns a dictionary containing 'results' (list of dicts) and 'errors' (list of dicts).
    """
    if not dicom_files:
        return {'results': [], 'errors': [{'SequenceName': sequence_name, 'Step': 'Input', 'Error': 'No DICOM files provided'}]}

    first_dicom_file_for_meta = dicom_files[0]
    task_results = []
    task_errors = []

    if log_debug: print(f"DEBUG: Starting sequence {sequence_name} ({len(dicom_files)} files)")

    try:
        # 1. Convert Sequence to NIfTI
        if log_debug: print(f"DEBUG: Converting sequence {sequence_name}")
        conversion_result = convert_sequence_to_nifti(dicom_files, output_dir, sequence_name)
        nifti_file_initial = conversion_result['output_file']
        if log_debug: print(f"DEBUG: Converted {sequence_name} to {nifti_file_initial}")

        # 2. Handle potential 4D splits
        processed_nifti_files = []
        if split:
            try:
                if log_debug: print(f"DEBUG: Attempting to split {nifti_file_initial}")
                split_mappings = split_4d_to_3d(first_dicom_file_for_meta, nifti_file_initial)
                processed_nifti_files = [mapping[1] for mapping in split_mappings]
                if log_debug: print(f"DEBUG: Split {nifti_file_initial} into {len(processed_nifti_files)} files")
            except Exception as e:
                task_errors.append({'SequenceName': sequence_name, 'NiftiFile': nifti_file_initial, 'Step': 'Split', 'Error': str(e)})
                if log_debug: print(f"DEBUG: Error during split for {nifti_file_initial}: {e}")
        else:
            processed_nifti_files = [nifti_file_initial]

        if log_debug: print(f"DEBUG: NIfTI files to process metadata for {sequence_name}: {processed_nifti_files}")

        # 3. Extract Metadata for each resulting NIfTI file
        for nifti_file in processed_nifti_files:
            try:
                if log_debug: print(f"DEBUG: Extracting metadata for {nifti_file} using {first_dicom_file_for_meta}")
                metadata = extract_all_metadata(first_dicom_file_for_meta)
                result_row = {
                    'FirstDicomFile': first_dicom_file_for_meta,
                    'NiftiFile': nifti_file,
                    **metadata
                }
                task_results.append(result_row)
            except Exception as e:
                task_errors.append({'SequenceName': sequence_name, 'FirstDicomFile': first_dicom_file_for_meta, 'NiftiFile': nifti_file, 'Step': 'Metadata', 'Error': str(e)})
                if log_debug: print(f"DEBUG: Error during metadata extraction for {first_dicom_file_for_meta} -> {nifti_file}: {e}")

    except Exception as e:
        task_errors.append({'SequenceName': sequence_name, 'FirstDicomFile': first_dicom_file_for_meta, 'Step': 'Conversion/Processing', 'Error': str(e)})
        if log_debug: print(f"DEBUG: Top-level error processing sequence {sequence_name}: {e}")

    # 4. Save results for this sequence to a temporary Parquet file
    if task_results:
        try:
            temp_df = pd.DataFrame(task_results)
            temp_file_path = os.path.join(temp_results_dir, f"seq_{sequence_name}_{uuid.uuid4()}.parquet")
            if log_debug: print(f"DEBUG: Saving temporary parquet file: {temp_file_path} for sequence {sequence_name}")
            temp_df.to_parquet(temp_file_path, engine='pyarrow')
        except Exception as e:
            task_errors.append({'SequenceName': sequence_name, 'Step': 'SaveTempParquet', 'Error': str(e)})
            if log_debug: print(f"DEBUG: Error saving temp parquet for sequence {sequence_name}: {e}")
            task_results = []
    else:
        if log_debug: print(f"DEBUG: No results generated for sequence {sequence_name} to save.")

    if log_debug: print(f"DEBUG: Finished processing sequence {sequence_name}. Results: {len(task_results)}, Errors: {len(task_errors)}")

    return {'results': task_results, 'errors': task_errors}

def process_root_dir(dicom_root_dir: str,
                        output_root_dir: str,
                        num_workers: int = 32,
                        error_log: bool = False,
                        split: bool = True,
                        log_debug: bool = False):
    """Process directory, analyzing sequences first, then processing each sequence in parallel."""

    error_list = []

    print("Scanning directories and analyzing sequences...")
    sequence_tasks = []
    dicom_dirs_found = 0
    total_sequences_found = 0

    for dirpath, dirnames, _ in os.walk(dicom_root_dir):
        if not dirnames:
            dicom_dirs_found += 1
            if log_debug: print(f"DEBUG: Analyzing sequences in: {dirpath}")
            try:
                analysis_result = analyze_dicom_sequences(dirpath)
                num_seq_in_dir = len(analysis_result['sequences'])
                total_sequences_found += num_seq_in_dir
                if log_debug: print(f"DEBUG: Found {num_seq_in_dir} sequences in {dirpath}")

                if num_seq_in_dir > 0:
                    relative_path = os.path.relpath(dirpath, dicom_root_dir)
                    current_output_dir = os.path.join(output_root_dir, relative_path)
                    os.makedirs(current_output_dir, exist_ok=True)

                    for seq_key, dicom_files in analysis_result['sequences'].items():
                        if seq_key in analysis_result['sequence_names']:
                            seq_name = analysis_result['sequence_names'][seq_key]
                            task_info = {
                                'dicom_files': dicom_files,
                                'output_dir': current_output_dir,
                                'sequence_name': seq_name,
                            }
                            sequence_tasks.append(task_info)
                        else:
                            error_list.append({'DicomDir': dirpath, 'SequenceKey': seq_key, 'Step': 'ScanPhase', 'Error': 'Sequence key found but name missing in analysis result.'})
                            if log_debug: print(f"DEBUG: ERROR - Missing sequence name for key {seq_key} in {dirpath}")

            except Exception as e:
                error_list.append({'DicomDir': dirpath, 'Step': 'AnalyzeSequences', 'Error': str(e)})
                print(f"ERROR: Failed to analyze sequences in {dirpath}: {e}")

    print(f"Scan complete. Found {dicom_dirs_found} leaf directories containing {total_sequences_found} sequences to process.")

    if not sequence_tasks:
        print("No valid DICOM sequences found to process.")
        return

    temp_results_dir = tempfile.mkdtemp(dir=output_root_dir, prefix="dicom_seq_results_")
    print(f"Using temporary directory for sequence results: {temp_results_dir}")

    print(f"Submitting {len(sequence_tasks)} sequence tasks to {num_workers} workers...")
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_seq_name = {
            executor.submit(process_sequence_and_save,
                            task['dicom_files'],
                            task['output_dir'],
                            task['sequence_name'],
                            temp_results_dir,
                            split,
                            log_debug): task['sequence_name']
            for task in sequence_tasks
        }

        for future in tqdm(concurrent.futures.as_completed(future_to_seq_name),
                           total=len(sequence_tasks),
                           desc="Processing Sequences"):
            seq_name = future_to_seq_name[future]
            try:
                task_output = future.result()
                if task_output.get('errors'):
                    error_list.extend(task_output['errors'])
            except Exception as e:
                error_list.append({'SequenceName': seq_name, 'Step': 'Executor', 'Error': str(e)})
                print(f"ERROR: Executor failed for task processing sequence {seq_name}: {e}")

    print("Aggregating results...")
    all_temp_files = [os.path.join(temp_results_dir, f)
                      for f in os.listdir(temp_results_dir) if f.endswith('.parquet')]

    if not all_temp_files:
        print("No sequence results were successfully saved.")
        final_df = pd.DataFrame()
    else:
        print(f"Found {len(all_temp_files)} temporary result files.")
        try:
            dataset = pq.ParquetDataset(all_temp_files)
            table = dataset.read()
            final_df = table.to_pandas()
            print(f"Successfully aggregated {len(final_df)} entries.")
        except Exception as e:
            print(f"Error aggregating Parquet files: {e}")
            print("Attempting to read files individually...")
            all_dfs = []
            for f in tqdm(all_temp_files, desc="Reading temp files"):
                try:
                    df_part = pd.read_parquet(f)
                    all_dfs.append(df_part)
                except Exception as read_err:
                    print(f"Could not read temporary file {f}: {read_err}")
                    error_list.append({'File': f, 'Step': 'AggregationFallbackRead', 'Error': str(read_err)})
            if all_dfs:
                final_df = pd.concat(all_dfs, ignore_index=True)
                print(f"Successfully aggregated {len(final_df)} entries using fallback.")
            else:
                print("Fallback aggregation failed. No data loaded.")
                final_df = pd.DataFrame()

    try:
        shutil.rmtree(temp_results_dir)
        print(f"Removed temporary directory: {temp_results_dir}")
    except Exception as e:
        print(f"Warning: Could not remove temporary directory {temp_results_dir}: {e}")

    if not final_df.empty:
        parquet_path = os.path.join(output_root_dir, 'nifti_dicom_mapping.parquet')
        try:
            final_df.to_parquet(parquet_path, engine='pyarrow', index=False)
            print(f"Final mapping saved to: {parquet_path}")
        except Exception as e:
            print(f"Error saving final Parquet file: {e}")
            error_list.append({'File': parquet_path, 'Step': 'SaveFinalParquet', 'Error': str(e)})
            csv_path = os.path.join(output_root_dir, 'nifti_dicom_mapping_fallback.csv')
            try:
                final_df.to_csv(csv_path, index=False)
                print(f"Saved fallback mapping to CSV: {csv_path}")
            except Exception as csv_e:
                print(f"Error saving fallback CSV file: {csv_e}")
                error_list.append({'File': csv_path, 'Step': 'SaveFallbackCSV', 'Error': str(csv_e)})
    else:
        print("No data to save in the final mapping file.")

    if error_log and error_list:
        error_df = pd.DataFrame(error_list)
        error_log_path = os.path.join(output_root_dir, 'error_log.csv')
        try:
            error_df.to_csv(error_log_path, index=False)
            print(f"Error log saved to: {error_log_path}")
        except Exception as e:
            print(f"Error saving error log: {e}")
    elif error_log:
        print("No errors recorded during processing (or error logging disabled).")
