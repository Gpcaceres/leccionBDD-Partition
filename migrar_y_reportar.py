"""
MIGRACIÓN Y REPORTE AUTOMÁTICO
Migra los datos de bonoleccion y muestra el reporte consolidado
"""

import psycopg2
import pyodbc
from datetime import datetime

# ============================================================
# CONFIGURACIÓN
# ============================================================

CONFIG_BONOLECCION = {
    'dbname': 'bonoleccion',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

CONFIG_PG_HISTORICO = {
    'dbname': 'mdh_historico',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

CONFIG_SQL_ACTUAL = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MDH_Operacional;"
    "UID=sa;"
    "PWD=admin;"
)

# ============================================================
# FUNCIONES
# ============================================================

def conectar_postgresql(config):
    try:
        conn = psycopg2.connect(**config)
        return conn
    except Exception as e:
        print(f"✗ Error conectando a PostgreSQL: {e}")
        return None

def conectar_sqlserver():
    try:
        conn = pyodbc.connect(CONFIG_SQL_ACTUAL)
        return conn
    except Exception as e:
        print(f"✗ Error conectando a SQL Server: {e}")
        return None

def crear_tabla_historica_pg(conn):
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS creditos_historicos CASCADE;")
    cursor.execute("""
        CREATE TABLE creditos_historicos (
            id SERIAL PRIMARY KEY,
            genero VARCHAR(20),
            edad INTEGER,
            etnia VARCHAR(50),
            zona VARCHAR(100),
            distrito_mies VARCHAR(100),
            provincia VARCHAR(50),
            canton VARCHAR(50),
            parroquia VARCHAR(100),
            tipo_zona VARCHAR(20),
            tipo_credito VARCHAR(50),
            tipo_actividad VARCHAR(200),
            actividad VARCHAR(300),
            numero_cdh INTEGER,
            tipo_subsidio VARCHAR(100),
            cdh_activos INTEGER,
            anio INTEGER,
            fecha_migracion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

def crear_tabla_actual_sql(conn):
    cursor = conn.cursor()
    cursor.execute("""
        IF OBJECT_ID('dbo.CreditosActuales', 'U') IS NOT NULL
            DROP TABLE dbo.CreditosActuales;
    """)
    cursor.execute("""
        CREATE TABLE CreditosActuales (
            id INT IDENTITY(1,1) PRIMARY KEY,
            genero VARCHAR(20),
            edad INT,
            etnia VARCHAR(50),
            zona VARCHAR(100),
            distrito_mies VARCHAR(100),
            provincia VARCHAR(50),
            canton VARCHAR(50),
            parroquia VARCHAR(100),
            tipo_zona VARCHAR(20),
            tipo_credito VARCHAR(50),
            tipo_actividad VARCHAR(200),
            actividad VARCHAR(300),
            numero_cdh INT,
            tipo_subsidio VARCHAR(100),
            cdh_activos INT,
            anio INT,
            fecha_migracion DATETIME DEFAULT GETDATE()
        );
    """)
    conn.commit()

def migrar_datos():
    print("\n" + "="*80)
    print("MIGRACIÓN DE DATOS REALES")
    print("="*80)
    
    # Conectar
    conn_fuente = conectar_postgresql(CONFIG_BONOLECCION)
    if not conn_fuente:
        return False
    
    conn_pg_historico = conectar_postgresql(CONFIG_PG_HISTORICO)
    if not conn_pg_historico:
        return False
    
    conn_sql_actual = conectar_sqlserver()
    if not conn_sql_actual:
        return False
    
    # Crear tablas
    print("\n→ Creando tablas...")
    crear_tabla_historica_pg(conn_pg_historico)
    crear_tabla_actual_sql(conn_sql_actual)
    
    # Estadísticas
    print("\n→ Analizando distribución...")
    cursor_fuente = conn_fuente.cursor()
    cursor_fuente.execute("""
        SELECT "AÑO", COUNT(*) as total
        FROM table1
        GROUP BY "AÑO"
        ORDER BY "AÑO";
    """)
    
    estadisticas = cursor_fuente.fetchall()
    for anio, total in estadisticas:
        destino = "PostgreSQL" if anio in [2022, 2023, 2024] else "SQL Server"
        print(f"  Año {anio}: {total:,} registros → {destino}")
    
    # Migrar históricos
    print("\n→ Migrando históricos (2022-2024)...")
    cursor_fuente.execute("""
        SELECT "Genero", "Edad", "Etnia", "Zona", "DistritoMies", 
               "Provincia", "Canton", "Parroquia", "TipoZona", "TipoCredito",
               "TipoActividad", "Actividad", "NumeroCDH", "TipoSubsidio",
               "CDH_ACTIVOS", "AÑO"
        FROM table1
        WHERE "AÑO" IN (2022, 2023, 2024)
    """)
    
    cursor_pg = conn_pg_historico.cursor()
    registros_historicos = 0
    batch = []
    
    for registro in cursor_fuente:
        batch.append(registro)
        if len(batch) >= 1000:
            cursor_pg.executemany("""
                INSERT INTO creditos_historicos 
                (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
                 parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                 numero_cdh, tipo_subsidio, cdh_activos, anio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, batch)
            conn_pg_historico.commit()
            registros_historicos += len(batch)
            print(f"  ✓ {registros_historicos:,} registros...", end='\r')
            batch = []
    
    if batch:
        cursor_pg.executemany("""
            INSERT INTO creditos_historicos 
            (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
             parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
             numero_cdh, tipo_subsidio, cdh_activos, anio)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, batch)
        conn_pg_historico.commit()
        registros_historicos += len(batch)
    
    print(f"\n  ✓ Total históricos: {registros_historicos:,}")
    
    # Migrar actuales
    print("\n→ Migrando actuales (2025)...")
    cursor_fuente.execute("""
        SELECT "Genero", "Edad", "Etnia", "Zona", "DistritoMies", 
               "Provincia", "Canton", "Parroquia", "TipoZona", "TipoCredito",
               "TipoActividad", "Actividad", "NumeroCDH", "TipoSubsidio",
               "CDH_ACTIVOS", "AÑO"
        FROM table1
        WHERE "AÑO" = 2025
    """)
    
    cursor_sql = conn_sql_actual.cursor()
    registros_actuales = 0
    batch = []
    
    for registro in cursor_fuente:
        batch.append(registro)
        if len(batch) >= 1000:
            cursor_sql.executemany("""
                INSERT INTO CreditosActuales 
                (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
                 parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                 numero_cdh, tipo_subsidio, cdh_activos, anio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            conn_sql_actual.commit()
            registros_actuales += len(batch)
            print(f"  ✓ {registros_actuales:,} registros...", end='\r')
            batch = []
    
    if batch:
        cursor_sql.executemany("""
            INSERT INTO CreditosActuales 
            (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
             parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
             numero_cdh, tipo_subsidio, cdh_activos, anio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        conn_sql_actual.commit()
        registros_actuales += len(batch)
    
    print(f"\n  ✓ Total actuales: {registros_actuales:,}")
    
    # Cerrar
    conn_fuente.close()
    conn_pg_historico.close()
    conn_sql_actual.close()
    
    print("\n✓ MIGRACIÓN COMPLETADA")
    return True

def generar_reporte():
    print("\n" + "="*100)
    print("REPORTE CONSOLIDADO - CRÉDITOS DE DESARROLLO HUMANO")
    print("="*100)
    
    try:
        # Conectar
        conn_pg = conectar_postgresql(CONFIG_PG_HISTORICO)
        conn_sql = conectar_sqlserver()
        
        if not conn_pg or not conn_sql:
            print("\n✗ No se pudo conectar a las bases de datos")
            return
        
        # Estadísticas generales
        cursor_pg = conn_pg.cursor()
        cursor_pg.execute("SELECT COUNT(*), SUM(cdh_activos) FROM creditos_historicos")
        total_historico, activos_historico = cursor_pg.fetchone()
        
        cursor_sql = conn_sql.cursor()
        cursor_sql.execute("SELECT COUNT(*), SUM(cdh_activos) FROM CreditosActuales")
        total_actual, activos_actual = cursor_sql.fetchone()
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"  • Histórico (2022-2024) en PostgreSQL: {total_historico:,} créditos")
        print(f"  • Actual (2025) en SQL Server:        {total_actual:,} créditos")
        print(f"  • TOTAL:                              {(total_historico + total_actual):,} créditos")
        print(f"  • CDH activos históricos:             {activos_historico or 0:,}")
        print(f"  • CDH activos actuales:               {activos_actual or 0:,}")
        
        # Top provincias
        print(f"\n📍 TOP 10 PROVINCIAS:")
        
        # PostgreSQL
        cursor_pg.execute("""
            SELECT provincia, COUNT(*) as total, SUM(cdh_activos) as activos
            FROM creditos_historicos
            GROUP BY provincia
            ORDER BY total DESC
        """)
        provincias_pg = {row[0]: {'historico': row[1], 'activos': row[2] or 0} for row in cursor_pg.fetchall()}
        
        # SQL Server
        cursor_sql.execute("""
            SELECT provincia, COUNT(*) as total, SUM(cdh_activos) as activos
            FROM CreditosActuales
            GROUP BY provincia
        """)
        provincias_sql = {row[0]: {'actual': row[1], 'activos': row[2] or 0} for row in cursor_sql.fetchall()}
        
        # Consolidar
        todas_provincias = {}
        for prov, datos in provincias_pg.items():
            todas_provincias[prov] = {'historico': datos['historico'], 'actual': 0, 'activos': datos['activos']}
        
        for prov, datos in provincias_sql.items():
            if prov in todas_provincias:
                todas_provincias[prov]['actual'] = datos['actual']
                todas_provincias[prov]['activos'] += datos['activos']
            else:
                todas_provincias[prov] = {'historico': 0, 'actual': datos['actual'], 'activos': datos['activos']}
        
        # Ordenar y mostrar top 10
        sorted_provinces = sorted(todas_provincias.items(), 
                                 key=lambda x: x[1]['historico'] + x[1]['actual'], 
                                 reverse=True)[:10]
        
        print(f"  {'Provincia':<30} {'Histórico':>12} {'Actual':>12} {'Total':>12} {'Activos':>12}")
        print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
        
        for provincia, datos in sorted_provinces:
            total = datos['historico'] + datos['actual']
            print(f"  {provincia:<30} {datos['historico']:>12,} {datos['actual']:>12,} {total:>12,} {datos['activos']:>12,}")
        
        # Distribución por año
        print(f"\n📅 DISTRIBUCIÓN POR AÑO:")
        cursor_pg.execute("""
            SELECT anio, COUNT(*) as total
            FROM creditos_historicos
            GROUP BY anio
            ORDER BY anio
        """)
        
        print(f"  {'Año':<10} {'Registros':>15} {'Base de Datos':<20}")
        print(f"  {'-'*10} {'-'*15} {'-'*20}")
        
        for anio, total in cursor_pg.fetchall():
            print(f"  {anio:<10} {total:>15,} {'PostgreSQL':<20}")
        
        cursor_sql.execute("""
            SELECT anio, COUNT(*) as total
            FROM CreditosActuales
            GROUP BY anio
        """)
        
        for anio, total in cursor_sql.fetchall():
            print(f"  {anio:<10} {total:>15,} {'SQL Server':<20}")
        
        # Distribución por género
        print(f"\n👥 DISTRIBUCIÓN POR GÉNERO:")
        
        cursor_pg.execute("""
            SELECT genero, COUNT(*) as total
            FROM creditos_historicos
            GROUP BY genero
        """)
        genero_pg = dict(cursor_pg.fetchall())
        
        cursor_sql.execute("""
            SELECT genero, COUNT(*) as total
            FROM CreditosActuales
            GROUP BY genero
        """)
        genero_sql = dict(cursor_sql.fetchall())
        
        total_general = total_historico + total_actual
        femenino_total = genero_pg.get('FEMENINO', 0) + genero_sql.get('FEMENINO', 0)
        masculino_total = genero_pg.get('MASCULINO', 0) + genero_sql.get('MASCULINO', 0)
        
        print(f"  • Femenino:  {femenino_total:>8,} ({femenino_total/total_general*100:.1f}%)")
        print(f"  • Masculino: {masculino_total:>8,} ({masculino_total/total_general*100:.1f}%)")
        
        # Top tipos de crédito
        print(f"\n💰 TOP 5 TIPOS DE CRÉDITO:")
        cursor_pg.execute("""
            SELECT tipo_credito, COUNT(*) as total
            FROM creditos_historicos
            GROUP BY tipo_credito
            ORDER BY total DESC
            LIMIT 5
        """)
        
        print(f"  {'Tipo de Crédito':<40} {'Total':>15}")
        print(f"  {'-'*40} {'-'*15}")
        
        for tipo, total in cursor_pg.fetchall():
            print(f"  {tipo:<40} {total:>15,}")
        
        print("\n" + "="*100)
        
        conn_pg.close()
        conn_sql.close()
        
    except Exception as e:
        print(f"\n✗ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    # Migrar datos
    if migrar_datos():
        # Generar reporte
        generar_reporte()
    else:
        print("\n✗ La migración falló")
