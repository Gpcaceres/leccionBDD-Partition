"""
============================================================
MIDDLEWARE DE PARTICIONAMIENTO - MINISTERIO DE DESARROLLO HUMANO
============================================================

Sistema de gestión de créditos de desarrollo humano con 
particionamiento de datos según criterio temporal:

  • Histórico (2022, 2023, 2024): almacenado en PostgreSQL
  • Actual (2025): almacenado en SQL Server

ESTRUCTURA REAL DE DATOS:
- 234,513 registros de créditos de bono de desarrollo
- 16 campos: género, edad, etnia, zona, provincia, cantón, etc.
- Datos provenientes de dump bonoleccion.sql

Autor: Sistema de Middleware Heterogéneo
Fecha: Diciembre 2024
============================================================
"""

import psycopg2
import pyodbc
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# ============================================================
# CONFIGURACIÓN DE CONEXIONES
# ============================================================

# PostgreSQL - Base de Datos Histórica
CONFIG_POSTGRESQL = {
    'dbname': 'mdh_historico',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

# SQL Server - Base de Datos Operacional
CONFIG_SQLSERVER = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MDH_Operacional;"
    "UID=sa;"
    "PWD=admin123;"
)

# ============================================================
# FUNCIONES DE INSERCIÓN
# ============================================================

def insert_credito(genero: str, edad: int, etnia: str, zona: str, 
                  distrito_mies: str, provincia: str, canton: str,
                  parroquia: str, tipo_zona: str, tipo_credito: str,
                  tipo_actividad: str, actividad: str, numero_cdh: int,
                  tipo_subsidio: str, cdh_activos: int, anio: int) -> bool:
    """
    Inserta un registro de crédito en la base de datos correspondiente
    según el año:
    
    - Años 2022-2024: PostgreSQL (histórico)
    - Año 2025: SQL Server (actual)
    
    Returns:
        bool: True si la inserción fue exitosa, False en caso contrario
    """
    
    try:
        # Decidir destino según el año
        if anio in [2022, 2023, 2024]:
            # Insertar en PostgreSQL (histórico)
            conn = psycopg2.connect(**CONFIG_POSTGRESQL)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO creditos_historicos 
                (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
                 parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                 numero_cdh, tipo_subsidio, cdh_activos, anio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (genero, edad, etnia, zona, distrito_mies, provincia, canton,
                  parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                  numero_cdh, tipo_subsidio, cdh_activos, anio))
            
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✓ Crédito {anio} insertado en PostgreSQL (histórico)")
            return True
            
        elif anio == 2025:
            # Insertar en SQL Server (actual)
            conn = pyodbc.connect(CONFIG_SQLSERVER)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO CreditosActuales 
                (genero, edad, etnia, zona, distrito_mies, provincia, canton, 
                 parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                 numero_cdh, tipo_subsidio, cdh_activos, anio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (genero, edad, etnia, zona, distrito_mies, provincia, canton,
                  parroquia, tipo_zona, tipo_credito, tipo_actividad, actividad,
                  numero_cdh, tipo_subsidio, cdh_activos, anio))
            
            conn.commit()
            cursor.close()
            conn.close()
            print(f"✓ Crédito {anio} insertado en SQL Server (actual)")
            return True
        else:
            print(f"✗ Año {anio} no válido. Debe ser 2022-2025.")
            return False
            
    except Exception as e:
        print(f"✗ Error insertando crédito: {e}")
        return False

# ============================================================
# FUNCIONES DE CONSULTA
# ============================================================

