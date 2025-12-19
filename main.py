# ============================================================
# MIDDLEWARE DE PARTICIONAMIENTO - MINISTERIO DESARROLLO HUMANO
# Sistema de Gestión de Créditos de Desarrollo Humano
# ============================================================
# 
# Criterio de Particionamiento:
# - Datos HISTÓRICOS (2022, 2023, 2024) → PostgreSQL
# - Datos ACTUALES (2025) → SQL Server
# ============================================================

import pyodbc
import psycopg2
from datetime import date


# ============================================================
# 1. CONEXIÓN A POSTGRESQL (REPOSITORIO HISTÓRICO)
# ============================================================
# Almacena datos históricos de los años 2022, 2023 y 2024
conn_postgres = psycopg2.connect(
    dbname="mdh_historico",
    user="postgres",
    password="admin",  # Cambiar por tu contraseña
    host="localhost",
    port=5432
)
conn_postgres.autocommit = False


# ============================================================
# 2. CONEXIÓN A SQL SERVER (REPOSITORIO OPERACIONAL)
# ============================================================
# Almacena datos actuales del año 2025
conn_sqlserver = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MDH_Operacional;"
    "UID=sa;"
    "PWD=admin"  # Cambiar por tu contraseña
)
conn_sqlserver.autocommit = False


# ============================================================
# 3. FUNCIÓN insert_credito
# ============================================================
def insert_credito(credito_id, anio, mes, beneficiario, monto, estado="ACTIVO"):
    """
    Inserta un crédito en el repositorio correcto según su año.
    
    Parámetros:
    - credito_id: ID único del crédito (INT)
    - anio: Año del crédito (INT)
    - mes: Mes del crédito (INT 1-12)
    - beneficiario: Nombre del beneficiario (VARCHAR)
    - monto: Monto del crédito (DECIMAL)
    - estado: Estado del crédito (VARCHAR)
    
    Lógica de particionamiento:
    - Si año es 2022, 2023 o 2024: inserta en PostgreSQL (histórico)
    - Si año es 2025: inserta en SQL Server (operacional)
    """
    print(f"\n--- Insertando crédito ID={credito_id}, Año={anio}, Mes={mes}, "
          f"Beneficiario={beneficiario}, Monto=${monto:,.2f}, Estado={estado} ---")
    
    # Validar año
    if anio not in [2022, 2023, 2024, 2025]:
        print(f"✗ Error: El año {anio} no está en el rango válido (2022-2025)")
        return
    
    # Validar monto
    if monto <= 0:
        print(f"✗ Error: El monto debe ser mayor a 0")
        return
    
    # Decidir destino según el año
    if anio in [2022, 2023, 2024]:
        # Insertar en PostgreSQL (histórico)
        print(f"→ El año {anio} es HISTÓRICO (2022-2024) → Insertando en PostgreSQL")
        try:
            cursor_pg = conn_postgres.cursor()
            cursor_pg.execute(
                """INSERT INTO creditos_historicos 
                   (credito_id, anio, mes, beneficiario, monto, estado) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (credito_id, anio, mes, beneficiario, monto, estado)
            )
            conn_postgres.commit()
            print("✓ Insertado exitosamente en PostgreSQL (repositorio histórico)")
        except Exception as e:
            conn_postgres.rollback()
            print(f"✗ Error al insertar en PostgreSQL: {e}")
    
    elif anio == 2025:
        # Insertar en SQL Server (operacional)
        print(f"→ El año {anio} es ACTUAL (2025) → Insertando en SQL Server")
        try:
            cursor_sql = conn_sqlserver.cursor()
            cursor_sql.execute(
                """INSERT INTO CreditosActuales 
                   (CreditoID, Anio, Mes, Beneficiario, Monto, Estado) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                credito_id, anio, mes, beneficiario, monto, estado
            )
            conn_sqlserver.commit()
            print("✓ Insertado exitosamente en SQL Server (repositorio operacional)")
        except Exception as e:
            conn_sqlserver.rollback()
            print(f"✗ Error al insertar en SQL Server: {e}")


