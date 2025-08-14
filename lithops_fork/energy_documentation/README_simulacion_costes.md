# Simulador de Costes AWS Lambda para Lithops

Este conjunto de herramientas te permite estimar los costes de ejecutar tus workloads de Lithops en AWS Lambda **antes** de ejecutarlos, ayudándote a optimizar costes y evitar sorpresas en tu factura de AWS.

## 🎯 ¿Por qué usar simulación de costes?

- **💰 Evitar sorpresas**: Conoce el coste antes de ejecutar
- **🎛️ Optimización**: Compara diferentes configuraciones
- **📊 Planificación**: Estima costes para diferentes escalas
- **🆓 Free Tier**: Maximiza el uso del tier gratuito de AWS
- **📈 Escalabilidad**: Planifica el crecimiento de tus workloads

## 📁 Archivos incluidos

```
energy_documentation/
├── main_german.py              # Tu script principal con simulación integrada
├── simulador_costes_aws.py     # Simulador interactivo
├── ejemplos_costes.py          # Ejemplos para diferentes workloads
└── README_simulacion_costes.md # Esta documentación
```

## 🚀 Uso rápido

### 1. Script principal con simulación integrada

Tu archivo `main_german.py` ahora incluye simulación de costes automática:

```bash
python main_german.py
```

El script te mostrará:
- 🧮 Simulación de costes estimados
- ❓ Confirmación antes de ejecutar
- ⏱️ Tiempo real de ejecución
- 📊 Comparación estimado vs real

### 2. Simulador interactivo

Para explorar diferentes escenarios sin ejecutar código:

```bash
python simulador_costes_aws.py
```

Incluye:
- 📋 Escenarios predefinidos (desarrollo, batch, ML, etc.)
- 🎛️ Configuración personalizada
- 🔍 Comparación de configuraciones de memoria
- 🆓 Calculadora del Free Tier

### 3. Ejemplos específicos por workload

Para ver ejemplos detallados de diferentes tipos de aplicaciones:

```bash
python ejemplos_costes.py
```

Cubre:
- 🖼️ Procesamiento de imágenes
- 📊 Análisis de datos
- 🤖 Machine Learning
- 🌐 APIs serverless

## 💡 Casos de uso

### Desarrollo y Testing
```python
# Pocas invocaciones para pruebas
simulacion = calcular_coste_aws_lambda(
    num_invocaciones=10,
    memoria_mb=128,
    duracion_estimada_ms=1000
)
# ✅ Resultado: $0.00 (dentro del free tier)
```

### Procesamiento Batch
```python
# Procesamiento de 1000 elementos
simulacion = calcular_coste_aws_lambda(
    num_invocaciones=1000,
    memoria_mb=256,
    duracion_estimada_ms=3000
)
# 💰 Resultado: ~$0.02
```

### Machine Learning
```python
# Entrenamiento distribuido
simulacion = calcular_coste_aws_lambda(
    num_invocaciones=100,
    memoria_mb=1024,
    duracion_estimada_ms=30000
)
# 💰 Resultado: ~$0.50
```

## 📊 Interpretando los resultados

La simulación te muestra:

```
📊 CONFIGURACIÓN:
   • Invocaciones: 1,000
   • Memoria: 256 MB
   • Duración estimada: 3000 ms
   • Región: us-east-1

🔧 AWS LAMBDA:
   • Requests totales: 1,000
   • Requests free tier: 1,000
   • Requests facturables: 0
   • GB-segundos totales: 0.75
   • GB-segundos free tier: 0.75
   • GB-segundos facturables: 0.0
   • Coste Lambda total: $0.0

💾 AWS S3:
   • PUT requests: 1,000
   • GET requests: 2,000
   • Coste S3 total: $0.002

💰 COSTE TOTAL ESTIMADO:
   • USD: $0.002
   • EUR: €0.0018 (aprox.)
```

## 🎛️ Parámetros de configuración

### `num_invocaciones`
- Número de veces que se ejecutará tu función
- Directamente relacionado con el tamaño de tu dataset

### `memoria_mb`
- Memoria asignada a cada función Lambda
- Opciones típicas: 128, 256, 512, 1024, 2048, 3008 MB
- ⚡ Más memoria = mayor velocidad pero mayor coste por GB-segundo

### `duracion_estimada_ms`
- Tiempo estimado que tardará cada función
- Incluye tiempo de procesamiento + operaciones S3
- 🎯 Optimizar este parámetro es clave para reducir costes