def consultar_todos_creditos() -> List[Dict]:
    """
    Consulta todos los créditos desde ambas bases de datos
    y los devuelve en una lista consolidada.
    
    Returns:
        List[Dict]: Lista de diccionarios con los datos de todos los créditos
    """
    
    creditos = []
    
    try:
        # Consultar PostgreSQL (histórico 2022-2024)
        conn_pg = psycopg2.connect(**CONFIG_POSTGRESQL)
        cursor_pg = conn_pg.cursor()
        
        cursor_pg.execute("""
            SELECT id, genero, edad, etnia, zona, distrito_mies, provincia, 
                   canton, parroquia, tipo_zona, tipo_credito, tipo_actividad,
                   actividad, numero_cdh, tipo_subsidio, cdh_activos, anio,
                   fecha_migracion
            FROM creditos_historicos
            ORDER BY anio, id
        """)
        
        for row in cursor_pg.fetchall():
            creditos.append({
                'id': row[0],
                'genero': row[1],
                'edad': row[2],
                'etnia': row[3],
                'zona': row[4],
                'distrito_mies': row[5],
                'provincia': row[6],
                'canton': row[7],
                'parroquia': row[8],
                'tipo_zona': row[9],
                'tipo_credito': row[10],
                'tipo_actividad': row[11],
                'actividad': row[12],
                'numero_cdh': row[13],
                'tipo_subsidio': row[14],
                'cdh_activos': row[15],
                'anio': row[16],
                'fecha_migracion': row[17],
                'origen': 'PostgreSQL (Histórico)'
            })
        
        cursor_pg.close()
        conn_pg.close()
        
        # Consultar SQL Server (actual 2025)
        conn_sql = pyodbc.connect(CONFIG_SQLSERVER)
        cursor_sql = conn_sql.cursor()
        
        cursor_sql.execute("""
            SELECT id, genero, edad, etnia, zona, distrito_mies, provincia, 
                   canton, parroquia, tipo_zona, tipo_credito, tipo_actividad,
                   actividad, numero_cdh, tipo_subsidio, cdh_activos, anio,
                   fecha_migracion
            FROM CreditosActuales
            ORDER BY anio, id
        """)
        
        for row in cursor_sql.fetchall():
            creditos.append({
                'id': row[0],
                'genero': row[1],
                'edad': row[2],
                'etnia': row[3],
                'zona': row[4],
                'distrito_mies': row[5],
                'provincia': row[6],
                'canton': row[7],
                'parroquia': row[8],
                'tipo_zona': row[9],
                'tipo_credito': row[10],
                'tipo_actividad': row[11],
                'actividad': row[12],
                'numero_cdh': row[13],
                'tipo_subsidio': row[14],
                'cdh_activos': row[15],
                'anio': row[16],
                'fecha_migracion': row[17],
                'origen': 'SQL Server (Actual)'
            })
        
        cursor_sql.close()
        conn_sql.close()
        
        return creditos
        
    except Exception as e:
        print(f"✗ Error consultando créditos: {e}")
        return creditos

def consultar_por_anio(anio: int) -> List[Dict]:
    """
    Consulta créditos de un año específico.
    
    Args:
        anio: Año a consultar (2022-2025)
    
    Returns:
        List[Dict]: Lista de créditos del año especificado
    """
    
    creditos = []
    
    try:
        if anio in [2022, 2023, 2024]:
            # Consultar en PostgreSQL
            conn = psycopg2.connect(**CONFIG_POSTGRESQL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, genero, edad, provincia, tipo_credito, tipo_subsidio, 
                       cdh_activos, anio
                FROM creditos_historicos
                WHERE anio = %s
                ORDER BY id
            """, (anio,))
            
            for row in cursor.fetchall():
                creditos.append({
                    'id': row[0],
                    'genero': row[1],
                    'edad': row[2],
                    'provincia': row[3],
                    'tipo_credito': row[4],
                    'tipo_subsidio': row[5],
                    'cdh_activos': row[6],
                    'anio': row[7],
                    'origen': 'PostgreSQL'
                })
            
            cursor.close()
            conn.close()
            
        elif anio == 2025:
            # Consultar en SQL Server
            conn = pyodbc.connect(CONFIG_SQLSERVER)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, genero, edad, provincia, tipo_credito, tipo_subsidio, 
                       cdh_activos, anio
                FROM CreditosActuales
                WHERE anio = ?
                ORDER BY id
            """, (anio,))
            
            for row in cursor.fetchall():
                creditos.append({
                    'id': row[0],
                    'genero': row[1],
                    'edad': row[2],
                    'provincia': row[3],
                    'tipo_credito': row[4],
                    'tipo_subsidio': row[5],
                    'cdh_activos': row[6],
                    'anio': row[7],
                    'origen': 'SQL Server'
                })
            
            cursor.close()
            conn.close()
        
        return creditos
        
    except Exception as e:
        print(f"✗ Error consultando año {anio}: {e}")
        return creditos

