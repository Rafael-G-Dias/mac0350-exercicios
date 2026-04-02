from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

db_usuarios = []

class Usuario(BaseModel):
    nome: str
    idade: int

@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()
    

@app.post("/users")
async def add_user(usuario: Usuario):
    db_usuarios.append(usuario.dict())
    return f"Usuário {usuario.nome} (Idade: {usuario.idade}) adicionado!"


@app.get("/users")
async def get_users(index: Optional[int] = Query(None)):
    if index is not None:
        try:
            return db_usuarios[index]
        except IndexError:
            return "Erro: Índice não encontrado na lista."
    
    return db_usuarios if db_usuarios else "A lista está vazia."



@app.delete("/users")
async def clear_users():
    db_usuarios.clear()
    return "Todos os usuários foram removidos com sucesso."