### `region`
- Región de AWS donde ejecutas (afecta precios)
- Por defecto: `us-east-1` (más barata)

## 💰 Pricing de AWS Lambda (Julio 2025)

### Requests
- **Coste**: $0.20 por 1,000,000 requests
- **Free tier**: 1,000,000 requests/mes

### Duration (Compute)
- **Coste**: $0.0000166667 por GB-segundo
- **Free tier**: 400,000 GB-segundos/mes

### S3 (incluido en simulación)
- **PUT requests**: $0.0005 por 1,000 requests
- **GET requests**: $0.0004 por 1,000 requests
- **Storage**: $0.023 por GB/mes

## 🎯 Estrategias de optimización

### 1. Optimizar duración
```python
# ❌ Código no optimizado (5000ms)
def funcion_lenta(data):
    # Código ineficiente
    time.sleep(1)  # Simulando procesamiento lento
    return process(data)

# ✅ Código optimizado (1000ms)
def funcion_rapida(data):
    # Código eficiente
    return process_optimized(data)
```

### 2. Balance memoria vs duración
```python
# Comparar configuraciones
configs = [
    {'memoria': 256, 'tiempo': 5000},  # Lento pero poca memoria
    {'memoria': 512, 'tiempo': 3000},  # Balance
    {'memoria': 1024, 'tiempo': 2000}  # Rápido pero más memoria
]

for config in configs:
    sim = calcular_coste_aws_lambda(1000, config['memoria'], config['tiempo'])
    print(f"Memoria: {config['memoria']}MB - Coste: ${sim['total']['coste_total_usd']}")
```

### 3. Aprovechar el Free Tier
```python
# Calcular máximo gratuito mensual
memoria_gb = 256 / 1024  # 0.25 GB
duracion_seg = 2  # 2 segundos
gb_seg_por_invocacion = memoria_gb * duracion_seg  # 0.5 GB-seg

max_invocaciones_gratis = 400_000 / gb_seg_por_invocacion  # 800,000 invocaciones
```

## 🔧 Personalización avanzada

### Añadir tu propia función de simulación

```python
from main_german import calcular_coste_aws_lambda, mostrar_simulacion_costes

def mi_workload_personalizado():
    # Tus parámetros específicos
    resultado = calcular_coste_aws_lambda(
        num_invocaciones=5000,
        memoria_mb=512,
        duracion_estimada_ms=4000,
        region='us-east-1'
    )
    
    mostrar_simulacion_costes(resultado)
    return resultado
```

### Integrar en tu flujo de CI/CD

```python
# En tu script de deployment
simulacion = calcular_coste_aws_lambda(expected_invocations, memory, duration)

# Establecer límites de coste
LIMITE_COSTE_USD = 10.0

if simulacion['total']['coste_total_usd'] > LIMITE_COSTE_USD:
    print(f"⚠️ Coste estimado (${simulacion['total']['coste_total_usd']}) "
          f"excede el límite (${LIMITE_COSTE_USD})")
    exit(1)
```

## 📈 Monitoreo de costes reales

Después de ejecutar tus workloads, compara con los costes reales:

1. **AWS Cost Explorer**: Para ver costes detallados
2. **AWS Budgets**: Para configurar alertas
3. **CloudWatch**: Para métricas de duración real

## ⚠️ Limitaciones y consideraciones

- **Estimaciones**: Los costes son estimados, los reales pueden variar
- **Cold starts**: No incluye tiempo de arranque en frío
- **Networking**: No incluye costes de transferencia de datos
- **Otros servicios**: Solo incluye Lambda + S3 básico
- **Precios**: Pueden cambiar, verificar pricing actual de AWS

## 🤝 Contribuir

Para mejorar las simulaciones:

1. Actualizar precios en `calcular_coste_aws_lambda()`
2. Añadir nuevos escenarios en `ejemplos_costes.py`
3. Mejorar precisión de estimaciones
4. Añadir soporte para otras regiones

## 🔗 Referencias

- [AWS Lambda Pricing](https://aws.amazon.com/es/lambda/pricing/)
- [AWS S3 Pricing](https://aws.amazon.com/es/s3/pricing/)
- [AWS Free Tier](https://aws.amazon.com/es/free/)
- [Lithops Documentation](https://lithops.cloud/)

---

💡 **Tip**: Empieza siempre con el simulador antes de ejecutar workloads grandes. ¡Tu cuenta bancaria te lo agradecerá! 💰
