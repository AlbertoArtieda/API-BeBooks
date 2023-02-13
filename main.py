from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from classes import *
from config import *
import hashlib

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

@app.get("/health")
def health_check():
    return "OK"

@app.post("/login", status_code=status.HTTP_201_CREATED)
def login(usuario: Login):
    with Session(engine) as session:
        usuario.password = hashlib.new("sha256",usuario.password).hexdigest()
        usuario = session.exec(
            select(Usuarios).where(Usuarios.usuario == usuario.nombre and Usuarios.password == usuario.password)
        ).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/register")
def register(usuario: Usuarios):
    with Session(engine) as session:
        usuario.password = hashlib.new("sha256",usuario.password).hexdigest()
        session.add(usuario)
        session.commit()

@app.post("/newbook")
def register(libro: Libros):
    with Session(engine) as session:
        session.add(libro)
        session.commit()

@app.post("/change")
def register(cambio: Cambios):
    with Session(engine) as session:
        session.add(cambio)
        session.commit()

@app.get("/getProvincias")
def getProvincias():
    with Session(engine) as session:
        return session.exec(
            select(Provincia.provincia).order_by(Provincia.ID_provincia)
            ).all()

@app.get("/Saleshistory")
def Saleshistory(usuario: Usuarios):
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_vende == usuario.ID_usuario and Libros.activo == 0)
            ).all()


@app.get("/prueba", response_model=UsuariosLeer)
def prueba():
    session = Session(engine)
    usuario = session.exec(select(Usuarios)).first()
    print(usuario.provincia.provincia)
    return usuario