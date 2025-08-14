import lithops
from lithops.storage import Storage ## abstraccion de lithops para interactuar con el subyacente : interfaz comun independiente al storage

import logging
import os
import time
from datetime import datetime

# Enable debug logging
# logging.basicConfig(level=logging.DEBUG)
# os.environ['LITHOPS_DEBUG'] = '1'


def calcular_coste_aws_lambda(num_invocaciones, memoria_mb=128, duracion_estimada_ms=1000, region='us-east-1'):
    """
    Calcula el coste estimado de ejecutar funciones Lambda en AWS
    
    Parámetros basados en AWS Lambda Pricing (Julio 2025):
    - Request charges: $0.20 por 1M de requests
    - Duration charges: $0.0000166667 por GB-segundo
    
    Args:
        num_invocaciones (int): Número de invocaciones de la función
        memoria_mb (int): Memoria asignada en MB (default: 128MB)
        duracion_estimada_ms (int): Duración estimada por invocación en ms (default: 1000ms)
        region (str): Región de AWS (default: us-east-1)
    
    Returns:
        dict: Desglose de costes estimados
    """
    
    # Pricing de AWS Lambda (us-east-1) - Julio 2025
    coste_por_request = 0.20 / 1_000_000  # $0.20 por millón de requests
    coste_por_gb_segundo = 0.0000166667   # $0.0000166667 por GB-segundo
    
    # Free tier: 1M requests gratuitos y 400,000 GB-segundos por mes
    free_requests = 1_000_000
    free_gb_seconds = 400_000
    
    # Convertir memoria a GB
    memoria_gb = memoria_mb / 1024
    
    # Calcular duración en segundos
    duracion_segundos = duracion_estimada_ms / 1000
    
    # Calcular GB-segundos totales
    gb_segundos_totales = num_invocaciones * memoria_gb * duracion_segundos
    
    # Calcular requests billables (después del free tier)
    requests_billables = max(0, num_invocaciones - free_requests)
    
    # Calcular GB-segundos billables (después del free tier)
    gb_segundos_billables = max(0, gb_segundos_totales - free_gb_seconds)
    
    # Calcular costes
    coste_requests = requests_billables * coste_por_request
    coste_compute = gb_segundos_billables * coste_por_gb_segundo
    coste_total = coste_requests + coste_compute
    
    # Estimar coste de S3 (storage y operaciones)
    # PUT requests: $0.0005 per 1,000 requests
    # GET requests: $0.0004 per 1,000 requests
    # Storage: $0.023 per GB por mes (estimado para archivos pequeños)
    s3_put_requests = num_invocaciones  # 1 PUT por invocación
    s3_get_requests = num_invocaciones * 2  # 1 GET para list_keys + 1 GET para get_object
    
    coste_s3_puts = (s3_put_requests / 1000) * 0.0005
    coste_s3_gets = (s3_get_requests / 1000) * 0.0004
    coste_s3_storage = 0.001  # Estimado para archivos muy pequeños (<1MB total)
    coste_s3_total = coste_s3_puts + coste_s3_gets + coste_s3_storage
    
    coste_total_con_s3 = coste_total + coste_s3_total
    
    resultado = {
        'configuracion': {
            'invocaciones': num_invocaciones,
            'memoria_mb': memoria_mb,
            'duracion_estimada_ms': duracion_estimada_ms,
            'region': region
        },
        'lambda': {
            'requests_totales': num_invocaciones,
            'requests_free_tier': min(num_invocaciones, free_requests),
            'requests_billables': requests_billables,
            'gb_segundos_totales': round(gb_segundos_totales, 6),
            'gb_segundos_free_tier': min(gb_segundos_totales, free_gb_seconds),
            'gb_segundos_billables': round(gb_segundos_billables, 6),
            'coste_requests_usd': round(coste_requests, 6),
            'coste_compute_usd': round(coste_compute, 6),
            'coste_lambda_total_usd': round(coste_total, 6)
        },
        's3': {
            'put_requests': s3_put_requests,
            'get_requests': s3_get_requests,
            'coste_puts_usd': round(coste_s3_puts, 6),
            'coste_gets_usd': round(coste_s3_gets, 6),
            'coste_storage_usd': round(coste_s3_storage, 6),
            'coste_s3_total_usd': round(coste_s3_total, 6)
        },
        'total': {
            'coste_total_usd': round(coste_total_con_s3, 6),
            'coste_total_eur': round(coste_total_con_s3 * 0.92, 6)  # Conversión aproximada USD->EUR
        }
    }
    
    return resultado


