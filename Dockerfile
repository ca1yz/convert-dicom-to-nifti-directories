FROM python:3.10-slim

WORKDIR /app

# comment to use pypi.org
RUN python -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple --upgrade pip
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /app

RUN pip install --no-cache-dir -e .

ENTRYPOINT ["dcmsort2nii"]
