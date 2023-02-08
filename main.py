from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, create_engine, Session, select
from classes import Login, Usuarios, Libros, Cambios, UsuariosBase
from config import *

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

@app.get("/health")
def health_check():
    return "OK"

@app.post("/login")
def login(usuario: Login):
    with Session(engine) as session:
        statement = select(Usuarios).where(UsuariosBase.usuario == usuario.nombre and Usuarios.password == usuario.password)
        print(len(session.exec(statement).all()) == 1)
        if (len(session.exec(statement).all()) == 1):
            return JSONResponse(status_code=status.HTTP_201_CREATED)
        else:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED)

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