def mostrar_simulacion_costes(resultado):
    """
    Muestra de forma legible la simulación de costes
    """
    print("\n" + "="*60)
    print("         SIMULACIÓN DE COSTES AWS LAMBDA + S3")
    print("="*60)
    
    config = resultado['configuracion']
    print(f"\n📊 CONFIGURACIÓN:")
    print(f"   • Invocaciones: {config['invocaciones']:,}")
    print(f"   • Memoria: {config['memoria_mb']} MB")
    print(f"   • Duración estimada: {config['duracion_estimada_ms']} ms")
    print(f"   • Región: {config['region']}")
    
    lambda_info = resultado['lambda']
    print(f"\n🔧 AWS LAMBDA:")
    print(f"   • Requests totales: {lambda_info['requests_totales']:,}")
    print(f"   • Requests free tier: {lambda_info['requests_free_tier']:,}")
    print(f"   • Requests facturables: {lambda_info['requests_billables']:,}")
    print(f"   • GB-segundos totales: {lambda_info['gb_segundos_totales']}")
    print(f"   • GB-segundos free tier: {lambda_info['gb_segundos_free_tier']}")
    print(f"   • GB-segundos facturables: {lambda_info['gb_segundos_billables']}")
    print(f"   • Coste requests: ${lambda_info['coste_requests_usd']}")
    print(f"   • Coste compute: ${lambda_info['coste_compute_usd']}")
    print(f"   • Coste Lambda total: ${lambda_info['coste_lambda_total_usd']}")
    
    s3_info = resultado['s3']
    print(f"\n💾 AWS S3:")
    print(f"   • PUT requests: {s3_info['put_requests']:,}")
    print(f"   • GET requests: {s3_info['get_requests']:,}")
    print(f"   • Coste PUTs: ${s3_info['coste_puts_usd']}")
    print(f"   • Coste GETs: ${s3_info['coste_gets_usd']}")
    print(f"   • Coste storage: ${s3_info['coste_storage_usd']}")
    print(f"   • Coste S3 total: ${s3_info['coste_s3_total_usd']}")
    
    total = resultado['total']
    print(f"\n💰 COSTE TOTAL ESTIMADO:")
    print(f"   • USD: ${total['coste_total_usd']}")
    print(f"   • EUR: €{total['coste_total_eur']} (aprox.)")
    
    if total['coste_total_usd'] == 0:
        print(f"\n✅ ¡Excelente! Tu ejecución está dentro del free tier de AWS!")
    elif total['coste_total_usd'] < 0.01:
        print(f"\n✅ Coste muy bajo - menos de $0.01")
    elif total['coste_total_usd'] < 1.00:
        print(f"\n⚠️  Coste moderado - menos de $1.00")
    else:
        print(f"\n⚠️  Coste significativo - más de $1.00")
    
    print("="*60 + "\n")


def funcion_german ( x ): 
    storage = Storage()
    try:
        # Use the same bucket as configured in lithops
        bucket_name = "lithops-us-east-1-45dk"
        
        # Create a test object
        test_key = f"test-execution/test-file-{x}.txt"
        test_data = f"Hello from AWS Lambda task {x}"
        storage.put_object(bucket_name, test_key, test_data)
        print(f"Created test file in S3: {bucket_name}/{test_key}")
        
        # List objects in the test directory
        keys = storage.list_keys(bucket_name, prefix="test-execution/")
        print(f"Found keys in {bucket_name}: {keys}")
        
        # Read back the test object
        result = storage.get_object(bucket_name, test_key)
        print(f"Read back from S3: {result}")
        
    except Exception as e:
        print(f"AWS S3 operation failed: {e}")
        import traceback
        traceback.print_exc()
    return x + 1

executor = lithops.FunctionExecutor(log_level='debug')

# SIMULACIÓN DE COSTES ANTES DE LA EJECUCIÓN
print("🧮 Realizando simulación de costes antes de la ejecución...")

# Configuración para la simulación
datos_entrada = [1, 2, 3]  # Los datos que vas a procesar
num_invocaciones = len(datos_entrada)
memoria_estimada_mb = 128  # Memoria por defecto de Lambda
duracion_estimada_ms = 2000  # Duración estimada por función (incluyendo S3 ops)

# Calcular costes estimados
simulacion = calcular_coste_aws_lambda(
    num_invocaciones=num_invocaciones,
    memoria_mb=memoria_estimada_mb,
    duracion_estimada_ms=duracion_estimada_ms,
    region='us-east-1'
)

# Mostrar simulación
mostrar_simulacion_costes(simulacion)

# Preguntar al usuario si desea continuar
respuesta = input("¿Deseas continuar con la ejecución? (s/n): ").lower().strip()

if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
    print("\n🚀 Iniciando ejecución...")
    
    # Registrar tiempo de inicio
    tiempo_inicio = time.time()
    inicio_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Inicio: {inicio_timestamp}")
    
    # Ejecutar las funciones
    ft = executor.map(funcion_german, datos_entrada)
    
    # Obtener resultados
    print("\n📋 Obteniendo resultados...")
    resultados = executor.get_result(ft)
    
    # Calcular tiempo transcurrido
    tiempo_fin = time.time()
    fin_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    duracion_real_segundos = tiempo_fin - tiempo_inicio
    duracion_real_ms = duracion_real_segundos * 1000
    
    print(f"\n✅ EJECUCIÓN COMPLETADA")
    print(f"⏰ Fin: {fin_timestamp}")
    print(f"⏱️  Duración total: {duracion_real_segundos:.2f} segundos")
    print(f"📊 Resultados: {resultados}")
    
    # Recalcular costes con duración real
    print("\n🔄 Recalculando costes con duración real...")
    simulacion_real = calcular_coste_aws_lambda(
        num_invocaciones=num_invocaciones,
        memoria_mb=memoria_estimada_mb,
        duracion_estimada_ms=int(duracion_real_ms / len(datos_entrada)),  # Duración promedio por función
        region='us-east-1'
    )
    
    print("\n📊 COMPARACIÓN ESTIMADO vs REAL:")
    print(f"   • Duración estimada por función: {duracion_estimada_ms} ms")
    print(f"   • Duración real promedio: {int(duracion_real_ms / len(datos_entrada))} ms")
    print(f"   • Coste estimado: ${simulacion['total']['coste_total_usd']}")
    print(f"   • Coste real: ${simulacion_real['total']['coste_total_usd']}")
    
    diferencia = simulacion_real['total']['coste_total_usd'] - simulacion['total']['coste_total_usd']
    if diferencia > 0:
        print(f"   • Diferencia: +${diferencia:.6f} (más caro de lo estimado)")
    elif diferencia < 0:
        print(f"   • Diferencia: ${diferencia:.6f} (más barato de lo estimado)")
    else:
        print(f"   • Diferencia: $0 (igual al estimado)")

else:
    print("\n❌ Ejecución cancelada por el usuario.")

 