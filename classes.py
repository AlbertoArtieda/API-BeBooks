from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class Provincia(SQLModel, table=True):
    ID_provincia: Optional[int] = Field(default=None, primary_key=True)
    provincia: str

class UsuariosBase(SQLModel):
    nombre_apellidos: str
    usuario: str
    token: Optional[str] = Field(default=None)
    ID_provincia: int
    cp: int
    email: str
    telefono: int
    direccion: str
    imagen_perfil: Optional[str] = Field(default=None)
    puntos: Optional[int] = Field(default=0)

class Usuarios(UsuariosBase, table=True):
    ID_usuario: Optional[int] = Field(default=None, primary_key=True)
    password: str
    provincia: Provincia = Relationship(
        sa_relationship_kwargs= {
            "primaryjoin": "foreign(Provincia.ID_provincia) == Usuarios.ID_provincia",
            "uselist": False
        }
    )

class LibroBase(SQLModel):
    titulo: str
    curso: str
    puntos: Optional[int] = Field(default=3)
    ID_usuario: int
    activo: Optional[int] = Field(default=1)
    imagen_libro: str
    editorial: str

class Libros(LibroBase, table=True):
    ID_libro: Optional[int] = Field(default=None, primary_key=True)
    isbn: str = Field(index=True)
    usuario: Usuarios = Relationship(
        sa_relationship_kwargs= {
            "primaryjoin": "foreign(Usuarios.ID_usuario) == Libros.ID_usuario",
            "uselist": False
        }
    )

class CambioBase(SQLModel):
    ID_user_compra: int
    ID_user_vende: int
    ID_libro: int

class Cambios(CambioBase, table=True):
    ID_cambio: Optional[int] = Field(default=None, primary_key=True)
    fecha: Optional [datetime] = Field(default=None)
    user_compra: Usuarios = Relationship(
        sa_relationship_kwargs= {
            "primaryjoin": "foreign(Usuarios.ID_usuario) == Cambios.ID_user_compra",
            "uselist": False
        }
    )
    user_vende: Usuarios = Relationship(
        sa_relationship_kwargs= {
            "primaryjoin": "foreign(Usuarios.ID_usuario) == Cambios.ID_user_vende",
            "uselist": False
        }
    )
    libro: Libros = Relationship(
        sa_relationship_kwargs= {
            "primaryjoin": "foreign(Libros.ID_libro) == Cambios.ID_libro",
            "uselist": False
        }
    )

class Login(SQLModel):
    nombre: str
    password: str
