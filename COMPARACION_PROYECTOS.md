# 🔄 COMPARACIÓN ENTRE PROYECTOS

## Proyecto 1: Laboratorio de Ventas vs Proyecto 2: Ministerio de Desarrollo Humano

### 📊 Tabla Comparativa

| Aspecto | Ventas (Lab) | Ministerio Desarrollo Humano |
|---------|-------------|------------------------------|
| **Contexto** | Empresa migrando plataforma de ventas | Ministerio gestionando créditos |
| **Criterio de Particionamiento** | < 2023 → SQL Server<br>≥ 2023 → PostgreSQL | 2022-2024 → PostgreSQL<br>2025 → SQL Server |
| **Motor Histórico** | SQL Server | PostgreSQL |
| **Motor Actual** | PostgreSQL | SQL Server |
| **Base de datos histórica** | ParticionDBSQLServer | mdh_historico |
| **Base de datos actual** | particiondbpostgres | MDH_Operacional |
| **Tabla histórica** | VentasSQLServer | creditos_historicos |
| **Tabla actual** | ventas_postgres | CreditosActuales |
| **Años históricos** | 2020, 2021, 2022 | 2022, 2023, 2024 |
| **Años actuales** | 2023, 2024, 2025 | 2025 |

### 🎯 Diferencia Principal

**Laboratorio de Ventas:**
```
Histórico (< 2023) → SQL Server
Actual (≥ 2023) → PostgreSQL
```

**Ministerio Desarrollo Humano:**
```
Histórico (2022-2024) → PostgreSQL
Actual (2025) → SQL Server
```

### 💡 ¿Por qué la inversión?

#### Laboratorio de Ventas
- Simula migración DE SQL Server HACIA PostgreSQL
- SQL Server = sistema legacy (antiguo)
- PostgreSQL = sistema nuevo (moderno)
- Datos nuevos van al sistema moderno

#### Ministerio Desarrollo Humano
- Enfoque en optimización de costos y rendimiento
- PostgreSQL = almacenamiento histórico económico (OLAP)
- SQL Server = operaciones actuales de alta performance (OLTP)
- Separa cargas analíticas de transaccionales

### 📁 Estructura de Datos

#### Laboratorio de Ventas
```sql
-- SQL Server (histórico)
VentaID, FechaVenta, Monto

-- PostgreSQL (actual)
ventaid, fechaventa, monto
```

#### Ministerio Desarrollo Humano
```sql
-- PostgreSQL (histórico)
credito_id, anio, mes, beneficiario, monto, estado, fecha_registro

-- SQL Server (actual)
CreditoID, Anio, Mes, Beneficiario, Monto, Estado, FechaRegistro
```

### 🔧 Funciones Principales

#### Laboratorio de Ventas
```python
insert_venta(venta_id, fecha_venta, monto)
consultar_todas_ventas()
imprimir_listado_consolidado(ventas)
```

#### Ministerio Desarrollo Humano
```python
insert_credito(credito_id, anio, mes, beneficiario, monto, estado)
consultar_todos_creditos()
imprimir_reporte_consolidado(creditos)
consultar_por_anio(anio)  # ← Función adicional
```

### ✅ Similitudes

Ambos proyectos comparten:
- ✅ Arquitectura de middleware Python
- ✅ Particionamiento lógico por criterio temporal
- ✅ Uso de motores heterogéneos
- ✅ Consultas unificadas
- ✅ Manejo de transacciones
- ✅ Validaciones de datos
- ✅ Reportes consolidados
- ✅ Documentación completa

### 🎓 Aprendizajes

#### Del Laboratorio de Ventas aprendemos:
- Migración gradual entre sistemas
- Mantener datos antiguos en sistema legacy
- Dirigir tráfico nuevo al sistema moderno

#### Del Ministerio aprendemos:
- Optimización de costos por tipo de dato
- Separación de cargas OLTP vs OLAP
- Usar motor correcto según caso de uso

### 📈 Casos de Uso Reales

**Patrón Laboratorio (legacy → moderno):**
- Migraciones de Oracle a PostgreSQL
- De SQL Server a MySQL
- De on-premise a cloud

**Patrón Ministerio (optimización por carga):**
- Data warehousing (histórico) + OLTP (actual)
- Archivado de datos antiguos
- Reducción de costos de licenciamiento

### 🔄 Conversión entre Proyectos

Para convertir un proyecto al otro, cambiar:

1. **Criterio de particionamiento:**
   ```python
   # Laboratorio → Ministerio
   if fecha.year < 2023:  # Cambiar a: if anio in [2022, 2023, 2024]:
   
   # Ministerio → Laboratorio
   if anio in [2022, 2023, 2024]:  # Cambiar a: if fecha.year < 2023:
   ```

2. **Destinos:**
   ```python
   # Laboratorio
   < 2023 → SQL Server
   ≥ 2023 → PostgreSQL
   
   # Ministerio (invertido)
   2022-2024 → PostgreSQL
   2025 → SQL Server
   ```

3. **Nombres de bases de datos y tablas**

### 📚 Conclusión

Ambos proyectos demuestran el mismo concepto (particionamiento lógico) pero con criterios diferentes, enseñando dos escenarios comunes en la industria:

1. **Migración tecnológica** (Laboratorio)
2. **Optimización operacional** (Ministerio)

Ambos son válidos y útiles según el contexto del negocio.

---

**Recomendación:** Estudia ambos proyectos para entender cómo el mismo patrón arquitectónico puede aplicarse de formas diferentes según las necesidades del negocio.
