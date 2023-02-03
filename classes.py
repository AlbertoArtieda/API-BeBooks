from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Usuarios(SQLModel, table=True):
    ID_usuario: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    apellidos: str
    ID_provincia: int
    password: str
    cp: int
    email: str
    telefono: int
    direccion: str
    imagen_perfil: Optional[str] = Field(default=None)
    puntos: int

class Libros(SQLModel, table=True):
    ID_libro: Optional[int] = Field(default=None, primary_key=True)
    isbn: int
    ID_editorial: int
    titulo: str
    curso: str
    puntos: Optional[int] = Field(default=3)
    ID_usuario: int
    activo: Optional[int] = Field(default=1)
    imagen_libro: str

class Cambios(SQLModel, table=True):
    ID_cambio: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime
    ID_user_compra: int
    ID_user_vende: int
    ID_libro: int

class Login(SQLModel):
    nombre: str
    password: str