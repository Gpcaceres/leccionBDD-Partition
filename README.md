# Sistema de Gestión de Créditos - Ministerio de Desarrollo Humano

Middleware de particionamiento lógico para gestión de créditos de desarrollo humano con almacenamiento distribuido entre PostgreSQL (histórico) y SQL Server (operacional).

## 📋 Contexto del Proyecto

El Ministerio de Desarrollo Humano administra un sistema de información que gestiona grandes volúmenes de datos históricos y actuales correspondientes a los años 2022, 2023, 2024 y 2025. A medida que el volumen crece, el rendimiento de consulta y el costo de almacenamiento se ven afectados.

Para mitigar este problema se implementa una **estrategia de particionamiento lógico por año**, distribuyendo los datos entre motores de base de datos heterogéneos, manteniendo la misma lógica de negocio y asegurando la integridad operacional.

## 🎯 Objetivos

### Objetivo General
Diseñar e implementar una solución de particionamiento lógico y acceso distribuido que permita optimizar consultas, escalar almacenamiento y mantener reglas de negocio consistentes.

### Objetivos Específicos
1. ✅ **Optimizar consultas** separando datos actuales vs. históricos
2. ✅ **Escalar almacenamiento** delegando histórico a PostgreSQL
3. ✅ **Mantener reglas de negocio** consistentes (validaciones, transaccionalidad, manejo de errores)
4. ✅ **Integrar motores heterogéneos** (PostgreSQL + SQL Server) en un flujo único

## 🏗️ Arquitectura de Particionamiento

### Condiciones Obligatorias

```
┌──────────────────────────────────────────────────────┐
│           MIDDLEWARE PYTHON                          │
│        (Lógica de Particionamiento)                  │
└────────────────┬─────────────────┬───────────────────┘
                 │                 │
                 │                 │
        ┌────────┴────────┐   ┌────┴────────────┐
        │                 │   │                 │
        ▼                 │   │                 ▼
┌──────────────┐         │   │       ┌──────────────┐
│ PostgreSQL   │         │   │       │ SQL Server   │
│              │         │   │       │              │
│ HISTÓRICO    │         │   │       │ OPERACIONAL  │
│ (2022-2024)  │         │   │       │   (2025)     │
└──────────────┘         │   │       └──────────────┘
                         │   │
                 Datos   │   │   Datos
                Históricos   │  Actuales
                         │   │
                    2022 │   │ 2025
                    2023 │   │
                    2024 │   │
                         │   │
                    Crecimiento →
```

### Distribución de Datos

| Período | Motor | Función | Características |
|---------|-------|---------|----------------|
| **2022-2024** | PostgreSQL | Repositorio Histórico | • Datos de solo lectura<br>• Optimizado para consultas analíticas<br>• Menor costo de almacenamiento |
| **2025** | SQL Server | Repositorio Operacional | • Datos activos<br>• Operaciones CRUD frecuentes<br>• Alto rendimiento transaccional |

## 📊 Estructura de Datos

### PostgreSQL: creditos_historicos
```sql
CREATE TABLE creditos_historicos (
    credito_id     INT PRIMARY KEY,
    anio           INT NOT NULL CHECK (anio IN (2022, 2023, 2024)),
    mes            INT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    beneficiario   VARCHAR(100) NOT NULL,
    monto          NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    estado         VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### SQL Server: CreditosActuales
```sql
CREATE TABLE CreditosActuales (
    CreditoID     INT NOT NULL PRIMARY KEY,
    Anio          INT NOT NULL CHECK (Anio = 2025),
    Mes           INT NOT NULL CHECK (Mes BETWEEN 1 AND 12),
    Beneficiario  NVARCHAR(100) NOT NULL,
    Monto         DECIMAL(12,2) NOT NULL CHECK (Monto > 0),
    Estado        NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    FechaRegistro DATETIME DEFAULT GETDATE()
);
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.10+
- PostgreSQL 12+
- SQL Server 2019+ (Express/Developer)
- ODBC Driver 17 for SQL Server

### Paso 1: Clonar y preparar entorno

```bash
cd ministerio-desarrollo-humano

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar PostgreSQL

```bash
# Conectarse a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE mdh_historico;

# Conectarse a la nueva base
\c mdh_historico

# Ejecutar el script de setup_databases.sql (sección PostgreSQL)
```

### Paso 3: Configurar SQL Server

```sql
-- En SSMS, ejecutar:
CREATE DATABASE MDH_Operacional;
GO

USE MDH_Operacional;
GO

-- Ejecutar el script de setup_databases.sql (sección SQL Server)
```

### Paso 4: Ajustar credenciales

Edita `main.py` y actualiza las contraseñas:

```python
# Línea 20: PostgreSQL
password="admin"  # ← Cambia por tu contraseña

# Línea 37: SQL Server
"PWD=admin"  # ← Cambia por tu contraseña
```

### Paso 5: Ejecutar

```bash
python main.py
```

## 📈 Funcionalidades Principales

### 1. Inserción Automática con Particionamiento

```python
insert_credito(1001, 2022, 3, "Juan Pérez", 1500.00, "ACTIVO")
# → Se inserta en PostgreSQL (histórico)

