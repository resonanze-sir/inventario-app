# models.py
# Aquí definimos cómo se ve cada tabla en la base de datos

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum
from datetime import datetime

# ============================================
# MODELO 1: PRODUCTOS
# ============================================
class Producto(Base):
    """
    Representa cada producto en el inventario.
    
    Cada fila en la tabla PRODUCTOS será un objeto Producto.
    """
    
    __tablename__ = "productos"  # Nombre de la tabla en la BD
    
    # COLUMNAS (los atributos de un producto)
    # Column(tipo_dato, restricciones)
    
    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True: Este es el identificador único (no puede repetirse)
    # index=True: Crea un índice para búsquedas rápidas
    
    nombre = Column(String(100), nullable=False)
    # String(100): Texto de máximo 100 caracteres
    # nullable=False: Es obligatorio (no puede estar vacío)
    
    descripcion = Column(String(500))
    # nullable es True por defecto, así que es opcional
    
    precio_costo = Column(Float, nullable=False)
    # Float: Número decimal (12.50, 99.99, etc.)
    
    precio_venta = Column(Float, nullable=False)
    # Este es el precio de venta (para calcular ganancia)
    
    sku = Column(String(50), unique=True, nullable=False)
    # unique=True: No puede haber dos productos con el mismo SKU
    # SKU = Código identificador del producto
    
    cantidad_stock = Column(Integer, default=0)
    # Integer: Número entero (cantidad de unidades)
    # default=0: Si no se especifica, comienza en 0
    
    categoria = Column(String(50))
    
    activo = Column(Integer, default=1)
    # 1 = activo, 0 = inactivo (para no eliminar, solo desactivar)
    
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    # datetime.utcnow: Automáticamente pone la fecha/hora actual
    
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # onupdate=datetime.utcnow: Se actualiza automáticamente cuando se modifica


# ============================================
# MODELO 2: VENTAS
# ============================================
class Venta(Base):
    """
    Registra cada venta realizada.
    """
    
    __tablename__ = "ventas"
    
    id = Column(Integer, primary_key=True, index=True)
    
    producto_id = Column(Integer, nullable=False)
    # Referencia al ID del producto vendido
    
    cantidad = Column(Integer, nullable=False)
    # Cuántas unidades se vendieron
    
    precio_unitario = Column(Float, nullable=False)
    # A qué precio se vendió
    
    total = Column(Float, nullable=False)
    # total = cantidad * precio_unitario
    
    metodo_pago = Column(String(50))
    # "Efectivo", "Tarjeta", "Transferencia", etc.
    
    fecha = Column(DateTime, default=datetime.utcnow)
    # Cuándo se hizo la venta


# ============================================
# MODELO 3: MOVIMIENTOS DE STOCK
# ============================================
class TipoMovimiento(str, enum.Enum):
    """
    Enum = una lista de opciones posibles
    
    Un movimiento de stock puede ser:
    - ENTRADA: Se agregó stock
    - SALIDA: Se sacó stock
    """
    ENTRADA = "entrada"
    SALIDA = "salida"


class MovimientoStock(Base):
    """
    Registra cada cambio en el stock.
    Permite ver el historial de por qué cambió.
    """
    
    __tablename__ = "movimientos_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    
    producto_id = Column(Integer, nullable=False)
    # Qué producto cambió
    
    tipo = Column(Enum(TipoMovimiento), nullable=False)
    # Es ENTRADA o SALIDA
    
    cantidad = Column(Integer, nullable=False)
    # Cuántas unidades entraron/salieron
    
    motivo = Column(String(200))
    # "Compra a proveedor", "Venta", "Daño", "Devolución", etc.
    
    fecha = Column(DateTime, default=datetime.utcnow)
    # Cuándo pasó el movimiento


# ============================================
# MODELO 4: COMPRAS
# ============================================
class Compra(Base):
    """
    Registra cada compra de productos (tejas).
    Simple: qué, cuánto, a qué precio, dónde, cuándo.
    """
    
    __tablename__ = "compras"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # QUÉ COMPRASTE
    producto_id = Column(Integer, nullable=False)
    # Qué producto compraste (ej: id del producto Tejas)
    
    cantidad = Column(Integer, nullable=False)
    # Cuántas unidades compraste
    
    # A QUÉ PRECIO
    precio_unitario = Column(Float, nullable=False)
    # A qué precio unitario ($10.50, $12, etc.)
    
    total = Column(Float, nullable=False)
    # total = cantidad × precio_unitario
    
    # DETALLES OPCIONALES
    ubicacion = Column(String(200))
    # De dónde las compraste (La Matanza, Flores, etc.)
    # Opcional
    
    notas = Column(String(500))
    # Notas: "Estado regular", "Algunas rotas", etc.
    # Opcional
    
    # FECHAS
    fecha = Column(DateTime, default=datetime.utcnow)
    # Automática: cuándo compraste (se genera sola)
    
    hora = Column(String(5))
    # Opcional: hora en formato HH:MM (14:30, 09:15, etc.)


# ============================================
# MODELO 5: TRANSACCIONES DE DINERO
# ============================================
class TipoTransaccion(str, enum.Enum):
    """
    Las transacciones pueden ser entrada o salida de dinero
    """
    ENTRADA = "entrada"
    SALIDA = "salida"


class Transaccion(Base):
    """
    Registra cada movimiento de dinero (entrada o salida).
    """
    
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    
    tipo = Column(Enum(TipoTransaccion), nullable=False)
    # ENTRADA (venta, depósito) o SALIDA (compra, gasto)
    
    monto = Column(Float, nullable=False)
    # Cuánto dinero entró o salió
    
    concepto = Column(String(200), nullable=False)
    # "Venta de remeras", "Compra de tejas", "Alquiler", etc.
    
    metodo_pago = Column(String(50))
    # "Efectivo", "Mercado Pago", "Transferencia", etc.
    
    referencia = Column(String(100))
    # Número de transacción, ID de venta, etc.
    
    fecha = Column(DateTime, default=datetime.utcnow)
    # Cuándo sucedió
    
    saldo_antes = Column(Float, default=0)
    # El dinero que había antes de esta transacción
    # Útil para auditoría
