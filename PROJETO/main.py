from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from database import create_db_and_tables, engine, Jogador, Time
from typing import Optional
import random

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="layout.html"
    )


# ROTAS DE JOGADORES (CRUD)


# 1. READ (Listar todos e Buscar)
@app.get("/jogadores")
async def pagina_jogadores(request: Request, q: Optional[str] = ""):
    # Abrimos a sessão
    with Session(engine) as session:
        query = select(Jogador)
        
        if q:
            query = query.where(Jogador.nome.contains(q))
            
        query = query.order_by(Jogador.nome)
        jogadores = session.exec(query).all()
        
        # Se o alvo for a tabela, sabemos que a requisição veio da barra de busca.
        if request.headers.get("hx-target") == "tabela-jogadores":
            return templates.TemplateResponse(
                request=request, 
                name="partials/lista_jogadores.html",
                context={"jogadores": jogadores}
            )
            
        # Se o alvo for o #conteudo (clique no menu) ou uma requisição normal,
        # retornamos a página HTML completa (com o formulário).
        return templates.TemplateResponse(
            request=request, 
            name="jogadores.html",
            context={"jogadores": jogadores}
        )

# 1.5. READ (Listar apenas 1 jogador - Usado no botão Cancelar da edição)
@app.get("/jogador/{id}")
async def get_jogador_unico(request: Request, id: int):
    with Session(engine) as session:
        jogador = session.get(Jogador, id)
        
    return templates.TemplateResponse(
        request=request, 
        name="partials/lista_jogadores.html",
        context={"jogadores": [jogador]} # Passamos como lista de 1 item por causa do 'for'
    )

# 2. CREATE (Adicionar novo Jogador)
@app.post("/jogador")
async def criar_jogador(
    request: Request,
    nome: str = Form(...),
    posicao: str = Form(...),
    nota: int = Form(...)
):
    novo_jogador = Jogador(nome=nome, posicao=posicao, nota=nota)
    with Session(engine) as session:
        session.add(novo_jogador)
        session.commit()
        session.refresh(novo_jogador)
        
        # Retorna o fragmento HTML renderizado para o HTMX injetar no fim da tabela
        return templates.TemplateResponse(
            request=request, 
            name="partials/lista_jogadores.html",
            context={"jogadores": [novo_jogador]} 
        )

# 3. UPDATE (A - Retornar o formulário de edição com a lista de times)
@app.get("/jogador/{id}/editar")
async def form_editar_jogador(request: Request, id: int):
    with Session(engine) as session:
        jogador = session.get(Jogador, id)
        # Buscamos todos os times disponíveis no banco para preencher o <select>
        times = session.exec(select(Time)).all() 
        
    return templates.TemplateResponse(
        request=request, 
        name="partials/form_edicao_nota.html",
        context={"jogador": jogador, "times": times}
    )

# 3. UPDATE (B - Salvar os dados editados, incluindo o time_id)
@app.put("/jogador/{id}")
async def atualizar_jogador(
    request: Request, 
    id: int, 
    nota: int = Form(...),
    # Recebemos como string para evitar erros do FastAPI caso o campo venha vazio do HTML
    time_id: Optional[str] = Form(None) 
):
    with Session(engine) as session:
        jogador = session.get(Jogador, id)
        if not jogador:
            return HTMLResponse("Erro: Jogador não encontrado", status_code=404)
        
        jogador.nota = nota
        
        # Tratamento seguro: Se for vazio ("") ou None, removemos do time. 
        # Caso contrário, convertemos para inteiro.
        if not time_id:
            jogador.time_id = None
        else:
            jogador.time_id = int(time_id)
            
        session.add(jogador)
        session.commit()
        session.refresh(jogador)
        
    return templates.TemplateResponse(
        request=request, 
        name="partials/lista_jogadores.html",
        context={"jogadores": [jogador]}
    )

# 4. DELETE (Remover)
@app.delete("/jogador/{id}")
async def deletar_jogador(id: int):
    with Session(engine) as session:
        jogador = session.get(Jogador, id)
        if jogador:
            session.delete(jogador)
            session.commit()
            
    # Retornamos uma string vazia. 
    # Como o hx-swap é "outerHTML", o HTMX vai substituir a <tr> por "" (apagando-a da tela).
    return HTMLResponse(content="")


# ROTAS DE TIMES (CRUD)


