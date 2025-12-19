# 📑 ÍNDICE DE DOCUMENTACIÓN
## Sistema de Gestión de Créditos - Ministerio de Desarrollo Humano

Bienvenido al proyecto de particionamiento lógico para gestión de créditos de desarrollo humano.

---

## 🚀 INICIO RÁPIDO

### Para comenzar inmediatamente:
1. **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** ⚡
   - Pasos resumidos para ejecutar
   - Checklist de verificación
   - Solución de problemas comunes

### Para entender el proyecto:
2. **[README.md](README.md)** 📘
   - Documentación completa
   - Contexto y objetivos
   - Arquitectura detallada
   - Instalación paso a paso

---

## 📁 ARCHIVOS DEL PROYECTO

### 🐍 Código Fuente
- **[main.py](main.py)**
  - Script principal del middleware
  - Funciones de inserción y consulta
  - Lógica de particionamiento
  - Ejemplos de uso

### ⚙️ Configuración
- **[setup_databases.sql](setup_databases.sql)**
  - Scripts de creación de bases de datos
  - Definición de tablas
  - Creación de índices
  - Consultas de validación

- **[requirements.txt](requirements.txt)**
  - Dependencias de Python
  - pyodbc y psycopg2-binary

- **[.gitignore](.gitignore)**
  - Archivos a ignorar en Git
  - Protege credenciales y entornos

---

## 📚 DOCUMENTACIÓN

### 📖 Guías y Manuales
- **[README.md](README.md)** - Documentación principal completa
- **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** - Guía de inicio rápido
- **[RESUMEN.txt](RESUMEN.txt)** - Resumen ejecutivo del proyecto

### 🔄 Comparación
- **[COMPARACION_PROYECTOS.md](COMPARACION_PROYECTOS.md)**
  - Comparación con el proyecto de laboratorio de ventas
  - Diferencias y similitudes
  - Casos de uso
  - Conversión entre patrones

---

## 🎯 NAVEGACIÓN POR OBJETIVO

### ¿Quieres ejecutar el proyecto rápidamente?
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

### ¿Necesitas entender la arquitectura?
→ [README.md](README.md) (sección Arquitectura de Particionamiento)

### ¿Quieres configurar las bases de datos?
→ [setup_databases.sql](setup_databases.sql)

### ¿Necesitas ver el código?
→ [main.py](main.py)

### ¿Tienes problemas?
→ [GUIA_RAPIDA.md](GUIA_RAPIDA.md) (sección Problemas Comunes)

### ¿Quieres comparar con el otro proyecto?
→ [COMPARACION_PROYECTOS.md](COMPARACION_PROYECTOS.md)

---

## 🏗️ ARQUITECTURA DEL PROYECTO

```
MINISTERIO DE DESARROLLO HUMANO
      Sistema de Créditos
              │
      ┌───────┴───────┐
      │               │
      ▼               ▼
┌──────────┐    ┌──────────┐
│PostgreSQL│    │   SQL    │
│          │    │  Server  │
└──────────┘    └──────────┘
 Histórico      Operacional
(2022-2024)       (2025)
```

**Criterio de Particionamiento:**
- Años 2022, 2023, 2024 → PostgreSQL (histórico)
- Año 2025 → SQL Server (operacional)

---

## 📊 ESTRUCTURA DE ARCHIVOS

```
ministerio-desarrollo-humano/
│
├── 📄 INDEX.md                     # Este archivo (navegación)
├── 📘 README.md                    # Documentación completa
├── ⚡ GUIA_RAPIDA.md               # Inicio rápido
├── 📋 RESUMEN.txt                  # Resumen ejecutivo
├── 🔄 COMPARACION_PROYECTOS.md    # Comparación con lab ventas
│
├── 🐍 main.py                      # Script principal
├── 🗄️ setup_databases.sql         # Scripts de BD
├── 📦 requirements.txt             # Dependencias
└── 🚫 .gitignore                   # Archivos ignorados
```

---

## 🎓 CONCEPTOS CLAVE

### Particionamiento Lógico
Separación de datos entre múltiples motores de BD según criterios de negocio.

### Motores Heterogéneos
Uso de diferentes sistemas de BD (PostgreSQL + SQL Server) en la misma arquitectura.

### OLTP vs OLAP
- **OLTP** (SQL Server): Transacciones operacionales frecuentes
- **OLAP** (PostgreSQL): Consultas analíticas sobre datos históricos

### Middleware
Capa de software que conecta y coordina acceso a múltiples bases de datos.

---

## ✅ CHECKLIST DE ESTUDIO

Para dominar este proyecto, asegúrate de:

- [ ] Leer [README.md](README.md) completo
- [ ] Entender el criterio de particionamiento
- [ ] Configurar PostgreSQL siguiendo [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
- [ ] Configurar SQL Server
- [ ] Ejecutar [main.py](main.py) exitosamente
- [ ] Verificar datos en ambos motores
- [ ] Entender cada función del código
- [ ] Leer [COMPARACION_PROYECTOS.md](COMPARACION_PROYECTOS.md)
- [ ] Probar modificaciones en el código

---

## 🔗 RECURSOS EXTERNOS

### Documentación Oficial
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQL Server Documentation](https://learn.microsoft.com/en-us/sql/)
- [Python psycopg2](https://www.psycopg.org/docs/)
- [Python pyodbc](https://github.com/mkleehammer/pyodbc/wiki)

### Descargas
- [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- [PostgreSQL](https://www.postgresql.org/download/)
- [SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads)

---

## 🆘 SOPORTE

### Problemas Técnicos
Consulta la sección "Problemas Comunes" en:
- [GUIA_RAPIDA.md](GUIA_RAPIDA.md)

### Preguntas sobre Arquitectura
Revisa:
- [README.md](README.md) - Sección Arquitectura
- [COMPARACION_PROYECTOS.md](COMPARACION_PROYECTOS.md)

### Dudas sobre el Código
Revisa:
- [main.py](main.py) - Código está muy comentado
- [setup_databases.sql](setup_databases.sql) - Scripts SQL documentados

---

## 📅 INFORMACIÓN DEL PROYECTO

**Institución:** Ministerio de Desarrollo Humano  
**Sistema:** Gestión de Créditos de Desarrollo Humano  
**Período de datos:** 2022-2025  
**Tecnologías:** Python, PostgreSQL, SQL Server  
**Patrón:** Particionamiento Lógico Heterogéneo  

---

## 📧 PRÓXIMOS PASOS

1. Lee [GUIA_RAPIDA.md](GUIA_RAPIDA.md)
2. Configura las bases de datos
3. Ejecuta [main.py](main.py)
4. Explora el código y documentación
5. Compara con el proyecto de ventas

---

**¡Buena suerte con tu proyecto!** 🚀

Para cualquier duda, consulta la documentación o revisa los comentarios en el código.
