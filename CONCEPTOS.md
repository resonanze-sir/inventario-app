# 📚 Conceptos de APIs REST

Vamos a aprender qué significa cada cosa que vimos en el código.

---

## ¿Qué es una API?

**API** = "Application Programming Interface" (Interfaz de Programación de Aplicaciones)

Es como un "camarero" entre tu app móvil y la base de datos:

```
App Móvil: "Necesito todos los productos"
           ↓
        API (Camarero)
           ↓
      Base de Datos: Trae los productos
           ↓
        API: Aquí están!
           ↓
App Móvil: ¡Gracias! Muestro en pantalla
```

---

## ¿Qué es REST?

**REST** = "Representational State Transfer"

Es un **estilo** para crear APIs. Sus reglas son:

### 1. Usa URLs para recursos

En lugar de hacer:
```
❌ /dame-todos-los-productos
❌ /get-productos
```

Hazlo así:
```
✅ /productos
```

### 2. Usa verbos HTTP

El método HTTP indica QUÉ HACER:

| Verbo | Significado | Ejemplo |
|-------|-------------|---------|
| **GET** | Obtener datos | Traer lista de productos |
| **POST** | Crear datos | Crear un nuevo producto |
| **PUT** | Actualizar datos | Cambiar el precio de un producto |
| **DELETE** | Eliminar datos | Eliminar un producto |

**Analogía con un restaurante:**

- **GET /meseros** → "Dame la lista de meseros" (obtener)
- **POST /meseros** → "Quiero contratar un nuevo mesero" (crear)
- **PUT /meseros/5** → "Quiero cambiar al mesero #5 a otra mesa" (actualizar)
- **DELETE /meseros/5** → "Despedir al mesero #5" (eliminar)

---

## Estructura de una petición HTTP

### Ejemplo: Obtener un producto

```
GET /productos/5 HTTP/1.1
Host: localhost:8000
Content-Type: application/json
```

**¿Qué significa?**

- **GET** = Verbo HTTP (obtener)
- **/productos/5** = Ruta (qué recurso quiero)
- **HTTP/1.1** = Versión del protocolo
- **Host** = Dónde está alojada la API
- **Content-Type** = Tipo de contenido (JSON)

### Ejemplo: Crear un producto

```
POST /productos HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "nombre": "Remera",
  "precio_costo": 200,
  "precio_venta": 500,
  "sku": "REM001"
}
```

**¿Qué significa?**

- **POST** = Crear (envío datos)
- **{...}** = El cuerpo (body) con los datos

---

## Estructura de una respuesta HTTP

### Respuesta exitosa

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 5,
  "nombre": "Remera",
  "precio_venta": 500,
  "stock": 50,
  "fecha_creacion": "2024-01-15T10:30:00"
}
```

**¿Qué significa?**

- **200 OK** = Status code (éxito)
- **{...}** = Los datos que pediste

### Respuesta con error

```
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "detail": "Producto no encontrado"
}
```

**¿Qué significa?**

- **404** = Status code (no existe)
- **"detail"** = El mensaje de error

---

## Status Codes Importantes

| Código | Significado | Ejemplo |
|--------|-------------|---------|
| **200** | OK - Todo bien | El producto existe |
| **201** | Created - Creado | Creaste un producto exitosamente |
| **400** | Bad Request - Solicitud mala | Enviaste un JSON inválido |
| **404** | Not Found - No existe | El producto que buscas no existe |
| **500** | Server Error - Error del servidor | Bug en nuestro código |

---

## ¿Cómo funciona nuestro código?

### 1. El cliente (app móvil) hace una petición

```python
# La app móvil envía:
POST /productos
{
  "nombre": "Remera",
  "precio_venta": 500
}
```

### 2. FastAPI recibe la petición

```python
@app.post("/productos")
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    # FastAPI automáticamente:
    # 1. Recibe el JSON
    # 2. Valida con Pydantic (ProductoCreate)
    # 3. Te lo pasa ya validado
```

### 3. El endpoint procesa y responde

```python
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    # 1. Verificar datos
    if producto_existe:
        raise HTTPException(status_code=400, detail="Ya existe")
    
    # 2. Crear objeto
    db_producto = Producto(nombre=producto.nombre, ...)
    
    # 3. Guardar en BD
    db.add(db_producto)
    db.commit()
    
    # 4. Devolver respuesta
    return db_producto  # FastAPI convierte a JSON automáticamente
