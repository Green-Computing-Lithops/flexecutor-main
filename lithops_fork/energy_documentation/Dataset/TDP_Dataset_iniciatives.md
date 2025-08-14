# ARTICULOS DE INTERES: 

* AWS services migrando a AMD: https://d1.awsstatic.com/events/Summits/nycsummit2023/PRT208-S_AMD_CostOptimizedScaling_E1_20230712_HCEdited.pdf

* base de datos CPU: 
    - https://www.cpu-world.com/CPUs/Xeon/Intel-Xeon%208275CL.html
    - https://www.cpu-world.com/CPUs/SoC.html

* https://ionutbalosin.com/2023/07/analyzing-jvm-energy-consumption-for-jdk-17-an-empirical-study/#:~:text=DRAM%20domain%2C%20utilizing%20diverse%20systems,precision%20compared%20to%20earlier%20generations

* ya han hablado de crear un dataset: https://www.apiscene.io/sustainability/building-an-aws-ec2-carbon-emissions-dataset/
    - On modern Intel CPUs, we have access to RAPL, Running Average Power Limit, an interface that gives access to a set of counters, giving energy and power consumption information. Using Turbostat, a tool by Intel, we can get the CPU TDP (Thermal Design Power). According to Intel, it refers to the power consumption under the maximum theoretical load. So it’s supposed to be the maximum sustainable power consumption for the CPU. This is especially useful because, on AWS, we use custom-made CPUs, which means that even if we can get the CPU model using a simple LS CPU comment on the terminal, we will never find any public information about this CPU model online. But most importantly, the tool gives us access to the CPU’s power consumption and the machine’s memory.
    - Turbostat, a tool by Intel, we can get the CPU TDP (Thermal Design Power).
    - https://medium.com/teads-engineering/building-an-aws-ec2-carbon-emissions-dataset-3f0fd76c98ac

* ha montado una base de datos: https://doc.api.boavizta.org/getting_started/cpu_component/ & https://docs.google.com/spreadsheets/d/1DqYgQnEDLQVQm5acMAhLgHLD8xXCG9BIrk-_Nv6jF3k/edit?gid=224728652#gid=224728652
* estimator:  https://medium.com/@benjamin.davy
    - IDEA: You need to identify make and model of as much of the hardware as you can. Things that consume electricity such as the CPU, chipset/motherboard, and the power supply unit (or its equivalent). I presume you are talking about EC2. If you log into a Linux EC2, try the command "lshw." It will list hardware info. Also, search for "linux list hardward" for more commands. Then the manufacturer of each subcomponent should have datasheets that detail the power requirements of its products

* https://sustainability.aboutamazon.com/products-services/aws-cloud
* https://medium.com/teads-engineering/evaluating-the-carbon-footprint-of-a-software-platform-hosted-in-the-cloud-e716e14e060c


# SCRAPPING HASTA LA GENERACION 14: 
https://github.com/toUpperCase78/intel-processors
