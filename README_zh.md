[English](./README.md) | **中文**

---

# Dcmsort2nii

## 简介

`dcmsort2nii` 是一个基于 `dicom2nifti` 的命令行工具，旨在简化和加速 DICOM 数据集的批量转换过程，将其转换为 NIfTI 格式。它可以自动处理复杂的目录结构、对序列进行分组并追踪元数据。查看使用示例[Jupyter Notebook](./example/example_notebook.ipynb).

## 安装与使用

首先，克隆仓库：
```bash
git clone https://github.com/ca1yz/dcmsort2nii.git
cd dcmsort2nii
```

### Docker (推荐)

构建 Docker 镜像：
```bash
docker build -t dcmsort2nii:latest .
```

运行转换（请替换 `/path/to/your/dicom_root_dir` 和 `/path/to/your/output` 为您的实际路径）：
```bash
docker run --rm \
  -v /path/to/your/dicom_root_dir:/data/input:ro \
  -v /path/to/your/output:/data/output \
  dcmsort2nii:latest \
  /data/input -o /data/output --split --log_error
```

### Conda

设置 Conda 环境并安装工具：
```bash
conda create -n dcmsort2nii python=3.11 -y
conda activate dcmsort2nii
pip install --no-cache-dir -e .
```

运行转换（请替换 `/path/to/your/dicom/files` 和 `/path/to/your/output` 为您的实际路径）：
```bash
dcmsort2nii /path/to/your/dicom/files -o /path/to/your/output
```

更多选项请运行 `dcmsort2nii --help`。

## 致谢

本项目的核心功能基于出色的 [dicom2nifti](https://github.com/icometrix/dicom2nifti) 项目。我们对其开发者们的杰出工作深表感谢，他们的成果是 `dcmsort2nii` 的基石。