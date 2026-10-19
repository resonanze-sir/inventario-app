# schemas.py
# Aquí definimos cómo deben verse los datos que llegan desde la app móvil

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

"""
¿Qué es Pydantic?

Pydantic es una librería que valida datos. Cuando la app móvil 
envía información, Pydantic verifica que sea del tipo correcto.

Ejemplo:
- Si envía nombre="Remera" (texto) ✅ Válido
- Si envía nombre=123 (número) ❌ Error! Esperamos texto
"""

# ============================================
# ESQUEMA 1: PRODUCTOS
# ============================================

class ProductoCreate(BaseModel):
    """
    Datos necesarios para CREAR un nuevo producto.
    
    Nota: No incluimos 'id' porque la BD lo genera automáticamente.
    No incluimos 'fecha_creacion' porque se pone automáticamente.
    """
    nombre: str  # Texto obligatorio
    descripcion: Optional[str] = None  # Texto opcional (puede estar vacío)
    precio_costo: float  # Número decimal obligatorio
    precio_venta: float  # Número decimal obligatorio
    sku: str  # Código único obligatorio
    cantidad_stock: int = 0  # Número entero, por defecto 0
    categoria: Optional[str] = None  # Texto opcional


class ProductoUpdate(BaseModel):
    """
    Datos para ACTUALIZAR un producto.
    
    Todos son opcionales porque quizás solo querés cambiar el nombre,
    no todo el producto.
    """
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_costo: Optional[float] = None
    precio_venta: Optional[float] = None
    cantidad_stock: Optional[int] = None
    categoria: Optional[str] = None
    activo: Optional[int] = None


class ProductoResponse(BaseModel):
    """
    Datos que DEVOLVEMOS cuando piden un producto.
    
    Incluimos todos los datos, incluso los que se generaron automáticamente.
    """
    id: int
    nombre: str
    descripcion: Optional[str]
    precio_costo: float
    precio_venta: float
    sku: str
    cantidad_stock: int
    categoria: Optional[str]
    activo: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        # Esto permite que Pydantic trabaje con objetos de SQLAlchemy
        from_attributes = True


# ============================================
# ESQUEMA 2: VENTAS
# ============================================

class VentaCreate(BaseModel):
    """
    Datos para registrar una venta.
    """
    producto_id: int  # Qué producto se vendió
    cantidad: int  # Cuántas unidades
    precio_unitario: float  # A qué precio unitario
    metodo_pago: Optional[str] = None  # Efectivo, Tarjeta, etc.


class VentaResponse(BaseModel):
    """
    Datos que devolvemos de una venta.
    """
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    total: float
    metodo_pago: Optional[str]
    fecha: datetime
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA 3: MOVIMIENTOS DE STOCK
# ============================================

class MovimientoStockCreate(BaseModel):
    """
    Datos para registrar un movimiento de stock.
    """
    producto_id: int  # Qué producto
    tipo: str  # "entrada" o "salida"
    cantidad: int  # Cuántas unidades
    motivo: Optional[str] = None  # Por qué


class MovimientoStockResponse(BaseModel):
    """
    Datos que devolvemos de un movimiento.
    """
    id: int
    producto_id: int
    tipo: str
    cantidad: int
    motivo: Optional[str]
    fecha: datetime
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA 4: TRANSACCIONES DE DINERO
# ============================================

class TransaccionCreate(BaseModel):
    """
    Datos para registrar una transacción de dinero.
    """
    tipo: str  # "entrada" o "salida"
    monto: float  # Cuánto dinero
    concepto: str  # Qué concepto (obligatorio)
    metodo_pago: Optional[str] = None
    referencia: Optional[str] = None


class TransaccionResponse(BaseModel):
    """
    Datos que devolvemos de una transacción.
    """
    id: int
    tipo: str
    monto: float
    concepto: str
    metodo_pago: Optional[str]
    referencia: Optional[str]
    fecha: datetime
    saldo_antes: float
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA 5: COMPRAS
# ============================================

class CompraCreate(BaseModel):
    """
    Datos para CREAR una compra.
    """
    producto_id: int  # Obligatorio
    cantidad: int  # Obligatorio
    precio_unitario: float  # Obligatorio
    ubicacion: Optional[str] = None  # Opcional
    notas: Optional[str] = None  # Opcional
    hora: Optional[str] = None  # Opcional (HH:MM)


class CompraResponse(BaseModel):
    """
    Datos que devolvemos de una compra.
    """
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float
    total: float
    ubicacion: Optional[str]
    notas: Optional[str]
    fecha: datetime  # Automática
    hora: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================
# ESQUEMA 6: DASHBOARD / ESTADÍSTICAS
# ============================================

class DashboardResponse(BaseModel):
    """
    Datos que la app móvil pide para mostrar el dashboard.
    
    Un dashboard es una pantalla con resumen de información.
    """
    total_productos: int  # Cuántos productos hay en total
    total_stock: int  # Suma de todas las cantidades
    total_dinero: float  # Dinero en caja
    total_ventas_hoy: float  # Dinero vendido hoy
    productos_bajo_stock: int  # Cuántos productos tienen poco stock
    productos_activos: int  # Cuántos productos están activos
