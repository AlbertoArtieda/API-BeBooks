from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlmodel import create_engine, Session, select
from classes import *
from config import *
from hashlib import sha256
import os, binascii
import requests, json

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

def comprobarUser(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        user = session.exec(
            select(Usuarios).where(Usuarios.token == token)
            ).one()
    return user

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
def change(cambio: Cambios, user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
        cambio.ID_user_compra = user.ID_usuario

        users_vende = session.exec(
            select(Usuarios).where(Usuarios.ID_usuario == cambio.ID_user_vende)
        ).one()
        changed_book = session.exec(
            select(Libros).where(Libros.ID_libro == cambio.ID_libro)
        ).one()

        user.puntos -= 3
        users_vende.puntos += 3
        changed_book.activo = 0
        cambio.fecha = datetime.now()

        # Arreglar los cambios en las tablas
        session.add(user)
        session.add(users_vende)
        session.add(cambio)
        session.add(changed_book)
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
def givenBooks(user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_vende == user.ID_usuario, Libros.ID_libro == Cambios.ID_libro)
            ).all()

# Recibe el token del usuario y devuelve todos los lubros que ha comprado un usuario
@app.post("/gottenBooks")
def gottenBooks(user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
        return session.exec(
            select(Libros.imagen_libro,Libros.titulo,Libros.isbn,Cambios.fecha).where(Cambios.ID_user_compra == user.ID_usuario, Libros.ID_libro == Cambios.ID_libro)
            ).all()

# Devuelve todos los libros que hay en venta (activo == 1)
@app.get("/searchBooks")
def SearchBooks():
    with Session(engine) as session:
        return session.exec(
            select(Libros.ID_libro, Libros.imagen_libro, Libros.titulo, Libros.isbn, Libros.ID_usuario).where(Libros.activo == 1)
            ).all()

# Recibe el token del usuario y devuelve todos los datos del usuario que ha hecho login para usarlos en la app
@app.get("/userData")
def userData(token: str = Header(default=None)):
    token = token.replace('"','')
    with Session(engine) as session:
        return session.exec(
            select(Usuarios.nombre_apellidos, Usuarios.usuario, Provincia.provincia, Usuarios.cp, Usuarios.direccion, Usuarios.email, Usuarios.telefono, Usuarios.imagen_perfil, Usuarios.puntos).where(Usuarios.token == token, Usuarios.ID_provincia == Provincia.ID_provincia)
            ).one()

# Recibe el token del usuario y devuelve todos los libros que el usuario tiene en venta (activo == 1)
@app.get("/userBooks")
def SearchBooks(user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
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

# Devuelve los usuarios que tengan el mismo cp
@app.get("/nearUsers")
def SearchBooks(user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
        return session.exec(
                select(Usuarios.imagen_perfil, Usuarios.ID_usuario, Usuarios.nombre_apellidos).where(Usuarios.cp == user.cp)
            ).all()
            
# Muestra libros subidos de una perfil ajeno
@app.get("/seeProfile")
def show_different_profile(id: int = Header(default=None)):
    with Session(engine) as session:
        user_books = session.exec(
            select(Libros.imagen_libro, Libros.titulo, Libros.isbn, Libros.ID_usuario, Libros.ID_libro).where(Libros.ID_usuario == id).where(Libros.activo == 1)
        ).all()
        return user_books

# Devuelve la imagen de perfil y el nombre del propietario de un libro subido
@app.get("/showOwner")
def show_different_profile(id: int = Header(default=None)):
    with Session(engine) as session:
        owner_info = session.exec(
            select(Usuarios.nombre_apellidos, Usuarios.imagen_perfil).where(Usuarios.ID_usuario == id)
        ).first()
        return owner_info

# Borra el token del usuario para poder hacer LogOut
@app.post("/deleteToken")
def show_different_profile(user : Usuarios = Depends(comprobarUser)):
    with Session(engine) as session:
        user.token = ""
        session.add(user)
        session.commit()
        session.refresh(user)

@app.post("/getbookinfo")
def get_book_info(isbn: str = Header(default=None)):
    result = requests.get("https://www.googleapis.com/books/v1/volumes?q=" + isbn)

    book = result.json()
    items = book.get("items")

    encoded = json.dumps(items)
    decoded = json.loads(encoded)
    
    titulo = decoded[0]["volumeInfo"]["title"]
    print(titulo)
    editorial = decoded[0]["volumeInfo"].get("publisher") # get() es para que devuelva "None" en vez de un error si no encuentra la clave "publisher"
    
    charactersToRemove = (",", ".", ":")
    for i in charactersToRemove:
        titulo = titulo.replace(i, "")

    cursos = ("eso", "ESO", "bachillerato", "Bachillerato", "BACHILLERATO", "primaria", "Primaria", "PRIMARIA")
    for i in cursos:
        if i in titulo.split():
            i_curso = titulo.split().index(i)
            curso = titulo.split()[i_curso-1] + " " + titulo.split()[i_curso]
            
            titulo = titulo.replace(curso, "")

            if editorial != None:
                return titulo, curso, editorial
            else:
                return titulo, curso, "Sin editorial"
    return "No es un libro de instituto o colegio"