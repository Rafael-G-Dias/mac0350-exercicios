# Gestor de Partidas (Rachas)

## Descrição do Projeto
Um web app simples desenhado para ajudar organizadores de futebol amador a gerenciar os jogadores e distribuir as equipes das partidas. O sistema permite cadastrar os jogadores, atribuir notas técnicas a eles e organizá-los em times, tudo em uma interface responsiva.

## Especificações Técnicas
- **Backend:** FastAPI
- **Banco de Dados:** Relacional (SQL)
- **Frontend:** HTML, CSS, JavaScript (Interfaces responsivas para Mobile e PC)
- **Interatividade:** HTMX (para requisições assíncronas e renderização dinâmica)

## Modelos de Dados
O projeto contará com dois modelos principais, estabelecendo uma relação **One to Many (1:N)**:
1. **Time:** Armazena as equipes da partida (Ex: Nome da equipe, Cor da camisa).
2. **Jogador:** Armazena os dados dos atletas (Ex: Nome, Posição, Nota/Nível técnico, ID do Time ao qual pertence).

## Funcionalidades e Operações HTMX (CRUD)
- **Create (`hx-post`):** Interface para adicionar novos jogadores à lista geral e criar novos times.
- **Read (`hx-get`):** Listagem de todos os jogadores cadastrados e visualização das escalações dos times.
- **Update (`hx-put`):** Atualizar a nota técnica de um jogador ou transferi-lo de um time para outro.
- **Delete (`hx-delete`):** Remover um jogador inativo do banco de dados.

## Funcionalidades Extras e Fictícias
- **Busca de Jogadores:** Uma barra de pesquisa para buscar jogadores específicos pelo nome utilizando HTMX, filtrando a lista em tempo real.
- **Gerador Automático de Times (Funcionalidade Simulada):** Um botão na interface que simula a divisão automática dos jogadores cadastrados em duas equipes balanceadas com base em suas notas técnicas. (Nota: Para o escopo desta fase do projeto, a lógica algorítmica de balanceamento perfeito é fictícia/simulada, focando na demonstração da interface e requisição via HTMX).