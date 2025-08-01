# Python 3.10
FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get install -y \
      g++ \
      make \
      cmake \
      unzip \
     && rm -rf /var/lib/apt/lists/* \
    && apt-cache search linux-headers-generic

ARG FUNCTION_DIR="/function"

 
RUN mkdir -p ${FUNCTION_DIR}

 
RUN pip install --upgrade --ignore-installed pip wheel six setuptools \
    && pip install --upgrade --no-cache-dir --ignore-installed \
        awslambdaric \
        boto3 \
        redis \
        httplib2 \
        requests \
        numpy \
        scipy \
        pandas \
        pika \
        kafka-python \
        cloudpickle \
        ps-mem \
        tblib \
        psutil \
        awslambdaric \
        boto3 \
        redis \
        httplib2 \
        requests \
        numpy \
        scipy \
        pandas \
        scikit-learn \
        joblib \
        wrapt>=1.14.0 \
        smart-open>=6.0.0 \
        pika \
        kafka-python \
        cloudpickle \
        ps-mem \
        tblib \
        psutil

 
WORKDIR ${FUNCTION_DIR}


# copiar dependencias y poner todas en el mismo directorio 
COPY lithops_lambda.zip ${FUNCTION_DIR} 

RUN unzip lithops_lambda.zip \
    && rm lithops_lambda.zip \
    && mkdir handler \
    && touch handler/__init__.py \
    && mv entry_point.py handler/

 

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "handler.entry_point.lambda_handler" ]
