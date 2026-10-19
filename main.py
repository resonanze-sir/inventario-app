# main.py
# Este es el archivo principal de la API
# Aquí definimos todas las rutas (endpoints)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

# Importamos lo que creamos
from database import engine, get_db, Base
from models import Producto, Venta, MovimientoStock, Transaccion, Compra
from schemas import (
    ProductoCreate, ProductoUpdate, ProductoResponse,
    VentaCreate, VentaResponse,
    MovimientoStockCreate, MovimientoStockResponse,
    TransaccionCreate, TransaccionResponse,
    CompraCreate, CompraResponse,
    DashboardResponse
)

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

# Crear todas las tablas en la BD
# (Si no existen, las crea)
Base.metadata.create_all(bind=engine)

# Crear la aplicación FastAPI
app = FastAPI(
    title="API Inventario",
    description="API para gestionar inventario, ventas y dinero",
    version="1.0.0"
)

# ============================================
# ENDPOINTS DE PRODUCTOS
# ============================================

@app.get("/")
def read_root():
    """
    Ruta raíz: http://localhost:8000/
    
    Devuelve un mensaje simple para verificar que la API funciona.
    """
    return {"mensaje": "¡Bienvenido a la API de Inventario!"}


@app.post("/productos", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """
    CREAR un nuevo producto
    
    POST /productos
    
    La app móvil envía:
    {
        "nombre": "Remera",
        "precio_costo": 200,
        "precio_venta": 500,
        "sku": "REM001",
        "cantidad_stock": 50,
        "categoria": "Ropa"
    }
    
    ¿Cómo funciona?
    1. El parámetro 'producto' recibe los datos y Pydantic los valida
    2. 'db' es la conexión a la base de datos (inyectada automáticamente)
    3. Creamos un nuevo objeto Producto de SQLAlchemy
    4. Lo guardamos en la BD
    5. Devolvemos el producto creado
    """
    
    # Verificar que el SKU no exista ya
    db_producto_existente = db.query(Producto).filter(
        Producto.sku == producto.sku
    ).first()
    
    if db_producto_existente:
        # Si existe, lanzamos error HTTP 400
        raise HTTPException(
            status_code=400,
            detail="El SKU ya existe"
        )
    
    # Crear el objeto de BD
    db_producto = Producto(
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio_costo=producto.precio_costo,
        precio_venta=producto.precio_venta,
        sku=producto.sku,
        cantidad_stock=producto.cantidad_stock,
        categoria=producto.categoria
    )
    
    # Guardarlo en la BD
    db.add(db_producto)  # Agrega a la sesión
    db.commit()  # Confirma los cambios
    db.refresh(db_producto)  # Actualiza el objeto con datos de la BD
    
    return db_producto


@app.get("/productos", response_model=list[ProductoResponse])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    LISTAR todos los productos
    
    GET /productos
    GET /productos?skip=10&limit=20  (para paginar)
    
    skip: cuántos saltar (para paginar)
    limit: cuántos mostrar como máximo
    
    Devuelve una lista de productos.
    """
    
    # Query: Consulta a la BD
    # filter(activo == 1): Solo productos activos
    # offset(skip): Salta 'skip' productos
    # limit(limit): Trae máximo 'limit' productos
    
    productos = db.query(Producto).filter(
        Producto.activo == 1
    ).offset(skip).limit(limit).all()
    
    return productos


@app.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    OBTENER un producto específico
    
    GET /productos/5
    
    producto_id: El ID del producto que queremos obtener
    """
    
    # Buscar el producto por ID
    producto = db.query(Producto).filter(
        Producto.id == producto_id,
        Producto.activo == 1
    ).first()
    
    if not producto:
        # Si no existe, error 404
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )
    
    return producto


@app.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """
    ACTUALIZAR un producto
    
    PUT /productos/5
    
    Podés actualizar solo algunos campos.
    """
    
    # Buscar el producto
    db_producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()
    
    if not db_producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )
    
    # Actualizar solo los campos que se enviaron
    # .dict(exclude_unset=True) devuelve solo los campos que se especificaron
    datos_actualizacion = producto_update.dict(exclude_unset=True)
    
    for campo, valor in datos_actualizacion.items():
        setattr(db_producto, campo, valor)  # Actualiza el atributo
    
    # Guardar cambios
    db.commit()
    db.refresh(db_producto)
    
    return db_producto


