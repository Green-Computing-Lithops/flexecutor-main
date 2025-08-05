verificar lambda rapl 
- no solo titulo 
- ebpf --> 

tamano de memoria --> mejors significativa 2048 / 1024 media cpu 
* diferentes tamanos de cpu 
- 512
- 1024
- 2048 ( limite, a partir de aqui no va a ir mejor )


tdp psultis  si no se puede : approach suficiente --> mira rapl 


# dimensiones a analizar : 
memoria 
workers 
arm / x86 
aplicaciones: 
, titanic ( monostage )
, pi_estimation (modificado / similar a titanic ) --> 
, video  ( stages diferentes)
, ml ( stages diferentes )

# medidas 
coste temporal 
coste energetico 
coste economico --> derivar de los tiempos de ejecucion  --> aws cobra por el tiempo --> diferente para x86 y arm tiempo x workers x conversion 
- 4.c --> 

* muchas configuraciones --> nos quedamos con la mejor de ellas 
* menos sofisticado que encontrar la tendencia de curva 



lanzar pocas configuraciones en la escala de valores disponibles 
- inferir la escala de costes 
- 

32 hojas si esta bien escrito es suficiente 
25 / 50 / 150 : coherente 
- meter varios puntos de energi 
- facil lectura 
- informativo 
- anada valor 
- entendimiento facil del trabajo 
- ingles: hazlo ingles 



intro 2 - 3 : problema y resolucion + resultados ( resumen)
subseccion : objetivos tfg --> rapido de conseguir que quieres hacer 

contexto 
    info lithops 
    info flexecutor  : wrapper + facilidad ( smart provisioning) --> no tan en detalle pq era para provisioning + facilidad de comun 
    arquitecturas procesador : x86 vs arm (energia )
    energia: 
        perf / psutil / rapl / ebpf --> 1 o 2 hojas por metodo --> 
    
    worker --> handler --> logica para medicion de la energia (no solo org --> demostrar trabajo en 15 min  como hemos implementado la medida de energia en el framework serverless que es lithops ) 
    serverless / statefull / stateless : tipos de aplicaciones que estamos : 
    paralelizar asignando las tareas en diferentes workers 
    100% match 
    stateless : 
    embarrasing paralell 



4) tdp vs energia de hardware 5% --> perf 
grafica de energia con coste energia y tiempo para diferentes tamanos 


porcentaje de ahorro medio / vs aplicacioines 
tiempo extra para obtener ahorro en energia 
diferencias significativas entre las 3 apps 
consume poco cpu? 
entrada salida --> todo gasto es cpu 
resultado tangible --> diferneicas significativas explicadas



resultados aws + k8s? 
kubernetes --> experimento b / fiabilidad de perf vs tdp  (4.b)
lambda no podemos usar rapl (fc) (4.c , 4.d )





ES MAS COMO LO VENDAS QUE COMO LO HAS HECHO
- se ve una demo 
- se ve un documento bonito 

jordi castella: mucho mejor una mierda envuelta en oro, que oro envuelto en mierda 

3  puede ser un monton o mucho 
- predictivos , accuracies muy bajas 
- 2 semanas hay que ser un maquinote --> aplicaciones en los modelos que toquen 
- cambiar con los modelos reales --> cuanto coste temporal tiene 


muy optimistas --> mejor para todos --> 


mas optimista 
llegar a junio con los 3 puntos concluidos 
- figuras una cosa y al final 

2 puntos y en septiembre  


