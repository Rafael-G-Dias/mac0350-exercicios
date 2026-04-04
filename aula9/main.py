from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/alunos")
async def listar_alunos(request: Request, q: str = "", page: int = 1):
    ITENS_POR_PAGINA = 10
    deslocamento = (page - 1) * ITENS_POR_PAGINA

    with Session(engine) as session:
        query = select(Aluno)
        if q:
            query = query.where(Aluno.nome.contains(q))
        query = query.order_by(Aluno.nome)
        resultados = session.exec(query.offset(deslocamento).limit(ITENS_POR_PAGINA + 1)).all()
        tem_proximo = len(resultados) > ITENS_POR_PAGINA
        alunos_para_exibir = resultados[:ITENS_POR_PAGINA] 

    return templates.TemplateResponse(
        request=request,
        name="lista_alunos.html",
        context={
            "alunos": alunos_para_exibir,
            "q": q,           
            "page": page,      
            "tem_proximo": tem_proximo
        }
    )