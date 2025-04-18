# Dcmsort2nii

## Introduction

`dcmsort2nii` is a Python tool that simplifies converting large, potentially **nested directories** of **DICOM** files into **NIfTI** format. It acts as a convenient wrapper around `dicom2nifti` for batch processing medical imaging datasets. Key features include automatic **sequence detection** (separating multiple sequences within one directory), **parallel conversion**, optional **4D splitting**, generation of a **metadata mapping file**, and easy deployment via **Dockerfile**.

### Example Input / Output 

Example notebook available [here](./example/example_notebook.ipynb)

## Installation

There are two primary ways to use `dcmsort2nii`:

### 1. Docker (Recommended)

Using Docker is the recommended method as it encapsulates all dependencies and ensures consistent execution across different environments.

**a. Build the Docker Image:**

Navigate to the project's root directory (where the `Dockerfile` is located) and run:

```bash
docker build -t dcmsort2nii:latest .
```

**b. Run the Docker Container:**

```bash
docker run --rm \
  -v /path/to/your/dicom/files:/data/input:ro \
  -v /path/to/your/output:/data/output \
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

**a. Clone the Repository:**

```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

**b. Install Dependencies:**

```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -r requirements.txt
```

**c. Run the Tool:**

```bash
python dcmsort2nii/main.py /path/to/your/dicom/files -o /path/to/your/output --split --log_error
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

