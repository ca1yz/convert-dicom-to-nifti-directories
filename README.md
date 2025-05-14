**English** | [中文](./README_zh.md)

---

# Dcmsort2nii

## Introduction

`dcmsort2nii` is a command-line tool built around `dicom2nifti` to simplify and accelerate the batch conversion of DICOM datasets into the NIfTI format. It automatically handles complex directory structures, groups sequences, and tracks metadata. See example usage in the [Jupyter Notebook](./example/example_notebook.ipynb).

## Installation and Usage

First, clone the repository:
```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

### Docker (Recommended)

Build the Docker image:
```bash
docker build -t dcmsort2nii:latest .
```

Run the conversion (replace `/path/to/your/dicom_root_dir` and `/path/to/your/output`):
```bash
docker run --rm \
  -v /path/to/your/dicom_root_dir:/data/input:ro \
  -v /path/to/your/output:/data/output \
  dcmsort2nii:latest \
  /data/input -o /data/output --split --log_error
```

### Conda

Setup a conda environment and install the tool:
```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -e .
```

Run the conversion (replace `/path/to/your/dicom/files` and `/path/to/your/output`):
```bash
dcmsort2nii /path/to/your/dicom/files -o /path/to/your/output
```

For more options, run `dcmsort2nii --help`.

## Credits

This project builds upon the core functionality provided by the fantastic [dicom2nifti](https://github.com/icometrix/dicom2nifti) library. We are deeply grateful to its developers for their excellent work, which serves as the foundation for `dcmsort2nii`.
