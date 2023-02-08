from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from classes import Login, Usuarios, UsuariosLeer, Libros, Cambios
from config import *

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

@app.get("/health")
def health_check():
    return "OK"

@app.post("/login", status_code=status.HTTP_201_CREATED)
def login(usuario: Login):
    with Session(engine) as session:
        usuario = session.exec(
            select(Usuarios).where(Usuarios.usuario == usuario.nombre and Usuarios.password == usuario.password)
        ).first()
        if not usuario:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/register")
def register(usuario: Usuarios):
    with Session(engine) as session:
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

@app.get("/prueba", response_model=UsuariosLeer)
def prueba():
    session = Session(engine)
    usuario = session.exec(select(Usuarios)).first()
    print(usuario.provincia.provincia)
    return usuario