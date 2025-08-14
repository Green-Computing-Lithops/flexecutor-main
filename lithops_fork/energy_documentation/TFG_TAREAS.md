
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# DISTRIBUCION DE LAS TAREAS TFG: 
* discord: https://discord.gg/y5Qe5dHt


## SEMANA 1 (07/02/2025): Viaje a tarragona
1. Instalar lithops y entender el funcionamiento
2. Presentacion de la idea Green computing
3. Diseno del modelo inicial

## SEMANA 2 (28/02/2025): 
1. Introducir valor aleatorio medicion de energia 
2. Dentro del handler, ver jobs alternativos

## SEMANA 3 (7/03/2025): 
1. Explorar alternativas de medicion de energia 
2. Valorar 

## SEMANA 4 (14/03/2025):

### ENERGIA:
1. Alternatively, you could use a different approach for measuring energy consumption that doesn't require sudo, such as using the RAPL interface directly through sysfs.
2. functions --> entornos que se pueda ejecutar perf o no + rapl
    - Esquema de procesadores : conocer procesador & ver si se puede ejecutar perf
    - Condicional para establecer metodo de calculo lithops directamente
        * De momento hacemos comparativa de todos los metodos: TDP / RAPL / PERF
3. Testear con algunos ejemplos de aplicaciones lithops: 
    - https://github.com/lithops-cloud/applications/blob/master/montecarlo/pi_estimation/pi_estimation.ipynb
    - https://github.com/lithops-cloud/applications/blob/master/mandelbrot/example_mandelbrot.ipynb




## SEMANA 5 (21/03/2025): 

### PARALELISMO: 
1. medir que paralelismo se ejecuta con menos energia 
    - kpi : optimizacion kpi estimator --> optimizar para energia en local 

2. Extraccion de multiples datos para ver que paralelismo da menos consumo energetico 
    - plot graph ( x niveles paralelismo y energy consumption)

3. Diseno y analisis de los datos de energia para diferentes niveles de paralelismo --> crear problema optimizable 
- x paralelismo:  map_instances 
- y energia:  ver que paralelismo menos energia da 

4. Obtener datos (evitar dependencia de entorno de ejecucion):  
    * pi estimation
    * airbnb 
    * paralel mandelbrot 
    * stock prediction


### ELEMENTOS A INTEGRAR 
- perf: media vs suma 
- detectar rapl con lithops
- Separar codigo energia del handler 
 

### DATABASE TDP: (agg energia Crear base de datos : Firebase + Scraper + N8N diario --> calculos directas ) 
* fuentes de datos de tdp maquinas de computacion mas comunes
* maquina EC2: uso cpu +  funcion --> maquinas de instancias virtuales : 
* Github: Extraer procesadores  
* Postgres: generar base de datos 
    - Generar API:
    - Valores null 
    -  


### LISTA DE IDEAS: 
1. Diferencia energia de lithops vs nativo  1 processor--> plot  
2. guardar la energia: decir en que maquina es mas eficiente ejecutar metabolomica 



## SEMANA 6 (28/03/2025):  fiesta major => Manri se complica 



## SEMANA 7: viernes 4 no reunion 



# reunion: 
virtualizaciones sobre maquinas --> caso de que tiene no tienes acceso a rapl
* no RAPL

baremetal: rapl --> nadie mas ejecutando el servidor 
* worker vs funcion: 
worker: unidad logica que te permite ejecurar una funcion dentro 

worker puede pasar que todas las funciones se estan ejecutando 
4 maquinas virtuales --> 4 worker --> 100 funciones --> cada una de las 25 funciones 
TDP --> energia de todo el host / no de la funcion completa 
* formula computo total y dividir por numero de funciones que tiene el worker 
* consumo energia funcion de pipeline --> 
* practica valores agregados --> llamada de workers paralelos --


PASO POSTERIOR:
optimizar por pipelines 
por detras: algoritmo de normalizacion de datos comparativa ejecuciones pasadas 

comparar : algoritmo de normalizacion en base de lo que ha pasado anterior 

