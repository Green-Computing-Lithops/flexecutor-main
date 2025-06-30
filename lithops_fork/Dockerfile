FROM python:3.10-slim

# 1. Instalar herramientas de sistema necesarias
RUN apt-get update && apt-get install -y gcc unzip && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

# 2. Instalar TODAS las dependencias de Python BASADAS EN TU setup.py
#    y las que necesita tu función.
RUN pip install \
    Click \
    tabulate \
    six \
    PyYAML \
    pika \
    tqdm \
    tblib \
    requests \
    paramiko \
    cloudpickle \
    ps-mem \
    psutil \
    kubernetes \
    boto3 \
    numpy \
    pandas \
    flask  
    # Flask la añadiremos solo si vuelve a ser un problema.

# 3. Preparar el directorio de trabajo
WORKDIR /lithops

# 4. Copy the entire lithops source code
COPY lithops /lithops/lithops

# 5. Copy the entry point script
COPY lithops/serverless/backends/k8s/entry_point.py lithopsentry.py

# 6. Copy setup.py to working directory
COPY setup.py .

    # 7. Install lithops in development mode
    RUN pip install -e /lithops

# 7. Set PYTHONPATH and ensure lithops is importable
ENV PYTHONPATH=/lithops
ENV LITHOPS_HOME=/lithops

# 8. Set the proper entry point
CMD ["python", "lithopsentry.py"]
