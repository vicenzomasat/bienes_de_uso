# Sistema de Amortización con Ajuste por Inflación FACPCE + Decimales Argentinos

## 🚀 Descripción
Sistema completo para gestión de bienes de uso con:
- ✅ Amortización tradicional basada en valores históricos
- ✅ Ajuste por inflación contable usando índices FACPCE
- ✅ **Manejo completo de decimales en formato argentino (1.234.567,89)**
- ✅ **CSV con separador punto y coma (;) para evitar conflictos**
- ✅ Ventanas separadas para vista histórica y ajustada
- ✅ Preparado para migración a SQLite

## 📊 Funcionalidades Principales

### Vista Histórica
- Gestión completa de bienes de uso
- Cálculos de amortización sobre valor histórico
- Cálculos de amortización tradicional
- **Visualización con formato argentino: 1.234.567,89**
- Import/Export CSV con decimales argentinos

### Vista Ajustada por Inflación
- Cálculo automático de ajuste por inflación FACPCE
- **Todos los valores en formato decimal argentino**
- Índices FACPCE integrados con validación
- Validación automática de índices faltantes
- Link directo a fuente oficial FACPCE
- Multithreading para cálculos complejos

## 🔢 Manejo de Decimales Argentinos

### Formato de Entrada y Visualización
```
Valor: 1.234.567,89
- Separador de miles: . (punto)
- Separador decimal: , (coma)
```

### Archivos CSV
```csv
ID;Descripción;TipoBien;Amortizable;Años;Ejercicio;FechaIngreso;FechaBaja;ValorOrigen
1;Máquina Industrial;Maquinaria;SI;10;2020;15/03/2020;;1.250.000,00
```

**Características CSV:**
- ✅ Separador: **punto y coma (;)**
- ✅ Decimales: **formato argentino (1.234.567,89)**
- ✅ Compatible con Excel argentino
- ✅ Sin conflictos entre separadores

## 🎯 Ejecución
```bash
python main.py
```

## 📋 Estructura del Sistema

```
models/          # Clases de datos (Bien, Empresa, IndiceFACPCE)
utils/           # Utilidades con soporte decimal argentino
# Sistema de Amortización con Ajuste por Inflación FACPCE + Decimales Argentinos

## 🚀 Descripción
Sistema de escritorio para gestión de bienes de uso con enfoque en contabilidad argentina:

- ✅ Amortización histórica y cálculo tradicional
- ✅ Ajuste por inflación contable usando índices FACPCE
- ✅ Manejo completo de decimales en formato argentino (1.234.567,89)
- ✅ CSV con separador punto y coma (;) para evitar conflictos con decimales
- ✅ Vistas separadas: Histórica (valores sin ajustar) y Ajustada (valores inflacionados)
- ✅ Persistencia en DuckDB (multi‑CUIT / multi‑empresa)

## 📊 Funcionalidades Principales

### Vista Histórica
- Gestión completa de bienes de uso (crear, importar, eliminar)
- Cálculos de amortización sobre valor histórico
- Visualización con formato argentino: 1.234.567,89
- Import/Export CSV con decimales argentinos

### Vista Ajustada por Inflación
- Cálculo automático de ajuste por inflación FACPCE
- Índices integrados y validación de fechas faltantes
- Export CSV de la vista ajustada
- Multithreading para cálculos pesados, interfaz responsiva

### Persistencia y Multi‑CUIT
- DuckDB como almacenamiento local (archivo: `data/cartera.duckdb`)
- Soporta múltiples empresas identificadas por C.U.I.T.
- Búsqueda por CUIT y creación rápida de dataset vacío si no existe
- Guardado con transacciones y backup (EXPORT DATABASE → Parquet)

## 🔢 Manejo de Decimales Argentinos

Formato de entrada y visualización:

Valor: 1.234.567,89
- Separador de miles: . (punto)
- Separador decimal: , (coma)

Archivos CSV de ejemplo:

```csv
ID;Descripción;TipoBien;Amortizable;Años;Ejercicio;FechaIngreso;FechaBaja;ValorOrigen
1;Máquina Industrial;Maquinaria;SI;10;2020;15/03/2020;;1.250.000,00
```

Características CSV:

- ✅ Separador: punto y coma (;)
- ✅ Decimales: formato argentino (1.234.567,89)
- ✅ Compatible con Excel argentino

## 🎯 Cómo ejecutar

En un entorno con Python 3.10+:

```powershell
python main.py
```

## 📋 Estructura del Proyecto

```
data/            # DuckDB file: cartera.duckdb
db/              # DuckDB helpers (schema, load/save)
models/          # Clases de datos (Bien, Empresa, IndiceFACPCE)
utils/           # Utilidades (validators, csv handler)
modules/         # Lógica de negocio (amortizaciones, inflacion, filtros)
views/           # Ventanas de interfaz (Tkinter)
dev_tools/       # Legacy generator (README only)
legacy/          # Archived SQLite prep (disabled)
```

## ✅ Ventajas destacadas

- Decimales argentinos nativos → Menos errores de importación/exportación
- CSV con `;` evita colisiones con la coma decimal
- UI orientada a contadores (datos de empresa, consulta por CUIT)
- Guardado transaccional en DuckDB y backups exportables

## ⚙️ Notas operativas y seguridad

- Mantener un solo escritor por archivo `.duckdb` (la app).
- Si abre `data/cartera.duckdb` con otra herramienta, hágalo en modo lectura.
- El archivo `legacy/database_prep.py` y la sección generadora previa han sido
	deshabilitados para evitar regenerar esquemas antiguos con columnas de "fecha diferida".

## 🔧 Futuras mejoras sugeridas

- Editor inline para bienes (actualmente la edición muestra un placeholder)
- Migraciones formales si cambiamos schema (ahora tenemos `meta.schema_version`)
- Tests unitarios para amortización e inflación

## 🔗 Recursos

- Índices oficiales FACPCE: https://www.facpce.org.ar/indices-facpce/

