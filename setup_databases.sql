-- ============================================================
-- SCRIPTS DE CONFIGURACIÓN DE BASES DE DATOS
-- Ministerio de Desarrollo Humano - Sistema de Créditos
-- ============================================================

-- ============================================================
-- PARTE 1: SQL SERVER (REPOSITORIO OPERACIONAL/ACTUAL)
-- ============================================================
-- Ejecutar en SQL Server Management Studio (SSMS) o sqlcmd

-- 1.1 Crear base de datos para datos actuales (2025)
IF DB_ID('MDH_Operacional') IS NULL
    CREATE DATABASE MDH_Operacional;
GO

USE MDH_Operacional;
GO

-- 1.2 Crear tabla para créditos actuales (año 2025)
IF OBJECT_ID('dbo.CreditosActuales','U') IS NULL
CREATE TABLE dbo.CreditosActuales (
    CreditoID     INT           NOT NULL PRIMARY KEY,
    Anio          INT           NOT NULL CHECK (Anio = 2025),
    Mes           INT           NOT NULL CHECK (Mes BETWEEN 1 AND 12),
    Beneficiario  NVARCHAR(100) NOT NULL,
    Monto         DECIMAL(12,2) NOT NULL CHECK (Monto > 0),
    Estado        NVARCHAR(20)  NOT NULL DEFAULT 'ACTIVO',
    FechaRegistro DATETIME      DEFAULT GETDATE()
);
GO

-- 1.3 Crear índices para optimizar consultas
CREATE INDEX IX_CreditosActuales_Anio_Mes ON dbo.CreditosActuales(Anio, Mes);
CREATE INDEX IX_CreditosActuales_Beneficiario ON dbo.CreditosActuales(Beneficiario);
CREATE INDEX IX_CreditosActuales_Estado ON dbo.CreditosActuales(Estado);
GO

-- 1.4 Verificar tabla creada
SELECT 
    TABLE_NAME, 
    COLUMN_NAME, 
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'CreditosActuales'
ORDER BY ORDINAL_POSITION;
GO

-- 1.5 (OPCIONAL) Limpiar datos de pruebas anteriores
-- TRUNCATE TABLE dbo.CreditosActuales;
-- GO


-- ============================================================
-- PARTE 2: POSTGRESQL (REPOSITORIO HISTÓRICO)
-- ============================================================
-- Ejecutar en pgAdmin o psql

-- 2.1 Crear base de datos (ejecutar conectado a postgres o template1)
-- CREATE DATABASE mdh_historico;

-- 2.2 Conectarse a la base mdh_historico y ejecutar:

-- Crear tabla para créditos históricos (años 2022, 2023, 2024)
CREATE TABLE IF NOT EXISTS creditos_historicos (
    credito_id     INT PRIMARY KEY,
    anio           INT NOT NULL CHECK (anio IN (2022, 2023, 2024)),
    mes            INT NOT NULL CHECK (mes BETWEEN 1 AND 12),
    beneficiario   VARCHAR(100) NOT NULL,
    monto          NUMERIC(12,2) NOT NULL CHECK (monto > 0),
    estado         VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2.3 Crear índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_creditos_historicos_anio_mes 
    ON creditos_historicos(anio, mes);

CREATE INDEX IF NOT EXISTS idx_creditos_historicos_beneficiario 
    ON creditos_historicos(beneficiario);

CREATE INDEX IF NOT EXISTS idx_creditos_historicos_estado 
    ON creditos_historicos(estado);

-- 2.4 Verificar tabla creada
SELECT 
    column_name, 
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'creditos_historicos'
ORDER BY ordinal_position;

-- 2.5 (OPCIONAL) Limpiar datos de pruebas anteriores
-- TRUNCATE TABLE creditos_historicos;


-- ============================================================
-- CONSULTAS DE VALIDACIÓN
-- ============================================================

-- SQL SERVER - Ver todos los créditos actuales (2025)
-- USE MDH_Operacional;
-- SELECT * FROM dbo.CreditosActuales ORDER BY Mes;

-- SQL SERVER - Resumen por mes
-- SELECT Mes, COUNT(*) as Cantidad, SUM(Monto) as Total
-- FROM dbo.CreditosActuales
-- GROUP BY Mes
-- ORDER BY Mes;

-- POSTGRESQL - Ver todos los créditos históricos (2022-2024)
-- SELECT * FROM creditos_historicos ORDER BY anio, mes;

-- POSTGRESQL - Resumen por año
-- SELECT anio, COUNT(*) as cantidad, SUM(monto) as total
-- FROM creditos_historicos
-- GROUP BY anio
-- ORDER BY anio;


-- ============================================================
-- SCRIPTS DE LIMPIEZA (USAR CON PRECAUCIÓN)
-- ============================================================

-- SQL SERVER - Eliminar todos los datos
-- USE MDH_Operacional;
-- TRUNCATE TABLE dbo.CreditosActuales;
-- GO

-- SQL SERVER - Eliminar tabla y base de datos
-- USE master;
-- GO
-- DROP DATABASE IF EXISTS MDH_Operacional;
-- GO

-- POSTGRESQL - Eliminar todos los datos
-- TRUNCATE TABLE creditos_historicos;

-- POSTGRESQL - Eliminar tabla y base de datos
-- DROP TABLE IF EXISTS creditos_historicos;
-- DROP DATABASE IF EXISTS mdh_historico;


-- ============================================================
-- CONSULTAS DE ANÁLISIS DISTRIBUIDO
-- ============================================================

-- Estas consultas deben ejecutarse desde el middleware Python
-- que combina datos de ambos repositorios

-- Ejemplo de análisis que el middleware puede realizar:
-- 1. Total de créditos por año (todos los años)
-- 2. Comparación año a año
-- 3. Beneficiarios con múltiples créditos
-- 4. Monto promedio por año
-- 5. Distribución mensual de créditos
