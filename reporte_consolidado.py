"""
REPORTE CONSOLIDADO - SOLO MUESTRA EL REPORTE
No requiere menú interactivo, solo genera el reporte consolidado
"""

import psycopg2
import pyodbc

CONFIG_PG = {
    'dbname': 'mdh_historico',
    'user': 'postgres',
    'password': 'admin',
    'host': 'localhost',
    'port': 5432
}

CONFIG_SQL = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=MDH_Operacional;"
    "UID=sa;"
    "PWD=admin;"
)

def generar_reporte():
    print("\n" + "="*100)
    print("REPORTE CONSOLIDADO - CRÉDITOS DE DESARROLLO HUMANO")
    print("="*100)
    
    try:
        # Conectar
        conn_pg = psycopg2.connect(**CONFIG_PG)
        conn_sql = pyodbc.connect(CONFIG_SQL)
        
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
        
        cursor_pg.execute("""
            SELECT provincia, COUNT(*) as total, SUM(cdh_activos) as activos
            FROM creditos_historicos
            GROUP BY provincia
            ORDER BY total DESC
        """)
        provincias_pg = {row[0]: {'historico': row[1], 'activos': row[2] or 0} for row in cursor_pg.fetchall()}
        
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
        
        # Top tipos de subsidio
        print(f"\n🏆 TOP 5 TIPOS DE SUBSIDIO:")
        cursor_pg.execute("""
            SELECT tipo_subsidio, COUNT(*) as total
            FROM creditos_historicos
            GROUP BY tipo_subsidio
            ORDER BY total DESC
            LIMIT 5
        """)
        
        print(f"  {'Tipo de Subsidio':<50} {'Total':>15}")
        print(f"  {'-'*50} {'-'*15}")
        
        for tipo, total in cursor_pg.fetchall():
            print(f"  {tipo:<50} {total:>15,}")
        
        print("\n" + "="*100)
        print("✓ REPORTE GENERADO EXITOSAMENTE")
        print("="*100 + "\n")
        
        conn_pg.close()
        conn_sql.close()
        
    except Exception as e:
        print(f"\n✗ Error generando reporte: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generar_reporte()