# 1. READ: Carrega a página de times listando todos do banco
@app.get("/times")
async def pagina_times(request: Request):
    with Session(engine) as session:
        times = session.exec(select(Time)).all()
        jogadores = session.exec(select(Jogador)).all() # Busca os jogadores
        
        return templates.TemplateResponse(
            request=request, 
            name="times.html",
            context={"times": times, "jogadores": jogadores} # Envia para o HTML
        )

# 2. CREATE: Recebe os dados do form, cria o time e devolve a linha HTML
@app.post("/time")
async def criar_time(
    request: Request,
    nome: str = Form(...),
    cor_camisa: str = Form(...),
    capitao_id: Optional[str] = Form(None) # Recebe o ID do capitão
):
    # Se recebeu um capitão, converte pra inteiro, senão fica None
    cap_id_convertido = int(capitao_id) if capitao_id else None
    
    novo_time = Time(nome=nome, cor_camisa=cor_camisa, capitao_id=cap_id_convertido)
    
    with Session(engine) as session:
        session.add(novo_time)
        session.commit()
        session.refresh(novo_time)
        
        return templates.TemplateResponse(
            request=request, 
            name="partials/lista_times.html",
            context={"times": [novo_time]}
        )
    
# 
@app.get("/gerar-times")
async def gerar_times(request: Request):
    with Session(engine) as session:
        jogadores = session.exec(select(Jogador)).all()
        times_db = session.exec(select(Time)).all()

        if len(jogadores) < 2:
            return HTMLResponse("<p style='color: red;'>Adicione pelo menos 2 jogadores!</p>")
        if len(times_db) < 2:
            return HTMLResponse("<p style='color: red;'>Crie pelo menos 2 times na aba Gestão de Times!</p>")

        # 1. Escolhe 2 times reais aleatoriamente
        times_escolhidos = random.sample(times_db, 2)
        time_a, time_b = times_escolhidos[0], times_escolhidos[1]

        jogadores_time_a = []
        jogadores_time_b = []
        jogadores_disponiveis = jogadores.copy()

        # 2. Garante os capitães em seus respectivos times
        if time_a.capitao_id:
            cap_a = next((j for j in jogadores_disponiveis if j.id == time_a.capitao_id), None)
            if cap_a:
                jogadores_time_a.append(cap_a)
                jogadores_disponiveis.remove(cap_a)

        if time_b.capitao_id:
            cap_b = next((j for j in jogadores_disponiveis if j.id == time_b.capitao_id), None)
            if cap_b:
                jogadores_time_b.append(cap_b)
                jogadores_disponiveis.remove(cap_b)

        # 3. Ordena os restantes do melhor para o pior
        jogadores_disponiveis.sort(key=lambda j: j.nota, reverse=True)

        # 4. Algoritmo Guloso (Sempre dá o próximo craque para o time que está perdendo na soma das notas)
        for jogador in jogadores_disponiveis:
            soma_a = sum(j.nota for j in jogadores_time_a)
            soma_b = sum(j.nota for j in jogadores_time_b)

            if soma_a <= soma_b:
                jogadores_time_a.append(jogador)
            else:
                jogadores_time_b.append(jogador)

        media_a = round(sum(j.nota for j in jogadores_time_a) / len(jogadores_time_a), 1) if jogadores_time_a else 0
        media_b = round(sum(j.nota for j in jogadores_time_b) / len(jogadores_time_b), 1) if jogadores_time_b else 0

        return templates.TemplateResponse(
            request=request,
            name="partials/resultado_racha.html",
            context={
                "time_a": time_a, "jogadores_a": jogadores_time_a, "media_a": media_a,
                "time_b": time_b, "jogadores_b": jogadores_time_b, "media_b": media_b
            }
        )

#DELETE: remove um time criado  
@app.delete("/time/{id}")
async def deletar_time(id: int):
    with Session(engine) as session:
        time = session.get(Time, id)
        if time:
            # 1. Procuramos jogadores vinculados a este time
            statement = select(Jogador).where(Jogador.time_id == id)
            jogadores_vinculados = session.exec(statement).all()
            
            # 2. Desvinculamos eles 
            for jogador in jogadores_vinculados:
                jogador.time_id = None
                session.add(jogador)
            
            # 3. Agora podemos deletar o time com segurança
            session.delete(time)
            session.commit()
            
    # Retornamos vazio para o HTMX remover a linha da tabela
    return HTMLResponse(content="")