## SEMANA 8: SALTO / vas atrasado / recuperar 
* finalizar valores para todas las ejecutiones --> prioritario --> directamente ejecucion 
* script cleaning diferentes 
* incluir varias mediciones de energia 
* extras: powerapi / detector de cpu / ver ejecucion / tdp database 
* empezar a escribir 




# MANRI : 
1. Minio: plataforma de objet storage de codigo abierto --> docker --> hacer pruebas 
    * ejecutar deployment de minio en local con docker --> chagpt en un unico comando 
    * flexecutor --> ejecutar 
2. flexecutor: plataforma jolteon --> adaptar / plataforma estructurada donde queda mas facil llevar a cabo operaciones 
    - profiling: pi_montecarlo --> directiva que permite lanzar pipeline de ejecucion con diferentes configuraciones 
    - output guarda ejecucion de tiempo de ejecucion : 
    - Trainign que permite tomar estos profiling --> entrenar modelos predictivos que nos pueden recomendar las mejora de los tiempos futuros --> predicting 
    - Accesso manri : finales de verano / algun bug --> ajustes --> preguntar 

3. Predicting: que ejecucion tiene el menor coste, introducir la menor parte de la energia 
* deployment de minio --> lanzar en local los casos de uso 
- link con todos los datos para poder lanzar los pipelines 

mini: ejemplos -- dag_execurion 
dag_profiling.py : importante --> lo mas encapsulada posible stages de computacione y ejecutan todas un mismo codigo 


con flexecutor: tener el ciclo cerrado que sea end to end 
* sintaxis de 
despues de ejecucion de profiling --> tiempo y ejecuciones 
* cuando tengamos eso vemos como optimizar --> tener ahi la energia 
* discriminador para cual optimizar cada approach ? 
flexecutor: TDP / rapl --> cuando escriba las diferentes metricas escriba tambien las metricas de energia 
flexecutor: ofrecer de manera clara smart provisioning que lithops no ofrece
lithops ofrece las capacidades , pero sin la nocion de optimizacion 
libreria
* aportar las directrivas de optimizacion
* optimizar los resultados de optimizacion 
cuando ejecutamos --> nos explica como funciona cada uno para 

iteraciones que cada una hace diferencte --> explicar jolteon 
tiempo / energia / 
def optimize(self): --> optimiza el pipeline con todos los predict que tiene y coge las opciones que mas te favorece 


punto clave esta semans 
dag_profiling : 
hito bastante guay y hacer la optimizacion real -> cloud -> cargas interesantes -> opciones reales 


# conexion para hacer el end to end 
en funcion de los resultados que existen 
* todos los papers de jolteon los optimicemos por energia --> ml / nl / video 
* listos para lanzar 

TFG 
jolteon : 
reiterar sobre algo existente 

tfm: 
pensar despues para tener un valor nuevo --> las piensas cuando ya tienes un resultado 
con iterar con un algorimo nuevo --> tfm 

32 paginas : experiencia no copypaste 
no pages 
secciones con hablar con ciertos elementos 
tfg documento --> claro
super conciso --> primer nivel 12 paginas de maximo nivel --> 
estructura tfg resultadista --> anexo lo que sea 

minimo integracion flexecutor y caso optimizacion maximo 

preguntar jolteon : 

mas facil introducirse si esta poco explotado 
estas cargando con trabajo de manri y german --> no les hagas perder el tiempo 

# 
german: muy importante ejecutar y recopilar no el que 
# plotmap

manri sufi 
varios nodos de distribucion y han cargado los nodos --> experimentos y no funcionan 
# Tareas pendientes
grafo funcionalidad --> diagrama de flujo --> chatgpt / draw.io



# Manri 07/03/2023: 
valores base y heuristica --> estimacion de energia --> links german 
TDP= procesador 65w
porcentaje de uso de cada aplicacion --> primer aproach 

version naive : consultar basicamente 

scrapping a una api -> consumo energia base 
hardcoding --> cambiar por necesario 


# STEPS to follow: 
1. Obtener la energia
    - version basica con tdp --> funcionando 
    - perf: te falta como guardar la informacion 
    - PowerApi: intentamos hasta las 9 --> sino pedimos ayuda
    - Ver como funciona Powerapi y ver alternativas

