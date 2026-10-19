# 📱 API de Inventario

Una API REST para gestionar inventario, ventas y dinero. Ideal para e-commerce y pequeños negocios.

---

## 📋 Requisitos Previos

1. **Python 3.10+**
   - Verificar: `python --version`

2. **PostgreSQL** (Base de datos)
   - [Descargar aquí](https://www.postgresql.org/download/)

3. **Git** (opcional, pero recomendado)

---

## 🚀 Instalación

### PASO 1: Clonar o descargar el proyecto

```bash
cd tu-carpeta-de-proyectos
git clone https://github.com/tuusuario/inventario-app.git
cd inventario-app
```

### PASO 2: Crear entorno virtual

El entorno virtual aísla las librerías de este proyecto.

```bash
# En Windows:
python -m venv venv
venv\Scripts\activate

# En Mac/Linux:
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` en tu terminal, indicando que el entorno está activo.

### PASO 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala FastAPI, SQLAlchemy, PostgreSQL, etc.

### PASO 4: Configurar PostgreSQL

**En Windows:**

1. Abre pgAdmin (generalmente viene con PostgreSQL)
2. Crea una nueva base de datos:
   - Right-click en "Databases" → "Create" → "Database"
   - Nombre: `inventario_db`
   - Owner: `postgres` (usuario por defecto)

**En Mac/Linux (terminal):**

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear la BD
CREATE DATABASE inventario_db;

# Salir
\q
```

### PASO 5: Actualizar el archivo database.py

Abre `database.py` y actualiza esta línea:

```python
DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/inventario_db"
```

Reemplaza:
- `usuario` → El usuario de PostgreSQL (por defecto: `postgres`)
- `contraseña` → Tu contraseña de PostgreSQL
- `inventario_db` → Nombre de la BD que creaste

**Ejemplo:**
```python
DATABASE_URL = "postgresql://postgres:micontraseña123@localhost:5432/inventario_db"
```

### PASO 6: ¡Ejecutar la API!

```bash
python main.py
```

Deberías ver algo como:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🧪 Probar la API

### Opción 1: Interfaz de Swagger (Muy fácil!)

Abre tu navegador y ve a:

```
http://localhost:8000/docs
```

Verás una interfaz bonita donde podes:
- Ver todos los endpoints
- Hacer peticiones
- Ver las respuestas

### Opción 2: Con curl (Terminal)

Crear un producto:

```bash
curl -X POST "http://localhost:8000/productos" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Remera",
    "precio_costo": 200,
    "precio_venta": 500,
    "sku": "REM001",
    "cantidad_stock": 50,
    "categoria": "Ropa"
  }'
```

Obtener todos los productos:

```bash
curl "http://localhost:8000/productos"
```

---

## 📁 Estructura del Proyecto

```
inventario-app/
├── database.py          # Configuración de la BD
├── models.py            # Definición de tablas (Producto, Venta, etc.)
├── schemas.py           # Validación de datos de entrada
├── main.py              # La API principal con todos los endpoints
├── requirements.txt     # Librerías necesarias
└── README.md           # Este archivo
```

---

## 🔌 Endpoints Disponibles

### Productos

| Método | Ruta | Descripción |
|--------|------|-------------|
| **POST** | `/productos` | Crear producto |
| **GET** | `/productos` | Listar todos |
| **GET** | `/productos/{id}` | Obtener uno |
| **PUT** | `/productos/{id}` | Actualizar |
| **DELETE** | `/productos/{id}` | Eliminar |

### Ventas

| Método | Ruta | Descripción |
|--------|------|-------------|
| **POST** | `/ventas` | Registrar venta |
| **GET** | `/ventas` | Listar ventas |

### Dashboard

| Método | Ruta | Descripción |
|--------|------|-------------|
| **GET** | `/dashboard` | Resumen de datos |

---

## 🛠️ Solucionar Problemas

### Error: `ModuleNotFoundError`

```bash
pip install -r requirements.txt
```

### Error: `could not connect to server`

- Verifica que PostgreSQL está corriendo
- Verifica que la `DATABASE_URL` es correcta en `database.py`

### Puerto 8000 ya está en uso

Cambia el puerto en `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📚 Próximos Pasos

1. **Entender el código**: Lee los comentarios en cada archivo
2. **Agregar más endpoints**: Por ejemplo, para movimientos de stock
3. **Crear la app móvil**: Conecta desde React Native/Flutter
4. **Agregar autenticación**: Usuario y contraseña
5. **Integrar Mercado Libre/Pago**: APIs externas

---

## 💡 Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Pydantic Docs](https://docs.pydantic.dev/)

---

¡Divertite aprendiendo! 🚀
