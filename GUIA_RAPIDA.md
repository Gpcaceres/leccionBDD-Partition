# 🚀 GUÍA RÁPIDA DE EJECUCIÓN
## Ministerio de Desarrollo Humano - Sistema de Créditos

## Pasos resumidos para ejecutar el proyecto

### 1️⃣ Instalar Python y dependencias

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.\.venv\Scripts\activate

# Instalar librerías
pip install pyodbc psycopg2-binary
```

### 2️⃣ Configurar PostgreSQL (Repositorio Histórico)

**En pgAdmin o psql, ejecutar:**

```sql
-- Crear base de datos
CREATE DATABASE mdh_historico;

-- Conectarse a mdh_historico
\c mdh_historico

-- Crear tabla
CREATE TABLE creditos_historicos (
    credito_id     INT PRIMARY KEY,
    anio           INT NOT NULL CHECK (anio IN (2022, 2023, 2024)),
    mes            INT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    beneficiario   VARCHAR(100) NOT NULL,
    monto          NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    estado         VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices
CREATE INDEX idx_creditos_historicos_anio_mes ON creditos_historicos(anio, mes);
```

**Verificar credenciales:**
- Usuario: `postgres`
- Contraseña: ajusta en el código (línea 20)

### 3️⃣ Configurar SQL Server (Repositorio Operacional)

**En SSMS o sqlcmd, ejecutar:**

```sql
-- Crear base de datos
CREATE DATABASE MDH_Operacional;
GO

USE MDH_Operacional;
GO

-- Crear tabla
CREATE TABLE dbo.CreditosActuales (
    CreditoID     INT NOT NULL PRIMARY KEY,
    Anio          INT NOT NULL CHECK (Anio = 2025),
    Mes           INT NOT NULL CHECK (Mes BETWEEN 1 AND 12),
    Beneficiario  NVARCHAR(100) NOT NULL,
    Monto         DECIMAL(12,2) NOT NULL CHECK (Monto > 0),
    Estado        NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    FechaRegistro DATETIME DEFAULT GETDATE()
);
GO

-- Crear índices
CREATE INDEX IX_CreditosActuales_Anio_Mes ON dbo.CreditosActuales(Anio, Mes);
GO
```

**Verificar autenticación:**
- Usuario: `sa`
- Contraseña: ajusta en el código (línea 37)

### 4️⃣ Ajustar credenciales en el código

Edita `main.py`:

**PostgreSQL (línea ~20):**
```python
password="admin"  # ← Cambia por tu contraseña
```

**SQL Server (línea ~37):**
```python
"PWD=admin"  # ← Cambia por tu contraseña
```

### 5️⃣ Ejecutar el proyecto

```bash
python main.py
```

### 6️⃣ Verificar resultados

**PostgreSQL (histórico 2022-2024):**
```sql
\c mdh_historico
SELECT * FROM creditos_historicos ORDER BY anio, mes;
```

**SQL Server (operacional 2025):**
```sql
USE MDH_Operacional;
SELECT * FROM dbo.CreditosActuales ORDER BY Mes;
```

---

## 🎯 Criterio de Particionamiento

```
┌─────────────────────────────────────────┐
│  ¿Año del crédito es 2022, 2023 o 2024? │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴───────┐
      │               │
     SÍ              NO (2025)
      │               │
      ▼               ▼
 ┌──────────┐    ┌──────────┐
 │PostgreSQL│    │   SQL    │
 │          │    │  Server  │
 └──────────┘    └──────────┘
  Histórico      Operacional
 (2022-2024)       (2025)
```

---

## 📊 Resultado Esperado

```
================================================================================
                SISTEMA DE GESTIÓN DE CRÉDITOS DE DESARROLLO HUMANO
                         MINISTERIO DE DESARROLLO HUMANO
================================================================================

Estrategia de Particionamiento Lógico:
  • Datos HISTÓRICOS (2022, 2023, 2024) → PostgreSQL (repositorio histórico)
  • Datos ACTUALES (2025) → SQL Server (repositorio operacional)
================================================================================

--- Insertando crédito ID=1001, Año=2022, Mes=3, Beneficiario=Juan Pérez González, Monto=$1,500.00, Estado=ACTIVO ---
→ El año 2022 es HISTÓRICO (2022-2024) → Insertando en PostgreSQL
✓ Insertado exitosamente en PostgreSQL (repositorio histórico)

[... más inserciones ...]

================================================================================
                         REPORTE CONSOLIDADO DE CRÉDITOS
                        MINISTERIO DE DESARROLLO HUMANO
================================================================================
ID       AÑO    MES   BENEFICIARIO                   MONTO           ESTADO       ORIGEN
----------------------------------------------------------------------------------------------------
1001     2022   3     Juan Pérez González            $1,500.00       ACTIVO       PostgreSQL (Histórico)
...
2001     2025   1     Jorge Herrera Medina           $2,500.00       ACTIVO       SQL Server (Actual)
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

---

## ✅ Checklist de Verificación

- [ ] Python 3.10+ instalado
- [ ] PostgreSQL corriendo localmente
- [ ] SQL Server corriendo localmente
- [ ] ODBC Driver 17 instalado
- [ ] Entorno virtual creado y activado
- [ ] Librerías instaladas
- [ ] Base de datos `mdh_historico` creada en PostgreSQL
- [ ] Tabla `creditos_historicos` creada
- [ ] Base de datos `MDH_Operacional` creada en SQL Server
- [ ] Tabla `CreditosActuales` creada
- [ ] Credenciales ajustadas en `main.py`
- [ ] Script ejecutado exitosamente
- [ ] Créditos visibles en ambos repositorios

---

## ❓ Problemas Comunes

### "ODBC Driver 17 not found"
👉 Descarga e instala desde:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### "Login failed for user 'sa'"
👉 Verifica:
1. SQL Server Authentication habilitada
2. Contraseña correcta
3. SSMS → Propiedades servidor → Security

### "connection to server failed" (PostgreSQL)
👉 Verifica:
1. PostgreSQL corriendo: `pg_isready`
2. Credenciales correctas
3. Puerto 5432 abierto

### "duplicate key value violates unique constraint"
👉 Los registros ya existen. Para limpiar:

**PostgreSQL:**
```sql
TRUNCATE TABLE creditos_historicos;
```

**SQL Server:**
```sql
TRUNCATE TABLE dbo.CreditosActuales;
```

---

¡Listo! 🎉

**Nota:** Este sistema está optimizado para separar datos históricos (PostgreSQL) de datos operacionales (SQL Server), mejorando rendimiento y reduciendo costos.