def obtener_estadisticas_por_provincia() -> Dict:
    """
    Obtiene estadísticas de créditos agrupados por provincia.
    
    Returns:
        Dict: Diccionario con provincias y sus totales
    """
    
    stats = {}
    
    try:
        # PostgreSQL (histórico)
        conn_pg = psycopg2.connect(**CONFIG_POSTGRESQL)
        cursor_pg = conn_pg.cursor()
        
        cursor_pg.execute("""
            SELECT provincia, COUNT(*) as total, SUM(cdh_activos) as total_activos
            FROM creditos_historicos
            GROUP BY provincia
            ORDER BY total DESC
        """)
        
        for row in cursor_pg.fetchall():
            provincia = row[0]
            if provincia not in stats:
                stats[provincia] = {'historico': 0, 'actual': 0, 'total_activos': 0}
            stats[provincia]['historico'] = row[1]
            stats[provincia]['total_activos'] += row[2] or 0
        
        cursor_pg.close()
        conn_pg.close()
        
        # SQL Server (actual)
        conn_sql = pyodbc.connect(CONFIG_SQLSERVER)
        cursor_sql = conn_sql.cursor()
        
        cursor_sql.execute("""
            SELECT provincia, COUNT(*) as total, SUM(cdh_activos) as total_activos
            FROM CreditosActuales
            GROUP BY provincia
        """)
        
        for row in cursor_sql.fetchall():
            provincia = row[0]
            if provincia not in stats:
                stats[provincia] = {'historico': 0, 'actual': 0, 'total_activos': 0}
            stats[provincia]['actual'] = row[1]
            stats[provincia]['total_activos'] += row[2] or 0
        
        cursor_sql.close()
        conn_sql.close()
        
        return stats
        
    except Exception as e:
        print(f"✗ Error obteniendo estadísticas: {e}")
        return stats

# ============================================================
# FUNCIONES DE REPORTE
# ============================================================

def imprimir_reporte_consolidado():
    """
    Imprime un reporte consolidado de todos los créditos
    """
    
    print("\n" + "="*100)
    print("REPORTE CONSOLIDADO - CRÉDITOS DE DESARROLLO HUMANO")
    print("="*100)
    
    # Obtener estadísticas generales
    try:
        conn_pg = psycopg2.connect(**CONFIG_POSTGRESQL)
        cursor_pg = conn_pg.cursor()
        cursor_pg.execute("SELECT COUNT(*), SUM(cdh_activos) FROM creditos_historicos")
        total_historico, activos_historico = cursor_pg.fetchone()
        cursor_pg.close()
        conn_pg.close()
        
        conn_sql = pyodbc.connect(CONFIG_SQLSERVER)
        cursor_sql = conn_sql.cursor()
        cursor_sql.execute("SELECT COUNT(*), SUM(cdh_activos) FROM CreditosActuales")
        total_actual, activos_actual = cursor_sql.fetchone()
        cursor_sql.close()
        conn_sql.close()
        
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"  • Histórico (2022-2024) en PostgreSQL: {total_historico:,} créditos")
        print(f"  • Actual (2025) en SQL Server:        {total_actual:,} créditos")
        print(f"  • TOTAL:                              {total_historico + total_actual:,} créditos")
        print(f"  • CDH activos históricos:             {activos_historico or 0:,}")
        print(f"  • CDH activos actuales:               {activos_actual or 0:,}")
        
        # Estadísticas por provincia
        print(f"\n📍 TOP 10 PROVINCIAS:")
        stats = obtener_estadisticas_por_provincia()
        sorted_provinces = sorted(stats.items(), 
                                 key=lambda x: x[1]['historico'] + x[1]['actual'], 
                                 reverse=True)[:10]
        
        print(f"  {'Provincia':<30} {'Histórico':>12} {'Actual':>12} {'Total':>12}")
        print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12}")
        
        for provincia, datos in sorted_provinces:
            total = datos['historico'] + datos['actual']
            print(f"  {provincia:<30} {datos['historico']:>12,} {datos['actual']:>12,} {total:>12,}")
        
        print("\n" + "="*100)
        
    except Exception as e:
        print(f"\n✗ Error generando reporte: {e}")

def imprimir_reporte_anual(anio: int):
    """
    Imprime un reporte detallado de un año específico
    """
    
    print(f"\n{'='*100}")
    print(f"REPORTE AÑO {anio}")
    print(f"{'='*100}")
    
    creditos = consultar_por_anio(anio)
    
    if not creditos:
        print(f"\nNo hay registros para el año {anio}")
        return
    
    print(f"\nTotal de créditos: {len(creditos):,}")
    print(f"Base de datos: {creditos[0]['origen']}")
    
    # Estadísticas de género
    femenino = sum(1 for c in creditos if c['genero'] == 'FEMENINO')
    masculino = sum(1 for c in creditos if c['genero'] == 'MASCULINO')
    
    print(f"\n👥 Distribución por género:")
    print(f"  • Femenino: {femenino:,} ({femenino/len(creditos)*100:.1f}%)")
    print(f"  • Masculino: {masculino:,} ({masculino/len(creditos)*100:.1f}%)")
    
    # Primeros 5 registros
    print(f"\n📋 Primeros 5 registros:")
    print(f"  {'ID':<8} {'Género':<12} {'Edad':<6} {'Provincia':<20} {'Tipo Crédito':<20}")
    print(f"  {'-'*8} {'-'*12} {'-'*6} {'-'*20} {'-'*20}")
    
    for credito in creditos[:5]:
        print(f"  {credito['id']:<8} {credito['genero']:<12} {credito['edad']:<6} "
              f"{credito['provincia']:<20} {credito['tipo_credito']:<20}")
    
    print(f"\n{'='*100}")

