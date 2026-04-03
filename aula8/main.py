from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

estado = {"curtidas": 0}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="layout.html")

@app.get("/aba/curtidas")
async def aba_curtidas(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="curtidas.html", 
        context={"curtidas": estado["curtidas"]}
    )

@app.get("/aba/jupiter")
async def aba_jupiter(request: Request):
    return templates.TemplateResponse(request=request, name="jupiter.html")

@app.get("/aba/professor")
async def aba_professor(request: Request):
    return templates.TemplateResponse(request=request, name="professor.html")

@app.post("/curtir")
async def curtir(request: Request):
    estado["curtidas"] += 1
    return templates.TemplateResponse(
        request=request, 
        name="curtidas.html", 
        context={"curtidas": estado["curtidas"]}
    )

@app.delete("/curtir")
async def resetar(request: Request):
    estado["curtidas"] = 0
    return templates.TemplateResponse(
        request=request, 
        name="curtidas.html", 
        context={"curtidas": estado["curtidas"]}
    )