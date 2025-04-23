[English](./README.md) | **中文**

---

# Dcmsort2nii

## 简介

处理医学影像数据时，一项常见的挑战是将大量、有时结构混乱的 DICOM 文件集合转换为许多分析流程所需的 NIfTI 格式。

`dcmsort2nii` 旨在减轻这一负担。它作为优秀的 `dicom2nifti` 库的一个封装，增加了旨在**简化**复杂数据集**批量处理**的**关键功能**。我们的目标是让繁琐的 DICOM 整理和转换变得更加简单快速：

*   **处理复杂目录结构**：只需指定根目录，即可自动遍历所有子目录结构。
*   **自动序列分组**：分析每个文件中的 DICOM 标头，自动识别并分组不同的成像序列，即使原始数据混杂存放。
*   **加速转换**：利用多个 CPU 核心进行并行处理，显著加快大型数据集的转换速度。
*   **关键元数据追踪**：生成详细的 `.parquet` 文件（并提供 `.csv` 作为备选），将每个输出的 NIfTI 文件映射回其原始 DICOM 序列的详细信息。
*   **灵活的 4D 处理**：可选择将 4D NIfTI 文件（常见于 fMRI 或 DWI）分割成单独的 3D 卷，这对于特定的分析或模型训练需求很有用。
*   **轻松部署**：Docker部署，但也可以在 conda 环境中通过 pip 安装。

### 输入/输出示例

请在此处查看实际操作示例：[./example/example_notebook.ipynb](./example/example_notebook.ipynb)

## 安装

首先克隆仓库。
```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

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
# 以下不变
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

Using default number of workers: 32 # 使用默认的工作进程数：32
Scanning directories and analyzing sequences... # 扫描目录并分析序列...
Scan complete. Found 9 leaf directories containing 31 sequences to process. # 扫描完成。发现 9 个叶目录，包含 31 个待处理序列。
Using temporary directory for sequence results: /data/output/dicom_seq_results_o5pk439z # 使用临时目录存放序列结果...
Submitting 31 sequence tasks to 32 workers... # 向 32 个工作进程提交 31 个序列任务...
Processing Sequences: 100%|██████████| 31/31 [00:09<00:00,  3.21it/s] # 处理序列进度
Aggregating results... # 汇总结果...
Found 26 temporary result files. # 找到 26 个临时结果文件。
Successfully aggregated 34 entries. # 成功汇总 34 个条目。
Removed temporary directory: /data/output/dicom_seq_results_o5pk439z # 已移除临时目录...
Final mapping saved to: /data/output/nifti_dicom_mapping.parquet # 最终映射文件保存至...
Error log saved to: /data/output/error_log.csv # 错误日志保存至...
```

### 2. Conda 安装

如果您不想使用 Docker，可以按照以下步骤安装：

**a. 创建虚拟环境并安装工具:**

```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -e .
```

**b. 运行工具:**

```bash
dcmsort2nii /path/to/your/dicom/files -o /path/to/your/output --split --log_error
```

**命令行选项:**
```
usage: main.py [-h] [-o OUTPUT_ROOT_DIR] [-e] [-s] [--no-split] [--log_debug]
               [--threads THREADS]
               dicom_root_dir

将 DICOM 序列转换为 NIfTI 并生成映射文件。

位置参数:
  dicom_root_dir        包含 DICOM 文件的根目录

选项:
  -h, --help            显示此帮助信息并退出
  -o OUTPUT_ROOT_DIR, --output_root_dir OUTPUT_ROOT_DIR
                        NIfTI 文件的输出目录
  -e, --log_error       将错误记录到 error_log.csv 文件
  -s, --split           将 4D NIfTI 文件分割成 3D 卷
  --no-split            明确禁用 4D NIfTI 文件分割
  --log_debug           在控制台启用详细的调试日志
  --threads THREADS     工作进程数量 (默认: 所有可用核心)
```

## 提交 Issue (问题反馈)

我们希望您在自己的数据集上尝试 `dcmsort2nii`！真实世界的数据测试对于改进这个工具来说很宝贵。

您是否遇到了 bug？对于新功能或改进有什么想法？这个工具在处理您特定的数据结构或格式时遇到了困难吗？在 GitHub 仓库上**提交一个 Issue**！无论是正面的还是批评性的反馈，都将帮助 `dcmsort2nii` 变得更好，惠及每一位用户。

## 致谢

本项目的核心功能基于出色的 [dicom2nifti](https://github.com/icometrix/dicom2nifti) 项目。我们对其开发者们的杰出工作深表感谢，他们的成果是 `dcmsort2nii` 的基石。