```

---

## Analogía: El Sistema de Expedientes

Imagina que tu API es un **sistema de expedientes en una oficina de gobierno**:

### Los Resources (Recursos)

```
/productos        → Carpeta de "Productos"
/ventas          → Carpeta de "Ventas"
/transacciones   → Carpeta de "Transacciones"
```

### Las Operaciones (Verbos)

```
GET /productos        → "Dame la lista de todos los expedientes"
POST /productos       → "Voy a abrir un nuevo expediente"
GET /productos/5      → "Dame el expediente #5"
PUT /productos/5      → "Voy a actualizar el expediente #5"
DELETE /productos/5   → "Voy a archivar el expediente #5"
```

### La Respuesta

```
GET /productos
↓
El empleado busca en la carpeta
↓
Trae los documentos
↓
Te entrega una respuesta JSON
```

---

## FastAPI: El "Camarero Inteligente"

FastAPI automáticamente:

1. **Recibe** las peticiones HTTP
2. **Valida** los datos (¿Es un número? ¿Es texto?)
3. **Convierte** entre JSON y objetos Python
4. **Ejecuta** tu código
5. **Devuelve** respuestas JSON

```python
@app.post("/productos")
def crear_producto(producto: ProductoCreate):
    #                        ↑↑↑↑↑↑↑↑↑↑↑
    # FastAPI valida que sea ProductoCreate
    # Si falta un campo: ❌ Error automático
    # Si hay un tipo erróneo: ❌ Error automático
    # Si todo está bien: ✅ Te pasa el objeto
```

---

## SQLAlchemy: El "Traductor" a la BD

SQLAlchemy traduce Python a SQL:

```python
# Código Python (lo que escribimos)
db.query(Producto).filter(Producto.id == 5).first()

# Se traduce a SQL automáticamente
SELECT * FROM productos WHERE id = 5 LIMIT 1
```

Ventajas:
- ✅ No escribir SQL (menos errores)
- ✅ Funciona con cualquier BD
- ✅ Más seguro contra hackers

---

## Session (Sesión de BD)

Una **sesión** es como "abrir un archivo":

```python
db = SessionLocal()  # Abrir conexión

# Hacer cambios
db.add(nuevo_producto)
db.commit()  # Guardar cambios

db.close()  # Cerrar conexión
```

**Por qué es importante cerrar:**
- Libera recursos
- Evita "conexiones colgadas"
- Permite que otros usen la BD

---

## Flujo Completo: Crear un Producto

```
1. App móvil
   │
   ├─ Hace petición POST
   │  Body: {"nombre": "Remera", "precio": 500}
   │
   ↓

2. FastAPI recibe
   │
   ├─ Pydantic valida el JSON
   │  ✅ ¿Tiene todos los campos? Sí
   │  ✅ ¿Tipos correctos? Sí
   │
   ↓

3. Tu función crear_producto() se ejecuta
   │
   ├─ Crea objeto Producto
   ├─ Agrega a la sesión: db.add()
   ├─ Confirma: db.commit()
   │
   ↓

4. SQLAlchemy traduce a SQL
   │
   ├─ INSERT INTO productos VALUES (...)
   │
   ↓

5. PostgreSQL ejecuta
   │
   ├─ Inserta en la tabla
   ├─ Genera ID automáticamente
   │
   ↓

6. FastAPI devuelve respuesta
   │
   ├─ Status: 200 OK
   ├─ Body: {"id": 1, "nombre": "Remera", ...}
   │
   ↓

7. App móvil recibe
   │
   └─ Muestra "¡Producto creado!"
```

---

## Prueba Mental: ¿Qué Pasa Si...?

### ¿Qué pasa si enviamos JSON inválido?

```json
{
  "nombre": "Remera",
  "precio": "No es un número"  ← Error!
}
```

**Resultado:**
```
Pydantic automáticamente rechaza
Status: 422 Unprocessable Entity
"precio debe ser un número"
```

### ¿Qué pasa si intentamos actualizar un producto que no existe?

```python
PUT /productos/9999
```

**Resultado:**
```python
producto = db.query(...).first()  # None
if not producto:
    raise HTTPException(404, "No existe")
```

---

## Próxima Lección

Ahora que entienden los conceptos, vamos a:
1. Ejecutar la API
2. Probar los endpoints
3. Ver cómo funciona en la realidad
4. Agregar más funcionalidades

¡Vámonos! 🚀
