@echo off
REM ============================================================
REM SCRIPT DE MIGRACIÓN COMPLETA - DATOS REALES
REM ============================================================

echo.
echo ================================================================================
echo MIGRACION DE DATOS REALES - MINISTERIO DE DESARROLLO HUMANO
echo ================================================================================
echo.
echo Este script creara las bases de datos y migrara los 234,513 registros
echo desde bonoleccion.sql a las bases de datos particionadas.
echo.
echo Distribucion:
echo   - 2022-2024: PostgreSQL (mdh_historico)
echo   - 2025:      SQL Server (MDH_Operacional)
echo.
pause

echo.
echo [1/4] Creando base de datos historica en PostgreSQL...
psql -U postgres -c "DROP DATABASE IF EXISTS mdh_historico;"
psql -U postgres -c "CREATE DATABASE mdh_historico;"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo crear la base de datos PostgreSQL
    pause
    exit /b 1
)
echo OK: Base de datos PostgreSQL creada

echo.
echo [2/4] Creando base de datos operacional en SQL Server...
sqlcmd -S localhost -U sa -P admin123 -Q "IF EXISTS (SELECT name FROM sys.databases WHERE name = 'MDH_Operacional') DROP DATABASE MDH_Operacional; CREATE DATABASE MDH_Operacional;"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo crear la base de datos SQL Server
    pause
    exit /b 1
)
echo OK: Base de datos SQL Server creada

echo.
echo [3/4] Verificando que bonoleccion existe...
psql -U postgres -d bonoleccion -c "SELECT COUNT(*) FROM table1;"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: La base de datos bonoleccion no existe o no tiene datos
    echo.
    echo Ejecuta primero:
    echo   psql -U postgres -c "CREATE DATABASE bonoleccion;"
    echo   psql -U postgres -d bonoleccion -f bonoleccion.sql
    echo.
    pause
    exit /b 1
)
echo OK: Base de datos bonoleccion verificada

echo.
echo [4/4] Ejecutando migracion de datos...
python migracion_datos_reales.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: La migracion fallo
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo MIGRACION COMPLETADA EXITOSAMENTE
echo ================================================================================
echo.
echo Puedes verificar los datos con:
echo   psql -U postgres -d mdh_historico -c "SELECT COUNT(*) FROM creditos_historicos;"
echo   sqlcmd -S localhost -U sa -P admin123 -d MDH_Operacional -Q "SELECT COUNT(*) FROM CreditosActuales;"
echo.
echo Para usar el sistema:
echo   python main_ministerio_actualizado.py
echo.
pause
