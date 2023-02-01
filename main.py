from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
import classes
from config import *

engine = create_engine(f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}")

app = FastAPI()

print(engine)

@app.get("/health")
def health_check():
    return "OK"


