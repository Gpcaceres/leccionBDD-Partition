# Particionamiento lógico entre PostgreSQL y SQL Server

Este ejemplo implementa la separación de datos históricos (2022-2024) y actuales (2025) usando motores heterogéneos mientras se mantiene la lógica de negocio consistente.

## Arquitectura
- **Histórico (2022-2024):** PostgreSQL (`ventas_historicas`).
- **Operacional (2025):** SQL Server (`VentasActuales`).
- **Regla de partición:** año < 2025 → PostgreSQL; año = 2025 → SQL Server.

## Estructura de tablas sugerida
```sql
-- PostgreSQL
CREATE TABLE ventas_historicas (
    venta_id SERIAL PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    monto NUMERIC(12, 2) NOT NULL CHECK (monto > 0)
);

-- SQL Server
CREATE TABLE VentasActuales (
    VentaID INT IDENTITY(1,1) PRIMARY KEY,
    FechaVenta DATE NOT NULL,
    Monto DECIMAL(12,2) NOT NULL CHECK (Monto > 0)
);
```

## Uso
1. Configure las variables de entorno para ambos motores (host, puerto, base de datos y credenciales).
2. Ejecute el módulo para insertar y leer datos distribuidos:

```bash
python partition_manager.py
```

## Flujo principal
1. `PartitionManager.insert_sale` valida reglas comunes (monto > 0 y año dentro de 2022-2025).
2. Redirige la escritura al motor correcto según el año.
3. Confirma la transacción o ejecuta rollback ante errores.
4. `PartitionManager.fetch_sales` unifica resultados de ambas bases para exponer un único dataset.