@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    ELIMINAR un producto (en realidad lo desactiva)
    
    DELETE /productos/5
    
    No lo borramos realmente, solo lo marcamos como inactivo.
    Esto preserva el historial.
    """
    
    db_producto = db.query(Producto).filter(
        Producto.id == producto_id
    ).first()
    
    if not db_producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )
    
    # Marcar como inactivo
    db_producto.activo = 0
    db.commit()
    
    return {"mensaje": "Producto eliminado"}


# ============================================
# ENDPOINTS DE VENTAS
# ============================================

@app.post("/ventas", response_model=VentaResponse)
def registrar_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    """
    REGISTRAR una venta
    
    POST /ventas
    
    Cuando alguien compra, registramos:
    1. La venta en la tabla VENTAS
    2. La salida de stock en MOVIMIENTOS_STOCK
    3. La entrada de dinero en TRANSACCIONES
    
    Es como un "cuádruple movimiento contable".
    """
    
    # Verificar que el producto existe
    producto = db.query(Producto).filter(
        Producto.id == venta.producto_id
    ).first()
    
    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )
    
    # Verificar que hay suficiente stock
    if producto.cantidad_stock < venta.cantidad:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Hay {producto.cantidad_stock}, necesitas {venta.cantidad}"
        )
    
    # Calcular el total de la venta
    total_venta = venta.cantidad * venta.precio_unitario
    
    # ===== 1. CREAR LA VENTA =====
    db_venta = Venta(
        producto_id=venta.producto_id,
        cantidad=venta.cantidad,
        precio_unitario=venta.precio_unitario,
        total=total_venta,
        metodo_pago=venta.metodo_pago
    )
    db.add(db_venta)
    
    # ===== 2. ACTUALIZAR EL STOCK =====
    producto.cantidad_stock -= venta.cantidad
    
    # ===== 3. REGISTRAR MOVIMIENTO DE STOCK =====
    movimiento = MovimientoStock(
        producto_id=venta.producto_id,
        tipo="salida",
        cantidad=venta.cantidad,
        motivo="Venta"
    )
    db.add(movimiento)
    
    # ===== 4. REGISTRAR TRANSACCIÓN DE DINERO =====
    # Primero obtener el saldo actual
    ultima_transaccion = db.query(Transaccion).order_by(
        Transaccion.id.desc()
    ).first()
    
    saldo_anterior = ultima_transaccion.saldo_antes + ultima_transaccion.monto if ultima_transaccion else 0
    
    transaccion = Transaccion(
        tipo="entrada",
        monto=total_venta,
        concepto=f"Venta de {producto.nombre}",
        metodo_pago=venta.metodo_pago,
        referencia=f"Venta #{db_venta.id}",
        saldo_antes=saldo_anterior
    )
    db.add(transaccion)
    
    # Confirmar todos los cambios juntos
    db.commit()
    db.refresh(db_venta)
    
    return db_venta


@app.get("/ventas", response_model=list[VentaResponse])
def listar_ventas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    LISTAR todas las ventas
    
    GET /ventas
    GET /ventas?skip=0&limit=50
    """
    
    ventas = db.query(Venta).offset(skip).limit(limit).all()
    return ventas


# ============================================
# ENDPOINTS DE COMPRAS
# ============================================

