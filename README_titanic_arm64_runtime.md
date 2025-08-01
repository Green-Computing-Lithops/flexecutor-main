# Guía para crear Runtime AWS Lambda ARM64 para Titanic

## Resumen
Este documento proporciona los pasos necesarios para crear un runtime AWS Lambda ARM64 para el proyecto Titanic usando Lithops, basado en la conversación de `/home/bigrobbin/Desktop/green_computing/flexecutor-main/information/cline_task_AWS_summarized.md`.

## Prerrequisitos
1. Entorno virtual Python activado (venv310)
2. Credenciales AWS válidas y actualizadas
3. Docker instalado
4. Lithops configurado con archivo `config_aws.yaml`

## Archivos Creados

### 1. Dockerfile ARM64 para Titanic
**Ubicación:** `/home/bigrobbin/Desktop/green_computing/flexecutor-main/examples/titanic/Dockerfile.arm64`

```dockerfile
# AWS Lambda ARM64 Runtime for Titanic Project
# Note: For compatibility with current build environment, using x86_64 base
# In production ARM64 environment, change to: public.ecr.aws/lambda/python:3.10-arm64
FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies
RUN yum update -y \
    && yum install -y \
        gcc \
        gcc-c++ \
        make \
        cmake3 \
        unzip \
        vim \
        gfortran \
        blas-devel \
        lapack-devel \
        python3-devel \
    && yum clean all

# Define custom function directory
ARG FUNCTION_DIR="/function"

# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

# Install Python dependencies
RUN pip install --upgrade --ignore-installed pip wheel six setuptools \
    && pip install --upgrade --no-cache-dir --ignore-installed \
        awslambdaric \
        boto3 \
        redis \
        httplib2 \
        requests \
        numpy==1.24.3 \
        scipy==1.10.1 \
        pandas>=1.5.0 \
        scikit-learn>=1.3.0 \
        joblib>=1.2.0 \
        wrapt>=1.14.0 \
        smart-open>=6.0.0 \
        pika \
        kafka-python \
        cloudpickle \
        ps-mem \
        tblib \
        psutil

# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}

# Add Lithops
COPY lithops_lambda.zip ${FUNCTION_DIR}
RUN unzip lithops_lambda.zip \
    && rm lithops_lambda.zip \
    && mkdir handler \
    && touch handler/__init__.py \
    && mv entry_point.py handler/

# Set the entrypoint
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.entry_point.lambda_handler" ]
```

## Comandos para Construir el Runtime

### 1. Configurar el entorno
```bash
# Navegar al directorio del proyecto
cd /home/bigrobbin/Desktop/green_computing/flexecutor-main

# Activar entorno virtual
source venv310/bin/activate

# Configurar credenciales AWS (actualizar con credenciales válidas desde aws_credentials.md)
export AWS_ACCESS_KEY_ID="ASIA4MTWMECOLY4OJFIO"
export AWS_SECRET_ACCESS_KEY="o5hMTs5fCnRX1MtbV09oiJMG/FPAwtg+DlCtKZox"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEMD//////////wEaCXVzLWVhc3QtMSJHMEUCIQD5FrKODB8obY6PWfwsS396QYesPS1SnVcTziPXkNNBIQIgLw2t679vceHZKE4pnRcnzy/BGmOet4gfw/Y/nfk8ljIq/wII6P//////////ARAAGgw4NTE3MjU1MjUxNDgiDGvm6qCgZ9xPEypQZCrTAgVjxdYwLKyt4RgqsosAfKIQhUFCfUuUuguTEa0RsFMnAQlMdk9RaZDsoZUdpCt68m3WEEvzmTSfhmGmqbnru7N9vboY70dM+kCauNfONPAuejNYU/78jRc7lgt1RjAJON24qLkSxjuGvZQk1J374OHuNzgosVOL8KD9rufvqymGFDef/hlWvJlzZCCjbbGUS/t9pXMWSPZdQwjg1vkMhyTHqJsuHDimOShNXaEG63dfPc1EKr3fOmyhMUt6fTPNWM4FFsFA3gdb2EO5k92ZfmpNoimx0E7k194pv//rSae52VBHaeNDSCaPE9x64l+yt9ruO8E3j7I2C+3wdxct4Ah3IWseWk9xjdA9wj7NYlweCE+cY8DdHHwHuWD95L4D3WAr4z15r2yxHUdDBiA3L1+Qmge8aSYidTN+RR+9UP2HtDOs5I9PLSiMHHrYvUFyXClJaTD11LHEBjqnAX6QDPsbayfnL5eJdEQwLoAUHwO7DtwB9Uhn/8LmryJTBokkd/KOTpYDGbwG/R8nT9WHeUmCm2KbmPcE+H9boEx4qlGa3niVLsruepAcE9MrP9nDM/9aOpplZcfAweyo5wPnj7PBOYxCTRvV5YRSkdNSbADVYi395esX5tDjqLyPrmHO2XGrx7MKmbFsw3HDjGvGzB4/ivlAcI4QwlIvGOY7f40w1kq7"

# Configurar archivo de configuración Lithops
export LITHOPS_CONFIG_FILE=config_aws.yaml
```

