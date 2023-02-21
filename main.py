from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from classes import *
from config import *
from hashlib import sha256
import datetime

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

@app.get("/health")
def health_check():
    return "OK"

@app.post("/login", status_code=status.HTTP_201_CREATED)
def login(usuario: Login):
    with Session(engine) as session:
        usuario.password = sha256(usuario.password.encode()).hexdigest()
        user = session.exec(
            select(Usuarios).where(Usuarios.password == usuario.password).where(Usuarios.usuario == usuario.nombre)
        ).one()
        user.token = user.usuario + str(datetime.datetime.now())
        user.token = sha256(user.token.encode()).hexdigest()
        session.add(user)
        session.commit()
        session.refresh(user)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user.token

@app.post("/register")
def register(usuario: Usuarios):
    with Session(engine) as session:
        usuario.password = sha256(usuario.password.encode()).hexdigest()
        session.add(usuario)
        session.commit()

@app.post("/newbook")
def newbook(libro: Libros):
    with Session(engine) as session:
        session.add(libro)
        session.commit()

@app.post("/change")
def change(cambio: Cambios):
    with Session(engine) as session:
        session.add(cambio)
        session.commit()

@app.get("/getProvincias")
def getProvincias():
    with Session(engine) as session:
        return session.exec(
            select(Provincia.provincia).order_by(Provincia.ID_provincia)
            ).all()

@app.post("/givenBooks")
def givenBooks(usuario: Login):
    with Session(engine) as session:
        user = session.exec(
            select(Usuarios).where(Usuarios.token == usuario.token)
        ).one()
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.user_vende == user.ID_usuario)
            ).all()

@app.get("/searchBooks")
def SearchBooks():
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro, Libros.titulo, Libros.isbn).where(Libros.activo == 1)
            ).all()