2. Predictor de carga 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Debbugger
## solved: 
 .vscode/launch.json

 {
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python no justMyCode",
      "type": "debugpy",
      "request": "launch",
      "purpose": ["debug-test"],
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}

ctrl + , --> justMyCode --> unselect all 


# run your own model without 
/home/bigrobbin/Desktop/git/lithops_fork/venv/bin/python flexecutor-main/examples/energy_comparison.py

# elementos de la reunion 
comando minio --> contenedor docker object storage != file storage --> almacenamiento object storage 
minio --> subir informacion ahi ( importante para replicar en el futuro --> object storage / no lithops storage --> S3 )
lithops --> bucket localhost / almacenamiento minio --> credenciales docker --> Map a storage ahi 


 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# minio
docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -v /home/bigrobbin/Desktop/git/lithops_fork/test-bucket:/data/test-bucket -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"


sudo docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -v /home/bigrobbin/Desktop/git/lithops_fork/test-bucket:/data/test-bucket -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"

sudo docker run -d -p 9000:9000 -p 9001:9001 --name minio quay.io/minio/minio server /data --console-address ":9001"


sudo docker run -d --name minio-server -p 9000:9000 -p 9001:9001 -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" quay.io/minio/minio server /data --console-address ":9001"

# servidor web --> 9001 / api rest 9000 : forwarding de dos puertos --> puerto sw vs api rest  

curl -O https://dl.min.io/client/mc/release/linux-amd64/mc