### 2. Construir el runtime
```bash
# Opción 1: Usando lithops (recomendado)
LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/green_computing/flexecutor-main/config_aws.yaml lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm

# Opción 2: Comando adaptado del original
source venv310/bin/activate && export LITHOPS_CONFIG_FILE=config_aws.yaml && lithops runtime build -b aws_lambda -f examples/titanic/Dockerfile.arm64 titanic_aws_lambda_arm
```

### 3. Verificar construcción
```bash
# Verificar que el runtime se creó correctamente
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/green_computing/flexecutor-main/config_aws.yaml && echo "Environment variable set: $LITHOPS_CONFIG_FILE"
```

### 4. Probar el runtime
```bash
# Ejecutar el ejemplo de Titanic
source venv310/bin/activate && python examples/titanic/main.py
```

## Notas Importantes

### Credenciales AWS
- Las credenciales deben actualizarse desde `/home/bigrobbin/Desktop/green_computing/flexecutor-main/aws_credentials.md`
- Verificar que las credenciales no hayan expirado antes de construir
- Las credenciales incluyen: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN

### Diferencias del Dockerfile ARM64 vs x86_64
1. **Imagen base**: Usa `public.ecr.aws/lambda/python:3.10` para compatibilidad actual
   - Para verdadero ARM64: `public.ecr.aws/lambda/python:3.10-arm64`
2. **Gestor de paquetes**: Usa `yum` en lugar de `apt-get` (compatible con Amazon Linux)
3. **Dependencias específicas**: Incluye todas las dependencias de ML necesarias para Titanic

### Dependencias incluidas
- Todas las dependencias del Dockerfile original de Titanic
- Librerías ML específicas: scikit-learn, pandas, numpy, scipy
- Dependencias de sistema: gcc, cmake, gfortran, blas-devel, lapack-devel

### Problemas conocidos y soluciones
1. **Error de plataforma**: Se resuelve usando imagen base x86_64 compatible
2. **Credenciales expiradas**: Actualizar desde aws_credentials.md
3. **Conflicto de configuración**: Usar LITHOPS_CONFIG_FILE explícitamente
4. **Dependencias del sistema**: Usar yum en lugar de apt-get para Amazon Linux

## Comandos para uso en producción ARM64
```bash
# Para uso real en ARM64, modificar Dockerfile.arm64:
# FROM public.ecr.aws/lambda/python:3.10-arm64

# Y construir con plataforma específica:
docker buildx build --platform linux/arm64 -t titanic_aws_lambda_arm -f examples/titanic/Dockerfile.arm64 .
```
