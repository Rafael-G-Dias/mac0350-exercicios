from fastapi import FastAPI, Request, Response, Depends, HTTPException, status, Cookie
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated, Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

db_usuarios = []

class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

class LoginData(BaseModel):
    nome: str
    senha: str

def get_active_user(session_user: Annotated[Optional[str], Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=401, detail="Não autorizado. Faça login.")
    user = next((u for u in db_usuarios if u["nome"] == session_user), None)
    if not user:
        raise HTTPException(status_code=401, detail="Sessão inválida.")
    
    return user

@app.get("/")
async def pagina_registro(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="registro.html"
    )

@app.post("/users")
async def criar_usuario(usuario: Usuario):
    if any(u["nome"] == usuario.nome for u in db_usuarios):
        raise HTTPException(status_code=400, detail="Usuário já existe")
    db_usuarios.append(usuario.model_dump()) 
    return {"mensagem": "Usuário criado com sucesso!"}

@app.get("/login")
async def pagina_login(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="login.html"
    )

@app.post("/login")
async def fazer_login(dados: LoginData, response: Response):
    usuario_encontrado = next((u for u in db_usuarios if u["nome"] == dados.nome and u["senha"] == dados.senha), None)
    if not usuario_encontrado:
        raise HTTPException(status_code=401, detail="Credenciais incorretas")
    response.set_cookie(key="session_user", value=dados.nome)
    return {"mensagem": "Login efetuado com sucesso!"}

@app.get("/home")
async def pagina_home(request: Request, user: dict = Depends(get_active_user)):
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"user": user}
    )