insert_credito(2001, 2025, 1, "María López", 2500.00, "ACTIVO")
# → Se inserta en SQL Server (operacional)
```

### 2. Consulta Unificada

```python
creditos = consultar_todos_creditos()
# → Combina datos de PostgreSQL + SQL Server
# → Retorna lista ordenada por año y mes
```

### 3. Consulta por Año (Optimizada)

```python
creditos_2023 = consultar_por_anio(2023)
# → Consulta directamente PostgreSQL

creditos_2025 = consultar_por_anio(2025)
# → Consulta directamente SQL Server
```

### 4. Reporte Consolidado

```python
imprimir_reporte_consolidado(creditos)
# → Muestra tabla formateada
# → Incluye totales por año
# → Indica origen de cada registro
```

## 🔍 Lógica de Negocio

### Validaciones Implementadas

✅ **Validación de año**: Solo acepta 2022, 2023, 2024, 2025  
✅ **Validación de mes**: Solo acepta 1-12  
✅ **Validación de monto**: Debe ser mayor a 0  
✅ **Manejo de transacciones**: Commit/Rollback automático  
✅ **Manejo de errores**: Mensajes descriptivos  
✅ **Integridad referencial**: PKs y constraints en ambos motores

### Reglas de Particionamiento

```python
if anio in [2022, 2023, 2024]:
    # → PostgreSQL (repositorio histórico)
    # Optimizado para consultas analíticas
    # Datos de solo lectura en producción
    
elif anio == 2025:
    # → SQL Server (repositorio operacional)
    # Optimizado para transacciones OLTP
    # Operaciones CRUD frecuentes
```

## 📊 Ejemplo de Salida

```
================================================================================
                REPORTE CONSOLIDADO DE CRÉDITOS
                   MINISTERIO DE DESARROLLO HUMANO
================================================================================
ID       AÑO    MES   BENEFICIARIO                   MONTO           ESTADO       ORIGEN
----------------------------------------------------------------------------------------------------
1001     2022   3     Juan Pérez González            $1,500.00       ACTIVO       PostgreSQL (Histórico)
1002     2022   7     María López Rodríguez          $2,000.00       ACTIVO       PostgreSQL (Histórico)
1003     2023   1     Carlos Martínez Díaz           $1,800.50       ACTIVO       PostgreSQL (Histórico)
...
2001     2025   1     Jorge Herrera Medina           $2,500.00       ACTIVO       SQL Server (Actual)
2002     2025   2     Laura Jiménez Ortiz            $2,300.75       ACTIVO       SQL Server (Actual)
----------------------------------------------------------------------------------------------------

RESUMEN POR AÑO:
--------------------------------------------------
  Año 2022: $     3,500.00  (PostgreSQL (Histórico))
  Año 2023: $     5,650.25  (PostgreSQL (Histórico))
  Año 2024: $     5,750.75  (PostgreSQL (Histórico))
  Año 2025: $     9,750.25  (SQL Server (Actual))
--------------------------------------------------
TOTAL GENERAL:           $    24,651.25
CANTIDAD DE CRÉDITOS:                12
================================================================================
```

## 🎓 Beneficios de la Arquitectura

### Rendimiento
- ✅ Separación de cargas OLTP (SQL Server) y OLAP (PostgreSQL)
- ✅ Consultas históricas no afectan operaciones actuales
- ✅ Índices optimizados por caso de uso

### Escalabilidad
- ✅ Crecimiento de histórico no afecta rendimiento operacional
- ✅ Posibilidad de archivar años antiguos fácilmente
- ✅ Flexible para agregar nuevos repositorios

### Costos
- ✅ PostgreSQL (gratuito) para volumen histórico grande
- ✅ SQL Server solo para datos actuales (menor licenciamiento)
- ✅ Optimización de recursos por motor

### Mantenibilidad
- ✅ Código centralizado en middleware Python
- ✅ Lógica de negocio consistente
- ✅ Fácil debugging y monitoreo

## 📁 Estructura del Proyecto

```
ministerio-desarrollo-humano/
│
├── main.py                    # Script principal
├── setup_databases.sql        # Scripts de creación de BD
├── requirements.txt           # Dependencias Python
├── README.md                 # Este archivo
└── .gitignore                # Archivos a ignorar en Git
```

## 🔐 Consideraciones de Seguridad

⚠️ **Para producción:**
- Usar variables de entorno para credenciales
- Implementar autenticación con Azure AD / OAuth
- Habilitar SSL/TLS en conexiones
- Aplicar principio de mínimo privilegio
- Auditar accesos y cambios
- Encriptar datos sensibles

## 📚 Tecnologías Utilizadas

- **Python 3.10+** - Lenguaje principal
- **PostgreSQL** - Repositorio histórico
- **SQL Server** - Repositorio operacional
- **pyodbc** - Conector SQL Server
- **psycopg2** - Conector PostgreSQL

## 👥 Autor

Ministerio de Desarrollo Humano - Sistema de Gestión de Créditos

## 📄 Licencia

Proyecto educativo - Laboratorio de Bases de Datos Distribuidas
