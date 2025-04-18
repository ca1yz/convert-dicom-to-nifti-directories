import os
import argparse
from pipeline import process_root_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert DICOM sequences to NIfTI with mapping.')
    parser.add_argument('dicom_root_dir', type=str,
                       help='Root directory containing DICOM files')
    parser.add_argument('-o', '--output_root_dir', type=str,
                       help='Output directory for NIfTI files')
    parser.add_argument('-e', '--error_log', action='store_true',
                       help='Log errors to error_log.csv')
    parser.add_argument('-s', '--split', action='store_true', default=False,
                       help='Split 4D NIfTI files into 3D volumes')
    parser.add_argument('--no-split', action='store_false', dest='split',
                       help='Explicitly disable splitting 4D NIfTI files')
    parser.add_argument('--log-debug', action='store_true',
                       help='Enable detailed debug logging to console')
    parser.add_argument('--threads', type=int, default=0,
                       help='Number of worker processes (default: all available)')

    args = parser.parse_args()

    if not args.dicom_root_dir:
        args.dicom_root_dir = input('Enter DICOM root directory: ')
    if not args.output_root_dir:
        args.output_root_dir = input('Enter output directory: ')
    if args.threads <= 0:
        args.threads = os.cpu_count()
        print(f"Using default number of workers: {args.threads}")

    os.makedirs(args.output_root_dir, exist_ok=True)

    process_root_dir(args.dicom_root_dir,
                     args.output_root_dir,
                     args.threads,
                     args.error_log,
                     args.split,
                     args.log_debug)