# ============================================================
# MENÚ INTERACTIVO
# ============================================================

def mostrar_menu():
    """Muestra el menú principal del sistema"""
    
    while True:
        print("\n" + "="*80)
        print("SISTEMA DE GESTIÓN DE CRÉDITOS - MINISTERIO DE DESARROLLO HUMANO")
        print("="*80)
        print("\n1. Insertar nuevo crédito")
        print("2. Consultar todos los créditos")
        print("3. Consultar créditos por año")
        print("4. Ver reporte consolidado")
        print("5. Ver reporte de un año específico")
        print("6. Estadísticas por provincia")
        print("0. Salir")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            print("\n--- INSERTAR NUEVO CRÉDITO ---")
            try:
                genero = input("Género (FEMENINO/MASCULINO): ")
                edad = int(input("Edad: "))
                etnia = input("Etnia: ")
                zona = input("Zona: ")
                distrito_mies = input("Distrito MIES: ")
                provincia = input("Provincia: ")
                canton = input("Cantón: ")
                parroquia = input("Parroquia: ")
                tipo_zona = input("Tipo zona (URBANA/RURAL): ")
                tipo_credito = input("Tipo crédito: ")
                tipo_actividad = input("Tipo actividad: ")
                actividad = input("Actividad: ")
                numero_cdh = int(input("Número CDH: "))
                tipo_subsidio = input("Tipo subsidio: ")
                cdh_activos = int(input("CDH activos: "))
                anio = int(input("Año (2022-2025): "))
                
                insert_credito(genero, edad, etnia, zona, distrito_mies, provincia,
                             canton, parroquia, tipo_zona, tipo_credito, tipo_actividad,
                             actividad, numero_cdh, tipo_subsidio, cdh_activos, anio)
            except ValueError:
                print("✗ Error: valores numéricos inválidos")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        elif opcion == "2":
            print("\n--- CONSULTANDO TODOS LOS CRÉDITOS ---")
            creditos = consultar_todos_creditos()
            print(f"\nTotal encontrado: {len(creditos):,} créditos")
            if creditos:
                print(f"\nPrimeros 10 registros:")
                for i, c in enumerate(creditos[:10], 1):
                    print(f"{i}. Año {c['anio']} - {c['genero']} - "
                          f"{c['provincia']} - {c['tipo_credito']} [{c['origen']}]")
        
        elif opcion == "3":
            try:
                anio = int(input("\nAño a consultar (2022-2025): "))
                creditos = consultar_por_anio(anio)
                print(f"\nCréditos del año {anio}: {len(creditos):,}")
                if creditos:
                    print(f"\nPrimeros 10 registros:")
                    for i, c in enumerate(creditos[:10], 1):
                        print(f"{i}. {c['genero']} - {c['provincia']} - {c['tipo_credito']}")
            except ValueError:
                print("✗ Año inválido")
        
        elif opcion == "4":
            imprimir_reporte_consolidado()
        
        elif opcion == "5":
            try:
                anio = int(input("\nAño del reporte (2022-2025): "))
                imprimir_reporte_anual(anio)
            except ValueError:
                print("✗ Año inválido")
        
        elif opcion == "6":
            print("\n--- ESTADÍSTICAS POR PROVINCIA ---")
            stats = obtener_estadisticas_por_provincia()
            if stats:
                sorted_provinces = sorted(stats.items(), 
                                         key=lambda x: x[1]['historico'] + x[1]['actual'], 
                                         reverse=True)
                
                print(f"\n{'Provincia':<30} {'Histórico':>12} {'Actual':>12} {'Total':>12}")
                print(f"{'-'*30} {'-'*12} {'-'*12} {'-'*12}")
                
                for provincia, datos in sorted_provinces:
                    total = datos['historico'] + datos['actual']
                    print(f"{provincia:<30} {datos['historico']:>12,} {datos['actual']:>12,} {total:>12,}")
        
        elif opcion == "0":
            print("\n¡Hasta pronto!")
            break
        
        else:
            print("\n✗ Opción no válida")

# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   SISTEMA DE MIDDLEWARE - MINISTERIO DE DESARROLLO HUMANO    ║
    ║                                                              ║
    ║   Particionamiento de datos reales:                          ║
    ║   • PostgreSQL: 2022-2024 (Histórico)                        ║
    ║   • SQL Server: 2025 (Actual)                                ║
    ║                                                              ║
    ║   Total: 234,513 registros de créditos                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    mostrar_menu()
