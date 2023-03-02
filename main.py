from fastapi import FastAPI, HTTPException, status, Header
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from classes import *
from config import *
from hashlib import sha256
import datetime
import os, binascii

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

# Comprobación de la conexión
@app.get("/health")
def health_check():
    return "OK"

# Recibe un usuario y password y la encripa. Comprueba que existan los datos en la BBDD y crea un token para dicho usuario
@app.post("/login", status_code=status.HTTP_201_CREATED)
def login(usuario: Login):
    with Session(engine) as session:
        usuario.password = sha256(usuario.password.encode()).hexdigest()
        user = session.exec(
            select(Usuarios).where(Usuarios.password == usuario.password).where(Usuarios.usuario == usuario.nombre)
        ).one()
        user.token = binascii.b2a_hex(os.urandom(20))
        session.add(user)
        session.commit()
        session.refresh(user)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user.token

# Recibe los datos del usuario, encripta la password y los registra en la BBDD
@app.post("/register")
def register(usuario: Usuarios):
    with Session(engine) as session:
        usuario.password = sha256(usuario.password.encode()).hexdigest()
        session.add(usuario)
        session.commit()

# Recibe los datos de la app y los añade a la BBDD
@app.post("/newbook")
def newbook(libro: Libros):
    with Session(engine) as session:
        session.add(libro)
        session.commit()

# Al confirmar un cambio se añaden los datos de dicho cambio a la BBDD
@app.post("/change")
def change(cambio: Cambios):
    with Session(engine) as session:
        session.add(cambio)
        session.commit()

# Devuelve todos los nombres de las provincias que hay en BBDD para usarlos en un DropDownList de la app
@app.get("/getProvincias")
def getProvincias():
    with Session(engine) as session:
        return session.exec(
            select(Provincia.provincia).order_by(Provincia.ID_provincia)
            ).all()

# Recibe el token del usuario y devuelve todos los libros que ha vendido un usuario
@app.get("/givenBooks")
def givenBooks(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        user = session.exec(
            select(Usuarios).where(Usuarios.token == token)
            ).one()
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_vende == user.ID_usuario, Libros.ID_libro == Cambios.ID_libro)
            ).all()

# Recibe el token del usuario y devuelve todos los lubros que ha comprado un usuario
@app.post("/gottenBooks")
def gottenBooks(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        user = session.exec(
            select(Usuarios).where(Usuarios.token == token)
            ).one()
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_compra == user.ID_usuario, Libros.ID_libro == Cambios.ID_libro)
            ).all()

# Devuelve todos los libros que hay en venta (activo == 1)
@app.get("/searchBooks")
def SearchBooks():
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro, Libros.titulo, Libros.isbn).where(Libros.activo == 1)
            ).all()

# Recibe el token del usuario y devuelve todos los datos del usuario que ha hecho login para usarlos en la app
@app.get("/userData")
def userData(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        return session.exec(
            select(Usuarios.nombre_apellidos, Usuarios.usuario, Usuarios.ID_provincia, Usuarios.cp, Usuarios.direccion, Usuarios.email, Usuarios.telefono, Usuarios.imagen_perfil, Usuarios.puntos).where(Usuarios.token == token)
            ).one()

# Recibe el token del usuario y devuelve todos los libros que el usuario tiene en venta (activo == 1)
@app.get("/userBooks")
def SearchBooks(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        user = session.exec(
            select(Usuarios).where(Usuarios.token == token)
            ).one()
        return session.exec(
            select(Libros.imagen_libro, Libros.titulo, Libros.isbn).where(Libros.ID_usuario == user.ID_usuario).where(Libros.activo == 1)
            ).all()

# Recibe la id del libro que se quiere "eliminar" y lo pone con activo a 0
@app.get("/deleteBook")
def deleteBook(id: int = Header(default=None)):
    with Session(engine) as session:
        book = session.exec(
            select(Libros).where(Libros.ID_libro == id)
            ).one()
        book.activo = 0
        session.add(book)
        session.commit()
        session.refresh(book)