(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ chmod +x mc
(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ ./mc alias set myminio http://localhost:9000 minioadmin minioadmin
mc: Configuration written to `/home/bigrobbin/.mc/config.json`. Please update your access credentials.
mc: Successfully created `/home/bigrobbin/.mc/share`.
mc: Initialized share uploads `/home/bigrobbin/.mc/share/uploads.json` file.
mc: Initialized share downloads `/home/bigrobbin/.mc/share/downloads.json` file.
Added `myminio` successfully.
(venv) bigrobbin@bigrobbin:~/Desktop/git/lithops_fork$ ./mc mb myminio/test-bucket

 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# paralelismo

Now I understand how the profiling data is stored. The get_my_exec_path() function returns the path where the flexorchestrator script is located, which is set by the @flexorchestrator() decorator. This path is used as the base path for storing the profiling data.

In the main.py file, the @flexorchestrator(bucket="test-bucket") decorator is used, which sets the base path to the directory where main.py is located, which is flexecutor-main/examples/video.

So the profiling data should be stored in:
flexecutor-main/examples/video/profiling/video/stage0.json
flexecutor-main/examples/video/profiling/video/stage1.json
flexecutor-main/examples/video/profiling/video/stage2.json
flexecutor-main/examples/video/profiling/video/stage3.json



# elements to solve the error 
        //     "(cpu 1, mem, worker 2)": { 
        //     "(cpu 4, mem, worker 4)": {
        //     "(cpu 8, mem, worker 8)": {
        //     "(cpu 8, mem, worker 16)": { --> principalmete workers



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Structure of the project 

1. **Lithops** – my serverless compute framework.  
2. **MinIO** – S3-compatible object storage used as the communication bus between functions.  
3. **Flexecutor** – a Python wrapper around Lithops that aggregates execution metadata (logs, perf stats, outputs) into a single report.

 


 





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# LITHOPS 
# install lithops backend: 

docker pull lithopscloud/ibmcf-python-v312


net stop LxssManager
net start LxssManager
wsl --update

## Entorno virtual

### configuracion entorno virtual
python -m venv venv
python3 -m venv venv

### Activate: 
venv\Scripts\activate // for mac
venv\Scripts\Activate.ps1 // for windows
source venv/bin/activate 
source .venv/bin/activate 
source lithops-venv/bin/activate 

### deactivate / finalize sesion: 
deactivate

### comprobacion elementos de entorno virtual
python --version
pip list
pip install -r requirements.txt // not allways necessary
pip install setup.py

### install lithops: 
<!-- pip install lithops -->

### Install the Package in Editable Mode
venv/bin/python -m pip install -e . 
pip install -e .

### una vez instalado el v env 
pip install -e ".[all]" --break-system-packages
pip install -e ".[all]" 


# lithops config file 
# lithops yaml
https://github.com/lithops-cloud/lithops/blob/master/config/config_template.yaml

# where configuration lithops is : 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config   #/path/to/your/config

# LITHOPS_CONFIG_FILE system environment variable:
export LITHOPS_CONFIG_FILE='/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config'
unset LITHOPS_CONFIG_FILE

echo $LITHOPS_CONFIG_FILE
ls ~/.lithops/config ./.lithops_config /etc/lithops/config


nano ~/.lithops/config

# command:  
python -c "import lithops; print(lithops.__file__)"


# inside the venv 
pip install --force-reinstall lithops



# see where lithops is 
C:\Users\Usuario\Desktop\lithops\lithops\__init__.py
pip uninstall lithops -y
rmdir /s /q C:\Users\Usuario\Desktop\lithops\lithops

# all unified: 
source lithops-venv/bin/activate 
export LITHOPS_CONFIG_FILE='/home/bigrobbin/Desktop/TFG/lithops_fork/lithops_config'
docker start minio
 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FLEXECUTOR
### sources in flexecutor: 
python3 -m venv venv-flexecutor

### Activate: 
source venv-flexecutor/bin/activate 

### install lithops in flexecutor: 
pip install --upgrade pip
pip install -e ../lithops_fork/
pip install -e . --break-system-packages

pip install -e /home/bigrobbin/Desktop/TFG/lithops_fork 

### LITHOPS_CONFIG: inside venv-flexecutor
python -c "import lithops; print(lithops.__file__)"

### where configuration lithops is : 

# LITHOPS_CONFIG_FILE system environment variable FLEXECUTOR:
* /path/to/your/config
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml   

* to usset 
unset LITHOPS_CONFIG_FILE

echo $LITHOPS_CONFIG_FILE
ls ~/.lithops/config ./.lithops_config /etc/lithops/config


nano ~/.lithops/config

# command:  
python -c "import lithops; print(lithops.__file__)"

### MinIO:
docker start minio


# all unified: 
source venv-flexecutor/bin/activate 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml  
docker start minio
 


 
# REPASO GENERAL: 
1. variables de entorno
2. Activar
3. instalar dependencias flexecutor
4. desinstalar lithops 
5. instalar lithops especifico con -e 
6. mostrar la ruta de configuracion al fichero lithops
7. configurar minio
8. subir datos a minio -> mismo bucket 
9. evitar dependencias minio: 
10. (MANRI): errores de elementos 
- comentar valores json 
- error 9
- diferencias energia 
- Error: parametro de un map iterdata , array maximo : idealmente 

# pasar directamente storage bucket : word counter directamente un fichero en object storage directamente ahi 
https://lithops-cloud.github.io/docs/source/data_processing.html
https://lithops-cloud.github.io/docs/source/data_partitioning.html
Processing data from the Cloud — Lithops  documentation
 



# manri error 9 : error 1= cuando finalizan bien 
lithops logs poll
R
comentar con manri: 
==== ENERGY MONITOR INITIALIZED FOR PROCESS 9 ====
2025-05-13 18:08:43,341 [INFO] handler.py:224 -- Reading stats file before execution: /tmp/lithops-bigrobbin/storage/lithops.jobs/aaf05f-0-M000/00000/job_stats.txt
 



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# minio 
# poner los datos en minio: 
test-bucket/
└── training-data/          (empty “folder”)
    └── training-data/
        └── train_pca_transform.txt

1) nuke the entire training-data prefix in one go:
mc rm --recursive --force myminio/test-bucket/training-data

2) Re‐upload only the contents of your local training-data folder 
mc cp -r /home/bigrobbin/Desktop/TFG/flexecutor-main/test-bucket/training-data myminio/test-bucket/training-data

2.1)
mc cp -r /home/bigrobbin/Desktop/TFG/flexecutor-main/test-bucket/training-data myminio/test-bucket/


