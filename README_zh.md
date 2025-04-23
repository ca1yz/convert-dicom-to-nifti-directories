# Dcmsort2nii

## 简介

`dcmsort2nii` 是一个 Python 工具，旨在简化将大型、可能包含**嵌套目录**的 **DICOM** 文件转换为 **NIfTI** 格式的过程。它作为 `dicom2nifti` 的一个便捷封装，特别适用于批量处理医学影像数据集。主要功能包括自动**序列检测**（能够区分同一目录下的多个序列）、**并行转换**、可选的 **4D 文件分割**、生成**元数据映射文件**，以及通过 **Dockerfile** 实现的轻松部署。

### 输入/输出示例

请参阅此处的示例 notebook：[./example/example_notebook.ipynb](./example/example_notebook.ipynb)

## 安装

使用 `dcmsort2nii` 主要有两种方式：

### 1. Docker (推荐)

推荐使用 Docker，因为它封装了所有依赖项，确保在不同环境中都能一致地执行。

**a. 构建 Docker 镜像:**

导航到项目的根目录（包含 `Dockerfile` 的地方）并运行：

```bash
docker build -t dcmsort2nii:latest .
```

**b. 运行 Docker 容器:**

将 `INPUT_DIR` 和 `OUTPUT_DIR` 更改为您期望的路径。

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

**运行示例输出:**
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

### 2. Conda 安装

如果您不想使用 Docker，可以按照以下步骤安装：

**a. 克隆仓库:**

```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

**b. 创建虚拟环境并安装工具:**

```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -e .
```

**c. 运行工具:**

```bash
dcmsort2nii /path/to/your/dicom/files -o /path/to/your/output --split --log_error
```

**命令行选项:**
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

## 致谢

本项目的核心功能基于 [dicom2nifti](https://github.com/icometrix/dicom2nifti)。我们非常感谢其开发者的工作和贡献，他们的成果是本项目的基础。