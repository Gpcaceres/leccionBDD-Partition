"""
Solución de particionamiento lógico para separar datos históricos y actuales
entre PostgreSQL (histórico: 2022-2024) y SQL Server (activo: 2025).

El módulo expone utilidades para:
- Validar reglas de negocio comunes antes de insertar.
- Dirigir escrituras según el año de la venta.
- Unificar consultas de ambos motores.

Las conexiones se parametrizan vía variables de entorno para evitar credenciales
fijas en el código:
- POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
- SQLSERVER_HOST, SQLSERVER_DB, SQLSERVER_USER, SQLSERVER_PASSWORD

Tablas esperadas:
- PostgreSQL: ventas_historicas(venta_id SERIAL PRIMARY KEY, fecha_venta DATE NOT NULL, monto NUMERIC(12,2) NOT NULL)
- SQL Server: VentasActuales(VentaID INT IDENTITY(1,1) PRIMARY KEY, FechaVenta DATE NOT NULL, Monto DECIMAL(12,2) NOT NULL)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Tuple

import psycopg2
import pyodbc


@dataclass
class DBConfig:
    """Parámetros de conexión para ambos motores."""

    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "particiondbpostgres")
    postgres_user: str = os.getenv("POSTGRES_USER", "admin")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "admin")

    sqlserver_host: str = os.getenv("SQLSERVER_HOST", "localhost")
    sqlserver_db: str = os.getenv("SQLSERVER_DB", "ParticionDBSQLServer")
    sqlserver_user: str = os.getenv("SQLSERVER_USER", "sa")
    sqlserver_password: str = os.getenv("SQLSERVER_PASSWORD", "admin")


def get_postgres_connection(config: DBConfig) -> psycopg2.extensions.connection:
    """Crea una conexión a PostgreSQL."""

    conn = psycopg2.connect(
        dbname=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
        host=config.postgres_host,
        port=config.postgres_port,
    )
    conn.autocommit = False
    return conn


def get_sqlserver_connection(config: DBConfig) -> pyodbc.Connection:
    """Crea una conexión a SQL Server usando ODBC Driver 17."""

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={config.sqlserver_host};"
        f"DATABASE={config.sqlserver_db};"
        f"UID={config.sqlserver_user};"
        f"PWD={config.sqlserver_password}"
    )
    conn.autocommit = False
    return conn


class PartitionManager:
    """Coordina operaciones distribuidas entre PostgreSQL y SQL Server."""

    def __init__(
        self,
        config: DBConfig | None = None,
        postgres_conn: psycopg2.extensions.connection | None = None,
        sqlserver_conn: pyodbc.Connection | None = None,
    ) -> None:
        self.config = config or DBConfig()
        self.postgres_conn = postgres_conn or get_postgres_connection(self.config)
        self.sqlserver_conn = sqlserver_conn or get_sqlserver_connection(self.config)

    def _validate_sale(self, sale_date: date, amount: float) -> None:
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        if sale_date.year not in {2022, 2023, 2024, 2025}:
            raise ValueError("El año de la venta debe estar entre 2022 y 2025")

    def insert_sale(self, sale_date: date, amount: float) -> None:
        """Inserta una venta en la base correcta según el año.

        Regla:
        - 2022, 2023, 2024 -> PostgreSQL (histórico)
        - 2025             -> SQL Server (operacional)
        """

        self._validate_sale(sale_date, amount)

        if sale_date.year < 2025:
            self._insert_postgres_sale(sale_date, amount)
        else:
            self._insert_sqlserver_sale(sale_date, amount)

    def _insert_postgres_sale(self, sale_date: date, amount: float) -> None:
        try:
            with self.postgres_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO ventas_historicas (fecha_venta, monto) VALUES (%s, %s)",
                    (sale_date, amount),
                )
            self.postgres_conn.commit()
        except Exception:
            self.postgres_conn.rollback()
            raise

    def _insert_sqlserver_sale(self, sale_date: date, amount: float) -> None:
        try:
            with self.sqlserver_conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO VentasActuales (FechaVenta, Monto) VALUES (?, ?)",
                    sale_date,
                    amount,
                )
            self.sqlserver_conn.commit()
        except Exception:
            self.sqlserver_conn.rollback()
            raise

    def fetch_sales(self) -> List[Tuple]:
        """Consulta unificada de ventas históricas y actuales."""

        sales: List[Tuple] = []
        with self.sqlserver_conn.cursor() as cur:
            cur.execute("SELECT VentaID, FechaVenta, Monto FROM VentasActuales")
            sales.extend(cur.fetchall())

        with self.postgres_conn.cursor() as cur:
            cur.execute("SELECT venta_id, fecha_venta, monto FROM ventas_historicas")
            sales.extend(cur.fetchall())

        return sales

    def close(self) -> None:
        """Cierra ambas conexiones."""

        for conn in (self.postgres_conn, self.sqlserver_conn):
            try:
                conn.close()
            except Exception:
                pass

    def __enter__(self) -> "PartitionManager":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def demo() -> Iterable[Tuple]:
    """Ejecuta una demostración insertando datos de ambos rangos."""

    manager = PartitionManager()
    manager.insert_sale(date(2024, 12, 31), 1500.0)
    manager.insert_sale(date(2025, 1, 15), 2500.0)
    sales = manager.fetch_sales()
    manager.close()
    return sales


if __name__ == "__main__":
    for venta in demo():
        print(venta)
