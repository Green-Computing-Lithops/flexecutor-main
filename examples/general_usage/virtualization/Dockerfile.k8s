FROM python:3.10-slim

# 1) Install all system tools in one RUN
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc \
      g++ \
      unzip \
      sudo \
      procps \
      curl \
      wget \
      git \
      build-essential \
 && (apt-get install -y bpfcc-tools python3-bpfcc || echo "BPF tools not available") \
 && (apt-get install -y linux-perf || echo "linux-perf not available") \
 && rm -rf /var/lib/apt/lists/*

# 2) Try to create perf symlink if available
RUN which perf && ln -sf $(which perf) /usr/local/bin/perf || echo "perf not available, energy monitoring will use CPU estimation"

# 3) Python dependencies - install in stages to better handle conflicts
RUN pip install --upgrade pip setuptools wheel

# Install basic dependencies first
RUN pip install \
      Click tabulate six PyYAML pika tqdm tblib \
      requests paramiko cloudpickle ps-mem psutil \
      kubernetes boto3 flask

# Install data science packages (these often have complex dependencies)
RUN pip install numpy pandas

# Install ML packages last
RUN pip install lightgbm scikit-learn

# Install additional packages needed for dataplug and titanic workflow
RUN pip install wrapt smart-open

# Install dataplug from git repository
RUN pip install git+https://github.com/CLOUDLAB-URV/dataplug

# 4) Create workspace
WORKDIR /app

# 5) Copy the modified Lithops library package
COPY lithops_fork/ /app/lithops_fork/

# 6) Install the modified Lithops library in development mode
RUN cd /app/lithops_fork && pip install -e .

# 7) Create the expected lithops directory structure for k8s backend
RUN mkdir -p /lithops

# 8) Copy the k8s entry point to the expected location-- REVIEW 
COPY lithops_fork/lithops/serverless/backends/k8s/entry_point.py /lithops/lithopsentry.py

# 9) Copy flexecutor application
COPY . /app/flexecutor/

# 10) Set working directory to flexecutor
WORKDIR /app/flexecutor

# 11) Make the entry point executable
RUN chmod +x /lithops/lithopsentry.py

# 12) Configure sudo for perf (if available)
RUN echo "root ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# 13) Create energy monitoring capability check script
RUN echo '#!/bin/bash\n\
echo "=== Energy Monitoring Capability Check ==="\n\
echo "Perf available: $(which perf >/dev/null && echo "YES" || echo "NO")"\n\
echo "RAPL accessible: $(test -r /sys/class/powercap/intel-rapl:0/energy_uj 2>/dev/null && echo "YES" || echo "NO")"\n\
echo "CPU estimation: YES (always available)"\n\
echo "========================================"\n\
' > /usr/local/bin/check-energy && chmod +x /usr/local/bin/check-energy

CMD ["python"]
