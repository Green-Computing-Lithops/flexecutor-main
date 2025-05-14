# Flexecutor
A flexible and DAG-optimized executor over Lithops

*Documentation pending to be written*


# to check all instances: 
sudo docker ps -a

pip3 install -e . --break-system-packages

# check info docker status 
sudo docker run -d -p 9000:9000 -p 9001:9001 --name minio quay.io/minio/minio server /data --console-address ":9001"
sudo docker ps

# install minio 
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc && sudo mv mc /usr/local/bin/
