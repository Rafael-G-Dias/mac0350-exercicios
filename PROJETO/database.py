from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, create_engine

# 1. MODELOS DE DADOS 

class Time(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cor_camisa: str
    
    capitao_id: Optional[int] = Field(default=None)
    
    jogadores: List["Jogador"] = Relationship(back_populates="time")


class Jogador(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    posicao: str
    nota: int  # Pode ser de 1 a 10 (nível técnico)
    
    # Chave Estrangeira: Aponta para a tabela 'time'. 
    # É Optional porque o jogador pode estar sem time definido ainda.
    time_id: Optional[int] = Field(default=None, foreign_key="time.id")
    
    # Relação Lado 'Muitos': O jogador enxerga apenas o seu próprio time
    time: Optional[Time] = Relationship(back_populates="jogadores")


# 2. CONFIGURAÇÃO DO BANCO

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine é o "motor" que traduz Python para código SQL. 
# echo=True faz o terminal imprimir os comandos SQL rodando por baixo dos panos.
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    # Função para criar o arquivo .db e as tabelas caso não existam
    SQLModel.metadata.create_all(engine)