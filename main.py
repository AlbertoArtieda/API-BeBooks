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
        usuario.passwordLog = sha256().hexdigest()
        usuario = session.exec(
            select(Usuarios).where(Usuarios.usuario == usuario.nombreLog and Usuarios.password == usuario.passwordLog)
        ).first()
        usuario.token = usuario.usuario + str(datetime.datetime.now())
        usuario.token = sha256().hexdigest()
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/dataUser")
def dataUser(usuario: Login):
    with Session(engine) as session:
        return session.exec(
            select(Usuarios).where(Usuarios.usuario == usuario.nombreLog)
            ).first()

@app.post("/register")
def register(usuario: Usuarios):
    with Session(engine) as session:
        usuario.password = sha256().hexdigest()
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

@app.post("/saleshistory")
def Saleshistory(usuario: Usuarios):
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_vende == usuario.ID_usuario and Libros.activo == 0)
            ).all()

@app.get("/searchBooks")
def SearchBooks():
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro, Libros.titulo, Libros.isbn).where(Libros.activo == 1)
            ).all()
