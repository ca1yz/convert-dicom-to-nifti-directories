FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./

# comment to use pypi.org
RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir -r requirements.txt

COPY ./dcmsort2nii /app/dcmsort2nii

ENTRYPOINT ["python", "dcmsort2nii/main.py"]