# ============================================================
# 4. FUNCIÓN consultar_todos_creditos
# ============================================================
def consultar_todos_creditos():
    """
    Consulta todos los créditos de ambos repositorios y los combina.
    Retorna una lista con todos los créditos ordenados por año y mes.
    """
    print("\n" + "="*80)
    print("CONSULTANDO TODOS LOS CRÉDITOS (HISTÓRICOS + ACTUALES)")
    print("="*80 + "\n")
    
    todos_los_creditos = []
    
    # Consultar PostgreSQL (créditos históricos 2022-2024)
    print("→ Consultando PostgreSQL (créditos históricos 2022-2024)...")
    try:
        cursor_pg = conn_postgres.cursor()
        cursor_pg.execute(
            """SELECT credito_id, anio, mes, beneficiario, monto, estado 
               FROM creditos_historicos 
               ORDER BY anio, mes"""
        )
        creditos_postgres = cursor_pg.fetchall()
        
        for credito in creditos_postgres:
            todos_los_creditos.append({
                'id': credito[0],
                'anio': credito[1],
                'mes': credito[2],
                'beneficiario': credito[3],
                'monto': float(credito[4]),
                'estado': credito[5],
                'origen': 'PostgreSQL (Histórico)'
            })
        print(f"✓ Encontrados {len(creditos_postgres)} créditos históricos en PostgreSQL")
    except Exception as e:
        print(f"✗ Error al consultar PostgreSQL: {e}")
    
    # Consultar SQL Server (créditos actuales 2025)
    print("→ Consultando SQL Server (créditos actuales 2025)...")
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_sql.execute(
            """SELECT CreditoID, Anio, Mes, Beneficiario, Monto, Estado 
               FROM CreditosActuales 
               ORDER BY Anio, Mes"""
        )
        creditos_sqlserver = cursor_sql.fetchall()
        
        for credito in creditos_sqlserver:
            todos_los_creditos.append({
                'id': credito[0],
                'anio': credito[1],
                'mes': credito[2],
                'beneficiario': credito[3],
                'monto': float(credito[4]),
                'estado': credito[5],
                'origen': 'SQL Server (Actual)'
            })
        print(f"✓ Encontrados {len(creditos_sqlserver)} créditos actuales en SQL Server")
    except Exception as e:
        print(f"✗ Error al consultar SQL Server: {e}")
    
    # Ordenar por año y mes
    todos_los_creditos.sort(key=lambda x: (x['anio'], x['mes']))
    
    return todos_los_creditos


# ============================================================
# 5. FUNCIÓN imprimir_reporte_consolidado
# ============================================================
def imprimir_reporte_consolidado(creditos):
    """
    Imprime un reporte consolidado de todos los créditos.
    """
    print("\n" + "="*100)
    print(" "*30 + "REPORTE CONSOLIDADO DE CRÉDITOS")
    print(" "*25 + "MINISTERIO DE DESARROLLO HUMANO")
    print("="*100)
    print(f"{'ID':<8} {'AÑO':<6} {'MES':<5} {'BENEFICIARIO':<30} {'MONTO':<15} {'ESTADO':<12} {'ORIGEN':<25}")
    print("-"*100)
    
    total_monto = 0.0
    totales_por_anio = {}
    
    for credito in creditos:
        print(f"{credito['id']:<8} {credito['anio']:<6} {credito['mes']:<5} "
              f"{credito['beneficiario']:<30} ${credito['monto']:<14,.2f} "
              f"{credito['estado']:<12} {credito['origen']:<25}")
        
        total_monto += credito['monto']
        
        # Acumular por año
        anio = credito['anio']
        if anio not in totales_por_anio:
            totales_por_anio[anio] = 0.0
        totales_por_anio[anio] += credito['monto']
    
    print("-"*100)
    print(f"\n{'RESUMEN POR AÑO:':<50}")
    print("-"*50)
    for anio in sorted(totales_por_anio.keys()):
        origen = "PostgreSQL (Histórico)" if anio < 2025 else "SQL Server (Actual)"
        print(f"  Año {anio}: ${totales_por_anio[anio]:>15,.2f}  ({origen})")
    
    print("-"*50)
    print(f"{'TOTAL GENERAL:':<30} ${total_monto:>15,.2f}")
    print(f"{'CANTIDAD DE CRÉDITOS:':<30} {len(creditos):>15}")
    print("="*100 + "\n")


