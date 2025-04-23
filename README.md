**English** | [中文](./README_zh.md)

---

# Dcmsort2nii

## Introduction

Dealing with medical imaging data often involves the challenging task of converting large, sometimes disorganized, collections of DICOM files into the NIfTI format required by many analysis pipelines. If you've ever wrestled with organizing files scattered across nested directories or struggled to correctly identify different imaging sequences (especially with multi-site or inconsistently structured data), you know it can be a significant bottleneck.

`dcmsort2nii` aims to alleviate this headache. It acts as a smart wrapper around the excellent `dicom2nifti` library, adding **key features** designed to streamline the batch processing of complex datasets. Our goal is to make the often-tedious first step of DICOM organization and conversion much simpler and faster:

*   **Handles Complex Structures**: Simply point it at your main DICOM directory, and it intelligently scans through all subdirectories to find your data.
*   **Automatic Sequence Grouping**: Analyzes DICOM headers within each patient/study folder to automatically identify and group different imaging sequences, even if they're mixed together.
*   **Accelerated Conversion**: Leverages multiple CPU cores for parallel processing, significantly speeding up conversion for large datasets.
*   **Essential Metadata Tracking**: Generates a detailed `.parquet` file (with a `.csv` fallback) that maps every output NIfTI file back to its original DICOM sequence details and source files – crucial for reproducibility and traceability!
*   **Flexible 4D Handling**: Optionally splits 4D NIfTI files (common for fMRI or DWI) into individual 3D volumes, useful for specific analysis or model training needs.
*   **Easy Deployment**: Includes a Dockerfile for straightforward deployment (recommended), but is also installable via pip/conda.

### Example Input / Output

See a practical example in action here: [./example/example_notebook.ipynb](./example/example_notebook.ipynb)

## Installation

Firts clone the repo.
```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

There are two primary ways to use `dcmsort2nii`:

### 1. Docker (Recommended)

Using Docker is the recommended method as it encapsulates all dependencies and ensures consistent execution across different environments.

**a. Build the Docker Image:**

Navigate to the project's root directory (where the `Dockerfile` is located) and run:

```bash
docker build -t dcmsort2nii:latest .
```

**b. Run the Docker Container:**

Change the `INPUT_DIR` and `OUTPUT_DIR` to your desired paths.
```bash
INPUT_DIR=/path/to/your/dicom_root_dir
OUTPUT_DIR=/path/to/your/output

mkdir -p $OUTPUT_DIR # prevent permission errors

docker run --rm \
  -u "$(id -u):$(id -g)"\
  -v $INPUT_DIR:/data/input:ro \
  -v $OUTPUT_DIR:/data/output \
  dcmsort2nii:latest \
  /data/input -o /data/output --split --log_error
```

example output:
```bash
$ docker run --rm \      
  -v "$(pwd)/example/sample_data":/data/input:ro \
  -v "$(pwd)/example/sample_docker_output":/data/output \
  dcmsort2nii:latest \
  /data/input -o /data/output --split --log_error

Using default number of workers: 32
Scanning directories and analyzing sequences...
Scan complete. Found 9 leaf directories containing 31 sequences to process.
Using temporary directory for sequence results: /data/output/dicom_seq_results_o5pk439z
Submitting 31 sequence tasks to 32 workers...
Processing Sequences: 100%|██████████| 31/31 [00:09<00:00,  3.21it/s]
Aggregating results...
Found 26 temporary result files.
Successfully aggregated 34 entries.
Removed temporary directory: /data/output/dicom_seq_results_o5pk439z
Final mapping saved to: /data/output/nifti_dicom_mapping.parquet
Error log saved to: /data/output/error_log.csv
```

### 2. Conda Installation

If you prefer to install the tool without Docker, you can use the following steps:

**a. Create virtual environment and install the tool:**

```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -e .
```

**b. Run the Tool:**

```bash
dcmsort2nii /path/to/your/dicom/files -o /path/to/your/output --split --log_error
```

options:
```
usage: main.py [-h] [-o OUTPUT_ROOT_DIR] [-e] [-s] [--no-split] [--log_debug]
               [--threads THREADS]
               dicom_root_dir

Convert DICOM sequences to NIfTI with mapping.

positional arguments:
  dicom_root_dir        Root directory containing DICOM files

options:
  -h, --help            show this help message and exit
  -o OUTPUT_ROOT_DIR, --output_root_dir OUTPUT_ROOT_DIR
                        Output directory for NIfTI files
  -e, --log_error       Log errors to error_log.csv
  -s, --split           Split 4D NIfTI files into 3D volumes
  --no-split            Explicitly disable splitting 4D NIfTI files
  --log_debug           Enable detailed debug logging to console
  --threads THREADS     Number of worker processes (default: all available)
```

## File an Issue

We highly encourage you to try `dcmsort2nii` on your own datasets! Real-world testing is invaluable for improving the tool.

Did you encounter a bug? Have an idea for a new feature or improvement? Did the tool struggle with your specific data structure or format? Please don't hesitate to **open an issue** on the GitHub repository! All feedback, positive or critical, is genuinely welcome and helps make `dcmsort2nii` better for everyone.

## Acknowledgments

This project builds upon the core functionality provided by the fantastic [dicom2nifti](https://github.com/icometrix/dicom2nifti) library. We are deeply grateful to its developers for their excellent work, which serves as the foundation for `dcmsort2nii`.