3) Verify
mc ls myminio/test-bucket/training-data
4) Rerun your pipeline


ver si servidor minio esta accesible: 
telnet 192.168.1.168 9000

# minio 
6. put all elements:
mc cp -r /home/bigrobbin/Desktop/REPASO/flexecutor/test-bucket/ myminio/test-bucket/
7. recordar configuracion en vez de localhost la propia de minio 
8. export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml  --> mejor que config normal 
- comandos 
 
source venv-flexecutor/bin/activate 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml
docker start minio

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# DOCKER
## Install wsl
https://docs.microsoft.com/es-es/windows/wsl/install-win10

## install docker
https://docs.docker.com/docker-for-windows/install/

* verify docker is installed
* verify the path to docker is in the environment variables


## instalar docker imagen de lithops
docker pull lithopscloud/ibmcf-python-v312
docker images
docker run -it lithopscloud/ibmcf-python-v312 python --version

 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Problemas: 
## no module pika installed as well as all requierements and libraries
* only when i intall lithops in local and execute the examples in the virtual machine it works 
* seems that the file should be installed in the venv python but also in the system
* in the folder: C:\Users\Usuario\AppData\Local\Temp\lithops-root there where errors bc the both enviroments are using the same folder 


```bash
$env:LITHOPS_DEBUG = "True"
lithops hello
```
 

## to run the examples:

* have complete and funtional commits in your local git repository
* create a new branch
* push the branch to the remote repository
* create a new cloud function
* push the cloud function to the remote repository
* create a new job
* push the job to the remote repository
* run the job
* validate before update 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# elements to execution enviroments 
lithops logs poll

# test in local: 
https://github.com/lithops-cloud/lithops/blob/master/docs/source/compute_config/localhost.md 
lithops hello -b localhost -s localhost

# see the logs : 
lithops logs poll



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 
GERMAN REVISIONES: 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ sudo groupadd docker
groupadd: group 'docker' already exists
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ sudo usermod -aG docker $USER
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ newgrp docker
bigrobbin@bigrobbin:~/Desktop/TFG$ docker run  hello-world

german: 
usuario no permisos sobre docker --> bigrrobin 

diferentes entornos con configuraciones 
imagen --> definir el container con una imagen especifica


runtime: docker.io/lithopscloud/ibmcf-python-v312 # imagen publica en docker: 
* permisos especiales por default --> usuario normal no tiene permisos 
* anadir usuario al grupo de docker 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker ps
permission denied while trying to connect to the Docker daemon socket at 


unix:///var/run/docker.sock: Get "http://%2Fvar%2Frun%2Fdocker.sock/v1.45/containers/json": dial unix /var/run/docker.sock: connect: permission denied

framework programacion 
por debajo container 
no podias correr containers de locker 

hello world de docker --> 
primero a gestionar c group de docker 
https://stackoverflow.com/questions/48957195/how-to-fix-docker-permission-denied



 docker ps -a

 
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker rm minio
Error response from daemon: No such container: minio
(venv) bigrobbin@bigrobbin:~/Desktop/TFG$ docker rm /minio-server


 
    
time sleep_pro 
forzar cpu loggaritmo --> replantear funcion 
chunck --> dividir en 2 
que la funcion que haga 
1000 ciclos
2 500 ciclos 
4 250 ciclos 

weak scaling 
automatizar sobre ese codigo --> cambiar para que sea 
consumo de energia segun paralelismo 
minio y runtimes 
automatizas + plot 



# GERMAN eror docker tipico : 
error docker --> clasico permisos
lithops logs poll

docker ps -a
* no puedes usar sudo pq en las maquinas virtuales y funciones no permite
* eliminar imagenes no necesarios: docker rm /minio-server

# POC
* word count: 
    - 1 lee 
    - 2 archivo la mitad 

# web interface / rest api 

 


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





prompt : I want a detailed guide and process of how to run this file: main_german.py
 
i am having some problems for the execution of a simple example using lithops with minio. The file is 

1) venv and installed lithops from my fork folder using: 
source venv-flexecutor/bin/activate 
pip install -e ../lithops_fork/


