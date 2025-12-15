# ============================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ============================================================
# pyodbc   : permite conectarse a SQL Server
# psycopg2 : permite conectarse a PostgreSQL
# date     : para manejar fechas en Python
import pyodbc
import psycopg2
from datetime import date


# ============================================================
# 2. CONEXIÓN A SQL SERVER (BASE DE DATOS LOCAL)
# ============================================================
# Se establece la conexión usando ODBC Driver 17
# autocommit = False permite manejar commit y rollback manualmente
conn_sqlserver = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=ParticionDBSQLServer;"
    "UID=sa;"
    "PWD=admin"
)
conn_sqlserver.autocommit = False


# ============================================================
# 3. CONEXIÓN A POSTGRESQL (BASE DE DATOS EN LA NUBE / SEGUNDO MOTOR)
# ============================================================
# Se establece la conexión a PostgreSQL
# El campo ventaid se asume autogenerado (SERIAL / IDENTITY)
conn_postgres = psycopg2.connect(
    dbname="particiondbpostgres",
    user="admin",
    password="admin",
    host="localhost",
    port=5432
)
conn_postgres.autocommit = False


# ============================================================
# 4. FUNCIÓN PARA INSERTAR VENTAS (PARTICIÓN HORIZONTAL)
# ============================================================
# Regla de partición:
# - Ventas con año < 2023  → SQL Server
# - Ventas con año >= 2023 → PostgreSQL
def insert_venta(venta_id, fecha_venta, monto):

    # ----------------------------
    # 4.1 Inserción en SQL Server
    # ----------------------------
    if fecha_venta.year < 2023:
        try:
            # Se abre cursor para ejecutar SQL
            with conn_sqlserver.cursor() as cur:
                cur.execute(
                    "INSERT INTO VentasSQLServer (VentaID, FechaVenta, Monto) "
                    "VALUES (?, ?, ?)",
                    venta_id, fecha_venta, monto
                )

            # Confirmación de la transacción
            conn_sqlserver.commit()

        except Exception:
            # Si ocurre un error, se revierte la transacción
            conn_sqlserver.rollback()
            raise

    # ----------------------------
    # 4.2 Inserción en PostgreSQL
    # ----------------------------
    else:
        try:
            with conn_postgres.cursor() as cur:
                cur.execute(
                    "INSERT INTO ventas_postgres (fechaventa, monto) "
                    "VALUES (%s, %s)",
                    (fecha_venta, monto)
                )

            # Confirmación de la transacción
            conn_postgres.commit()

        except Exception:
            # Reversión en caso de error
            conn_postgres.rollback()
            raise


# ============================================================
# 5. FUNCIÓN PARA CONSULTA DISTRIBUIDA
# ============================================================
# Obtiene registros desde ambas bases de datos
# y los unifica en una sola lista en Python
def select_ventas():
    ventas = []

    # ----------------------------
    # 5.1 Consulta en SQL Server
    # ----------------------------
    with conn_sqlserver.cursor() as cur:
        cur.execute(
            "SELECT VentaID, FechaVenta, Monto FROM VentasSQLServer"
        )
        ventas.extend(cur.fetchall())

    # ----------------------------
    # 5.2 Consulta en PostgreSQL
    # ----------------------------
    with conn_postgres.cursor() as cur:
        cur.execute(
            "SELECT ventaid, fechaventa, monto FROM ventas_postgres"
        )
        ventas.extend(cur.fetchall())

    return ventas


# ============================================================
# 6. PRUEBA DE INSERCIÓN
# ============================================================
# Venta del año 2022 → SQL Server
insert_venta(100, date(2022, 2, 15), 150.00)

# Venta del año 2023 → PostgreSQL
insert_venta(200, date(2023, 5, 20), 200.00)


# ============================================================
# 7. PRUEBA DE CONSULTA DISTRIBUIDA
# ============================================================
# Se muestran en consola los registros de ambos motores
for v in select_ventas():
    print(v)


# ============================================================
# 8. CIERRE DE CONEXIONES
# ============================================================
# Buenas prácticas: cerrar conexiones al finalizar
conn_sqlserver.close()
conn_postgres.close()
