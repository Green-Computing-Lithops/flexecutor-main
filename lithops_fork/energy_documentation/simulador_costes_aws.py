#!/usr/bin/env python3
"""
Simulador de Costes AWS Lambda - Casos de Uso Comunes
=====================================================

Este script proporciona ejemplos de simulación de costes para diferentes
escenarios de uso de AWS Lambda con Lithops.

Basado en AWS Lambda Pricing: https://aws.amazon.com/es/lambda/pricing/
"""

import sys
import os

# Añadir el directorio padre al path para importar las funciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_german import calcular_coste_aws_lambda, mostrar_simulacion_costes


def simular_escenarios():
    """
    Simula diferentes escenarios de uso comunes
    """
    
    escenarios = [
        {
            'nombre': 'Desarrollo/Testing - Pocas invocaciones',
            'descripcion': 'Script de prueba con pocas ejecuciones',
            'invocaciones': 10,
            'memoria_mb': 128,
            'duracion_ms': 1000
        },
        {
            'nombre': 'Procesamiento ligero - Batch pequeño',
            'descripcion': 'Procesamiento de 100 elementos pequeños',
            'invocaciones': 100,
            'memoria_mb': 128,
            'duracion_ms': 2000
        },
        {
            'nombre': 'Procesamiento medio - Batch mediano',
            'descripcion': 'Procesamiento de 1000 elementos',
            'invocaciones': 1000,
            'memoria_mb': 256,
            'duracion_ms': 3000
        },
        {
            'nombre': 'Procesamiento intensivo - Batch grande',
            'descripcion': 'Procesamiento de 10,000 elementos',
            'invocaciones': 10000,
            'memoria_mb': 512,
            'duracion_ms': 5000
        },
        {
            'nombre': 'Machine Learning - Training distribuido',
            'descripcion': 'Entrenamiento ML con alta memoria y duración',
            'invocaciones': 500,
            'memoria_mb': 1024,
            'duracion_ms': 30000
        },
        {
            'nombre': 'Big Data - Procesamiento masivo',
            'descripcion': 'Análisis de big data con muchas invocaciones',
            'invocaciones': 100000,
            'memoria_mb': 256,
            'duracion_ms': 2000
        }
    ]
    
    print("🧮 SIMULADOR DE COSTES AWS LAMBDA + S3")
    print("=====================================")
    print("Selecciona un escenario para simular:\n")
    
    for i, escenario in enumerate(escenarios, 1):
        print(f"{i}. {escenario['nombre']}")
        print(f"   {escenario['descripcion']}")
        print(f"   ({escenario['invocaciones']:,} invocaciones, {escenario['memoria_mb']}MB, {escenario['duracion_ms']}ms)\n")
    
    print("7. Escenario personalizado")
    print("0. Salir\n")
    
    try:
        opcion = int(input("Selecciona una opción (0-7): "))
        
        if opcion == 0:
            print("👋 ¡Hasta luego!")
            return
        
        elif 1 <= opcion <= 6:
            escenario = escenarios[opcion - 1]
            print(f"\n🎯 Simulando: {escenario['nombre']}")
            print(f"📝 {escenario['descripcion']}\n")
            
            resultado = calcular_coste_aws_lambda(
                num_invocaciones=escenario['invocaciones'],
                memoria_mb=escenario['memoria_mb'],
                duracion_estimada_ms=escenario['duracion_ms']
            )
            
            mostrar_simulacion_costes(resultado)
            
        elif opcion == 7:
            print("\n📝 ESCENARIO PERSONALIZADO")
            print("=" * 30)
            
            invocaciones = int(input("Número de invocaciones: "))
            memoria = int(input("Memoria en MB (128, 256, 512, 1024, etc.): "))
            duracion = int(input("Duración estimada en ms: "))
            
            print(f"\n🎯 Simulando escenario personalizado:")
            print(f"   • {invocaciones:,} invocaciones")
            print(f"   • {memoria} MB de memoria")
            print(f"   • {duracion} ms de duración\n")
            
            resultado = calcular_coste_aws_lambda(
                num_invocaciones=invocaciones,
                memoria_mb=memoria,
                duracion_estimada_ms=duracion
            )
            
            mostrar_simulacion_costes(resultado)
            
        else:
            print("❌ Opción no válida")
            
    except ValueError:
        print("❌ Por favor, introduce un número válido")
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")