@app.post("/compras", response_model=CompraResponse)
def registrar_compra(compra: CompraCreate, db: Session = Depends(get_db)):
    """
    REGISTRAR una compra de tejas
    
    POST /compras
    
    Cuando compras tejas:
    1. Se registra en COMPRAS
    2. Se aumenta el STOCK del producto
    3. Se registra el GASTO en TRANSACCIONES
    4. Se registra el movimiento en MOVIMIENTOS_STOCK
    
    Nota: La fecha se genera automáticamente
    """
    
    # Verificar que el producto existe
    producto = db.query(Producto).filter(
        Producto.id == compra.producto_id
    ).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Calcular total
    total_compra = compra.cantidad * compra.precio_unitario
    
    # ===== 1. CREAR LA COMPRA =====
    db_compra = Compra(
        producto_id=compra.producto_id,
        cantidad=compra.cantidad,
        precio_unitario=compra.precio_unitario,
        total=total_compra,
        ubicacion=compra.ubicacion,
        notas=compra.notas,
        hora=compra.hora
    )
    db.add(db_compra)
    
    # ===== 2. ACTUALIZAR EL STOCK =====
    producto.cantidad_stock += compra.cantidad
    
    # ===== 3. REGISTRAR MOVIMIENTO DE STOCK =====
    movimiento = MovimientoStock(
        producto_id=compra.producto_id,
        tipo="entrada",
        cantidad=compra.cantidad,
        motivo="Compra de tejas"
    )
    db.add(movimiento)
    
    # ===== 4. REGISTRAR GASTO (SALIDA DE DINERO) =====
    ultima_transaccion = db.query(Transaccion).order_by(
        Transaccion.id.desc()
    ).first()
    
    saldo_anterior = ultima_transaccion.saldo_antes + ultima_transaccion.monto if ultima_transaccion else 0
    
    transaccion = Transaccion(
        tipo="salida",  # Salida porque gastaste dinero
        monto=total_compra,
        concepto=f"Compra de {producto.nombre}",
        saldo_antes=saldo_anterior
    )
    db.add(transaccion)
    
    db.commit()
    db.refresh(db_compra)
    
    return db_compra


@app.get("/compras", response_model=list[CompraResponse])
def listar_compras(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    LISTAR todas las compras
    
    GET /compras
    GET /compras?skip=0&limit=50
    """
    compras = db.query(Compra).offset(skip).limit(limit).all()
    return compras


@app.get("/compras/{compra_id}", response_model=CompraResponse)
def obtener_compra(compra_id: int, db: Session = Depends(get_db)):
    """
    OBTENER una compra específica
    
    GET /compras/1
    """
    compra = db.query(Compra).filter(Compra.id == compra_id).first()
    
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    
    return compra


# ============================================
# ENDPOINTS DE DASHBOARD
# ============================================

@app.get("/dashboard", response_model=DashboardResponse)
def obtener_dashboard(db: Session = Depends(get_db)):
    """
    OBTENER datos del dashboard
    
    GET /dashboard
    
    Devuelve resumen de todo: cuántos productos, stock total, dinero, etc.
    
    Esto se muestra en la pantalla principal de la app móvil.
    """
    
    # Contar productos activos
    total_productos = db.query(func.count(Producto.id)).filter(
        Producto.activo == 1
    ).scalar()
    
    # Sumar el stock de todos los productos
    total_stock = db.query(func.sum(Producto.cantidad_stock)).filter(
        Producto.activo == 1
    ).scalar() or 0
    
    # Sumar el dinero total
    total_dinero = db.query(func.sum(Transaccion.monto)).filter(
        Transaccion.tipo == "entrada"
    ).scalar() or 0
    
    # Dinero vendido HOY
    hoy = datetime.utcnow().date()
    total_ventas_hoy = db.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha) == hoy
    ).scalar() or 0
    
    # Productos con stock bajo (menos de 10 unidades)
    productos_bajo_stock = db.query(func.count(Producto.id)).filter(
        Producto.cantidad_stock < 10,
        Producto.activo == 1
    ).scalar()
    
    # Productos activos
    productos_activos = total_productos
    
    return DashboardResponse(
        total_productos=total_productos,
        total_stock=int(total_stock),
        total_dinero=total_dinero,
        total_ventas_hoy=total_ventas_hoy,
        productos_bajo_stock=productos_bajo_stock,
        productos_activos=productos_activos
    )


# ============================================
# EJECUTAR LA API
# ============================================

if __name__ == "__main__":
    # Para ejecutar: python main.py
    # Luego acceder a: http://localhost:8000
    
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",  # Accesible desde cualquier IP
        port=8000,  # Puerto 8000
        reload=True  # Auto-recarga si cambias código (desarrollo)
    )