2) set the configuration to this file: 
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/TFG/flexecutor-main/config_template.yaml   

3) minio storage / runtime selected and iniciated
docker start minio

To check the logs is useful the command :  lithops logs poll




## after meeting: 

Flexecutor acts as a wrapper of lithops: 
i want to store the energy measures imported by lithops in this folder
examples/ml/profiling/machine_learning 
1) if i delete the json inside the folder i obtain errors, why is that? is correct? whould not be useful if the json are generated in each execution.

2) after run examples/ml/main.py  is always needed to run  minio_cleanup.py to do not have elements inside minio to dificult the execution. 

3) how i can store the measures of energy in examples/ml/profiling/machine_learning  after running examples/ml/main.py ?  



# 
# Flexecutor
A flexible and DAG-optimized executor over Lithops

*Documentation pending to be written*


# ERRORES: 
1. circular imports 
2. dependencias flexecutor / diferentes carpetas
3. flexecutor : cd /home/bigrobbin/Desktop/REPASO/flexecutor && /home/bigrobbin/Desktop/REPASO/flexecutor/venv-flexecutor/bin/python -m pip install -e .
4. dataplug & cloud objets: /home/bigrobbin/Desktop/REPASO/flexecutor/venv-flexecutor/bin/python -m pip install dataplug

5. PYTHONPATH=. python3 examples/mini/dag_profiling.py



# prompt inicial : 

Explícame detalladamente los siguientes pasos para ejecutar flexecutor un entorno de pruebas:

1. He instalado MinIO en un entorno local y va a actuar como object storage
2. Tiene un bucket llamado "test-bucket" donde almacenaré archivos de prueba.

3. quiero que experimentes con ejecuciones varios ejemplos ubicados en examples/{ml|video}.

4. En los scripts de los casos de uso (examples/ml/main.py y examples/video/main.py), específicamente en la variable FlexData.prefix, encontraré las rutas donde debo subir los archivos de entrada para las diferentes aplicaciones.

5. El objetivo final es ejecutar diferentes configuraciones utilizando la operación DAGExecutor.profile y recopilar métricas de cada configuración.

Por favor, proporciona instrucciones paso a paso sobre:
 
- Cómo ejecutar DAGExecutor.profile con diferentes configuraciones (examples/ml/main.py y examples/video/main.py)
- Cómo recopilar y analizar los datos de consumo energético


IMPORTANTE: 
- centrate en la estructura existente y en entender como funciona, no crees archivos nuevos si no es absolutamente necesario 

Incluye ejemplos de comandos específicos que debería ejecutar en cada paso.


# error retorno 
código de retorno -9, lo que generalmente indica que el proceso fue terminado por una señal SIGKILL


lithops:
    backend: localhost 
    storage: minio  

 


minio:
    # storage_bucket: lithops-test
    storage_bucket: test-bucket
    endpoint: http://192.168.1.168:9000 # dentro de docker s3 / minio: self deployed accesible desde ambos entornos : 172.17.0.1 --> r
    access_key_id: minioadmin
    secret_access_key: minioadmin
<!-- # 
# (venv-flexecutor) bigrobbin@bigrobbin:~/Desktop/TFG/flexecutor-main$ telnet 172.17.0.1 9000
# Trying 172.17.0.1...
# Connected to 172.17.0.1.
# Escape character is '^]'.

# sudo entorno de docker --> $  -->




docker start minio
source venv-flexecutor/bin/activate
export LITHOPS_CONFIG_FILE=/home/bigrobbin/Desktop/REPASO/flexecutor/config.yaml


Vale entiendo lo que me propones pero hay areas de mejora: 
1. tras la ejecucion de examples/ml/main_profile.py se ha quedado estancado. 
- 2025-05-16 00:08:02,254 [INFO] invokers.py:225 -- ExecutorID 6d6aec-0 | JobID M004 - View execution logs at /tmp/lithops-bigrobbin/logs/6d6aec-0-M004.log
2025-05-16 00:08:02,254 [INFO] wait.py:101 -- ExecutorID 6d6aec-0 - Waiting for 1 function activations to complete