def comparar_configuraciones():
    """
    Compara diferentes configuraciones de memoria para el mismo workload
    """
    print("\n🔍 COMPARACIÓN DE CONFIGURACIONES DE MEMORIA")
    print("=" * 50)
    
    invocaciones = 1000
    duracion_base = 5000  # ms
    
    configuraciones = [
        {'memoria': 128, 'factor_velocidad': 1.0},
        {'memoria': 256, 'factor_velocidad': 0.8},
        {'memoria': 512, 'factor_velocidad': 0.6},
        {'memoria': 1024, 'factor_velocidad': 0.5},
        {'memoria': 2048, 'factor_velocidad': 0.4}
    ]
    
    print(f"📊 Comparando {invocaciones:,} invocaciones con diferentes configuraciones:")
    print(f"   (Duración base: {duracion_base}ms con 128MB)\n")
    
    resultados = []
    
    for config in configuraciones:
        # Ajustar duración según la memoria (más memoria = más velocidad)
        duracion_ajustada = int(duracion_base * config['factor_velocidad'])
        
        resultado = calcular_coste_aws_lambda(
            num_invocaciones=invocaciones,
            memoria_mb=config['memoria'],
            duracion_estimada_ms=duracion_ajustada
        )
        
        resultados.append({
            'memoria': config['memoria'],
            'duracion': duracion_ajustada,
            'coste': resultado['total']['coste_total_usd']
        })
    
    print("💰 COMPARACIÓN DE COSTES:")
    print("-" * 40)
    for r in resultados:
        print(f"   {r['memoria']:4d}MB | {r['duracion']:4d}ms | ${r['coste']:8.6f}")
    
    # Encontrar la opción más económica
    mas_barato = min(resultados, key=lambda x: x['coste'])
    print(f"\n✅ Configuración más económica:")
    print(f"   {mas_barato['memoria']}MB - ${mas_barato['coste']:.6f}")


def calcular_breakeven_free_tier():
    """
    Calcula cuántas invocaciones puedes hacer dentro del free tier
    """
    print("\n🆓 CALCULADORA FREE TIER")
    print("=" * 25)
    
    print("Límites del Free Tier de AWS Lambda:")
    print("• 1,000,000 requests gratuitos por mes")
    print("• 400,000 GB-segundos gratuitos por mes\n")
    
    memoria_mb = int(input("Memoria configurada (MB): "))
    duracion_ms = int(input("Duración por invocación (ms): "))
    
    memoria_gb = memoria_mb / 1024
    duracion_segundos = duracion_ms / 1000
    gb_segundos_por_invocacion = memoria_gb * duracion_segundos
    
    # Límites del free tier
    limite_requests = 1_000_000
    limite_gb_segundos = 400_000
    
    # Calcular máximas invocaciones por cada límite
    max_por_requests = limite_requests
    max_por_compute = int(limite_gb_segundos / gb_segundos_por_invocacion)
    
    # El límite real es el menor de los dos
    max_invocaciones_gratis = min(max_por_requests, max_por_compute)
    
    print(f"\n📊 RESULTADOS:")
    print(f"   • GB-segundos por invocación: {gb_segundos_por_invocacion:.6f}")
    print(f"   • Máximo por límite de requests: {max_por_requests:,}")
    print(f"   • Máximo por límite de compute: {max_por_compute:,}")
    print(f"   • ✅ Máximo real gratuito: {max_invocaciones_gratis:,} invocaciones/mes")
    
    if max_invocaciones_gratis < 1000:
        print(f"   ⚠️  Configuración intensiva - solo {max_invocaciones_gratis} invocaciones gratis")
    elif max_invocaciones_gratis < 10000:
        print(f"   🟡 Configuración moderada")
    else:
        print(f"   ✅ Configuración eficiente para el free tier")


def menu_principal():
    """
    Menú principal del simulador
    """
    while True:
        print("\n" + "="*50)
        print("    SIMULADOR DE COSTES AWS LAMBDA")
        print("="*50)
        print("1. Simular escenarios predefinidos")
        print("2. Comparar configuraciones de memoria")
        print("3. Calculadora Free Tier")
        print("4. Información sobre pricing")
        print("0. Salir")
        print("-"*50)
        
        try:
            opcion = input("Selecciona una opción: ").strip()
            
            if opcion == "0":
                print("👋 ¡Hasta luego!")
                break
            elif opcion == "1":
                simular_escenarios()
            elif opcion == "2":
                comparar_configuraciones()
            elif opcion == "3":
                calcular_breakeven_free_tier()
            elif opcion == "4":
                mostrar_info_pricing()
            else:
                print("❌ Opción no válida")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def mostrar_info_pricing():
    """
    Muestra información detallada sobre el pricing de AWS Lambda
    """
    print("\n💰 INFORMACIÓN DE PRICING AWS LAMBDA")
    print("=" * 40)
    print("📍 Región: US East (N. Virginia)")
    print("📅 Actualizado: Julio 2025")
    print("\n🔹 REQUESTS:")
    print("   • $0.20 por 1,000,000 requests")
    print("   • Free tier: 1,000,000 requests/mes")
    print("\n🔹 DURATION (COMPUTE):")
    print("   • $0.0000166667 por GB-segundo")
    print("   • Free tier: 400,000 GB-segundos/mes")
    print("\n🔹 S3 PRICING:")
    print("   • PUT requests: $0.0005 por 1,000 requests")
    print("   • GET requests: $0.0004 por 1,000 requests")
    print("   • Storage: $0.023 por GB/mes")
    print("\n🔗 Más información:")
    print("   https://aws.amazon.com/es/lambda/pricing/")
    print("   https://aws.amazon.com/es/s3/pricing/")


if __name__ == "__main__":
    menu_principal()
