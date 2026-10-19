# database.py
# Este archivo configura la conexión a la base de datos

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# CONNECTION STRING
# Es como la "dirección" de la base de datos
# Formato: postgresql://usuario:contraseña@host:puerto/nombre_bd
DATABASE_URL = "postgresql://postgres:123asd@localhost:5432/inventario_db"

# create_engine: Crea la conexión con la BD
# echo=True: Muestra en consola las consultas SQL (útil para aprender)
engine = create_engine(DATABASE_URL, echo=True)

# SessionLocal: Herramienta para hacer consultas a la BD
# Cada consulta necesita una "sesión" (como abrir un archivo)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: Clase padre de todos los modelos
# Todos nuestros modelos van a heredar de esto
Base = declarative_base()

# Función para obtener la BD en cada petición
def get_db():
    """
    Esta función crea una conexión a la BD para cada petición
    y la cierra cuando termina.
    
    Es importante cerrar la conexión para no "colgar" recursos.
    """
    db = SessionLocal()
    try:
        yield db  # "yield" es como un return pero permite continuar después
    finally:
        db.close()  # Cierra la conexión
