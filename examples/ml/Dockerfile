# AWS Lambda x86_64 Runtime for ML Project
# Using proper x86_64 base image for AWS Lambda
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
        git \
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
        scikit-learn==1.2.2 \
        lightgbm>=4.0.0 \
        joblib>=1.2.0 \
        minio>=7.0.0 \
        kubernetes>=18.0.0 \
        wrapt>=1.14.0 \
        smart-open>=6.0.0 \
        pika \
        kafka-python \
        cloudpickle \
        ps-mem \
        tblib \
        psutil

# Install Lithops fork from local directory (Green Computing Lithops fork with additional features)
# Copy the lithops fork source code into the container
COPY lithops_fork/ /tmp/lithops_fork/
RUN cd /tmp/lithops_fork && pip install . && rm -rf /tmp/lithops_fork

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
ENTRYPOINT [ "/var/lang/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.entry_point.lambda_handler" ]
