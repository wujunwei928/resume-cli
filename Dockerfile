# resume-cli 容器镜像：安装后以 resume-cli 为入口
FROM python:3.12-slim

WORKDIR /app

# 先拷贝元数据与源码再安装，利用层缓存
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .

# 示例数据便于容器内直接演示
COPY examples ./examples

ENTRYPOINT ["resume-cli"]
CMD ["--help"]