# ============================================================
# 6. FUNCIÓN consultar_por_anio
# ============================================================
def consultar_por_anio(anio):
    """
    Consulta créditos de un año específico del repositorio correcto.
    """
    print(f"\n→ Consultando créditos del año {anio}...")
    
    if anio in [2022, 2023, 2024]:
        # Consultar PostgreSQL
        try:
            cursor_pg = conn_postgres.cursor()
            cursor_pg.execute(
                """SELECT credito_id, anio, mes, beneficiario, monto, estado 
                   FROM creditos_historicos 
                   WHERE anio = %s
                   ORDER BY mes""",
                (anio,)
            )
            resultados = cursor_pg.fetchall()
            print(f"✓ Encontrados {len(resultados)} créditos en PostgreSQL")
            return resultados
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    elif anio == 2025:
        # Consultar SQL Server
        try:
            cursor_sql = conn_sqlserver.cursor()
            cursor_sql.execute(
                """SELECT CreditoID, Anio, Mes, Beneficiario, Monto, Estado 
                   FROM CreditosActuales 
                   WHERE Anio = ?
                   ORDER BY Mes""",
                anio
            )
            resultados = cursor_sql.fetchall()
            print(f"✓ Encontrados {len(resultados)} créditos en SQL Server")
            return resultados
        except Exception as e:
            print(f"✗ Error: {e}")
            return []


# ============================================================
# 7. PROGRAMA PRINCIPAL
# ============================================================
if __name__ == "__main__":
    print("\n" + "="*100)
    print(" "*25 + "SISTEMA DE GESTIÓN DE CRÉDITOS DE DESARROLLO HUMANO")
    print(" "*30 + "MINISTERIO DE DESARROLLO HUMANO")
    print("="*100)
    print("\nEstrategia de Particionamiento Lógico:")
    print("  • Datos HISTÓRICOS (2022, 2023, 2024) → PostgreSQL (repositorio histórico)")
    print("  • Datos ACTUALES (2025) → SQL Server (repositorio operacional)")
    print("="*100)
    
    # Insertar créditos de prueba
    print("\n" + "="*100)
    print(" "*35 + "INSERTANDO CRÉDITOS DE PRUEBA")
    print("="*100)
    
    # Créditos históricos (2022-2024 → PostgreSQL)
    insert_credito(1001, 2022, 3, "Juan Pérez González", 1500.00, "ACTIVO")
    insert_credito(1002, 2022, 7, "María López Rodríguez", 2000.00, "ACTIVO")
    insert_credito(1003, 2023, 1, "Carlos Martínez Díaz", 1800.50, "ACTIVO")
    insert_credito(1004, 2023, 6, "Ana García Fernández", 2200.75, "ACTIVO")
    insert_credito(1005, 2023, 12, "Luis Sánchez Morales", 1650.00, "ACTIVO")
    insert_credito(1006, 2024, 2, "Carmen Ruiz Castro", 1900.25, "ACTIVO")
    insert_credito(1007, 2024, 8, "Pedro Ramírez Torres", 2100.00, "ACTIVO")
    insert_credito(1008, 2024, 11, "Isabel Flores Vargas", 1750.50, "ACTIVO")
    
    # Créditos actuales (2025 → SQL Server)
    insert_credito(2001, 2025, 1, "Jorge Herrera Medina", 2500.00, "ACTIVO")
    insert_credito(2002, 2025, 2, "Laura Jiménez Ortiz", 2300.75, "ACTIVO")
    insert_credito(2003, 2025, 3, "Roberto Silva Mendoza", 2800.00, "ACTIVO")
    insert_credito(2004, 2025, 4, "Patricia Cruz Navarro", 2150.50, "ACTIVO")
    
    # Consultar todos los créditos
    todos_los_creditos = consultar_todos_creditos()
    
    # Imprimir reporte consolidado
    imprimir_reporte_consolidado(todos_los_creditos)


# ============================================================
# 8. CIERRE DE CONEXIONES
# ============================================================
print("\n→ Cerrando conexiones...")
conn_postgres.close()
conn_sqlserver.close()
print("✓ Conexiones cerradas correctamente\n")
