# 🏭 WMS — Warehouse Management System

Sistema completo de gestión de almacén construido con **Streamlit + Supabase (PostgreSQL) + SQLAlchemy**.

---

## 📁 Estructura del proyecto

```
wms_app/
├── app.py              # Aplicación principal Streamlit (UI)
├── database.py         # Modelos SQLAlchemy + conexión
├── services.py         # Lógica de negocio (CRUD + reportes)
├── pdf_generator.py    # Generación de PDFs con ReportLab
├── schema.sql          # Script SQL para Supabase (tablas + datos de ejemplo)
├── requirements.txt    # Dependencias Python
├── .env.example        # Variables de entorno (copiar como .env)
└── .streamlit/
    └── secrets.toml.example
```

---

## 🚀 Instrucciones de despliegue

### 1. Configurar Supabase

1. Crea una cuenta en [supabase.com](https://supabase.com) (plan gratuito disponible)
2. Crea un nuevo proyecto
3. Ve a **SQL Editor** y ejecuta todo el contenido de `schema.sql`
4. Copia la **Connection String** desde `Settings → Database → URI`

### 2. Instalar dependencias locales

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate.bat     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tu URL de Supabase
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[PASSWORD]@...
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La app se abre en `http://localhost:8501`

---

## ☁️ Despliegue en Streamlit Community Cloud (gratuito)

1. Sube el proyecto a GitHub (sin el `.env`)
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Conecta tu repositorio
4. En **Advanced Settings → Secrets**, añade:
   ```toml
   DATABASE_URL = "postgresql://..."
   ```
5. Haz clic en **Deploy**

---

## 🗄️ Modelo de datos

| Tabla        | Descripción                              |
|-------------|------------------------------------------|
| `tarifas`    | Precios por tipo de operación            |
| `clientes`   | Clientes con tarifa y condiciones pago   |
| `stock`      | Pallets en almacén (entrada/salida)      |
| `movimientos`| Registro de operaciones con coste calc.  |

---

## 📱 Funcionalidades

| Módulo        | Descripción                                     |
|--------------|-------------------------------------------------|
| Dashboard     | KPIs en tiempo real, últimas ops, stock activo  |
| Clientes      | CRUD completo con asignación de tarifas         |
| Tarifas       | CRUD completo con precios por operación         |
| Operaciones   | Registro con cálculo automático de coste        |
| Stock         | Gestión de pallets: entrada, salida, consulta   |
| Reportes      | Almacenaje, Picking, Cargas, Resumen mensual    |
| Facturación   | Resumen por cliente + exportación PDF           |

---

## 📊 Tipos de operación

| Tipo        | Coste calculado           |
|-------------|---------------------------|
| almacenaje  | cantidad × precio_pallet_dia |
| picking     | cantidad × precio_picking  |
| packing     | cantidad × precio_picking  |
| carga       | cantidad × precio_carga    |
| descarga    | cantidad × precio_descarga |

---

## 📄 Informes PDF generados

1. **Informe de Almacenaje** — Pallets, días, coste por período
2. **Informe de Picking/Packing** — Detalle de preparaciones
3. **Informe de Cargas/Descargas** — Movimientos de mercancía
4. **Resumen Mensual Global** — Todos los clientes
5. **Factura por Cliente** — Desglose completo individual

---

## ⚙️ Variables de entorno

| Variable       | Descripción                       |
|---------------|-----------------------------------|
| `DATABASE_URL` | Connection string PostgreSQL/Supabase |

---

## 🛠️ Tecnologías

- **Streamlit** `>=1.35` — Interfaz web
- **SQLAlchemy** `>=2.0` — ORM y acceso a BD
- **psycopg2-binary** — Driver PostgreSQL
- **ReportLab** `>=4.0` — Generación de PDFs
- **pandas** — Procesamiento de datos
- **python-dotenv** — Variables de entorno

---

## 💡 Tips de uso

- Crea primero las **tarifas** antes de crear clientes
- Asigna una tarifa a cada cliente para que el coste se calcule automáticamente
- El informe de almacenaje calcula días basándose en `fecha_entrada` y `fecha_salida` del stock
- Puedes filtrar el historial de operaciones por cliente, tipo y rango de fechas
- Los PDFs se generan al instante y están listos para enviar a clientes

---

## 📝 Licencia

MIT — Uso libre para proyectos propios y comerciales.