2. Me puedes explicar paso a paso como y por que se generan los  archivos json generados examples/ml/profiling/machine_learning , 
3. Ademas explicame el comportamiento de las diferentes fases y el orden entre ellas: 
- executor.train() 
- executor.predict(config)
- executor.optimize()

asi como generan : 
- examples/*/images/
- examples/*/profiling/
- examples/*/profiling/mocks
- examples/*/models/













# manri : 
* 65 tdp --> worker? 
 dentro de los lambda
  + diccionario :  

prompt : 

what i want is to store in the json file the following information: 
from : 
  "cpu_usage": [
    {
      "cpu_id": 0,
      "cpu_percent": 4.0,
      "timestamp": 1747414204.524089 
To 
  "cpu_usage": [
    {
      "cpu_id": 0,
      "cpu_percent": 4.0,
      "start_timestamp": 1747414204.524089 
      "end_timestamp": 18147414204.524089 






prompt: 

I need help into architectural design, could you sumarize  all the files that are used from lithops since the execution. 
i mean with a brief description 

first one secuential sumary 

general_test_map_reduce.py  > lithops/executors.py  >  ... > handler.py > energymanager > energy monitor

And then i want a bit of explanation of the project where you briefly explain wich desing pattern is being used and how critical is its performance in the thread workers


# PROMPT 2: 

Act as a Architectural software engieneer and analyze the architecture of my Lithops-based project. Please provide:

1. A sequential summary of all files involved in the execution flow, starting from general_test_map_reduce.py through to the energy monitoring components. For each file, provide a brief description of its purpose and role in the execution pipeline.
 

2. An architectural analysis that identifies each file for:
   - its main purpose
   - The key design patterns being used in the project
   - How these patterns affect the performance of thread workers and all flow
   - Critical performance considerations in the execution flow
   - The relationship between the core execution components and the energy management system
   - Add important information to present to the project 


# con ese promt --> disenas flujo de trabajo lithops + tfg 

pregunta como diseno de patrones como integrar energia de forma escalable sin alterar handler.py  
como crear una pequena interfaz o elemento que incluya diversos elementos de electricidad 



Act as a Architectural software engieneer you are in charge to  introduced the energy elements into an existing framework call lithops  but: 
- I want to have  nice patterns included 
- An option to don't use the energy module with energy = False
- I need to be able to implement new energy measurements tools, now are only 2 but in the future could be 10, so maintain an easy inclusion of each energy element
so keep that in mind to suggest how to design the project 



PROMPT ARCHITECTURE: 


Aswer deep searh: 
Act as an Architectural Software Engineer tasked with integrating energy monitoring capabilities into the Lithops framework. Design a modular energy monitoring system with the following requirements:

1. Recommend appropriate design patterns for seamlessly integrating energy monitoring into Lithops without disrupting its core functionality. Consider patterns like:
   - Factory Method or Abstract Factory for creating energy measurement tools
   - Strategy Pattern for different energy measurement implementations
   - Observer Pattern for monitoring energy events
   - Decorator Pattern for optionally adding energy monitoring
   - Any other patterns you believe would create a clean, maintainable architecture

2. Include a mechanism to completely disable energy monitoring with a simple "energy=False" parameter, ensuring:
   - Zero performance impact when disabled
   - No code changes required to toggle this feature
   - Clean handling of all related components when disabled

3. Design for extensibility to accommodate future energy measurement tools:
   - Currently supporting perf and eBPF as the two measurement tools
   - Must scale to support 10+ tools in the future
   - Allow for easy registration of new measurement tools without modifying core code
   - Maintain consistent interfaces across all measurement implementations

4. Ensure equal compatibility across all Lithops backend types:
   - Serverless backends
   - Standalone backends
   - Localhost backends

Please provide:
- A high-level architectural diagram represented both:
  * Visually (generated diagram)
  * As detailed text with hierarchies and relationships clearly indicated
- Interface definitions for the key components
- Explanation of how the selected design patterns fulfill the requirements
- Implementation considerations for ensuring performance is not significantly impacted
- Code examples for critical integration points

Consider how your design will interact with Lithops' existing components, particularly the execution flow from executors.py through handler.py.