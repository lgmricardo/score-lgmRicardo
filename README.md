# Score — Football Analytics Dashboard ⚽

Aplicação web para visualização e análise de dados de futebol em tempo real via API-Football v3, com motor de machine learning embutido.

**Stack:** Vue.js 3 + Tailwind CSS (Frontend) · Express/Node.js (BFF) · FastAPI/Python (Backend ML)

---

## Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Iniciar](#como-iniciar)
- [Funcionalidades](#funcionalidades)
- [Análise ML — Detalhes](#análise-ml--detalhes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Arquitetura](#arquitetura)
- [Troubleshooting](#troubleshooting)

---

## Requisitos

### Software

| Software | Versão mínima | Verificar |
|----------|---------------|-----------|
| Python   | 3.10+         | `python3 --version` |
| Node.js  | 18.0+         | `node --version` |
| npm      | 9.0+          | `npm --version` |

### Chave da API

Obtenha sua chave gratuita em [api-sports.io](https://api-sports.io) e configure em `backend/.env`.

---

## Instalação

### 1. Backend (FastAPI + Python)

```bash
cd backend

# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Instalar dependências
pip install -r requirements.txt

# Criar .env
cat > .env << 'EOF'
API_KEY=sua_chave_aqui
DEBUG=True
CACHE_TTL=3600
EOF
```

**Dependências Python (`requirements.txt`):**
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
python-dotenv==1.0.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
shap>=0.41.0
```

> `shap` é opcional — o sistema funciona sem ela, mas os valores SHAP ficarão indisponíveis na UI. Os gráficos de Feature Importance exibem apenas RF Importance quando SHAP não está instalado.

---

### 2. BFF — Back-For-Front (Express/Node.js)

```bash
cd bff
npm install

cat > .env << 'EOF'
BACKEND_URL=http://localhost:8000
PORT=3001
NODE_ENV=development
EOF
```

---

### 3. Frontend (Vue.js 3 + Vite)

```bash
cd frontend
npm install
```

---

## Como Iniciar

### Opção A — Script automático (recomendado)

```bash
chmod +x start.sh   # apenas na primeira vez

./start.sh start    # iniciar todos os serviços
./start.sh stop     # parar tudo
./start.sh restart  # reiniciar tudo
./start.sh status   # ver status de cada serviço
```

### Opção B — Manual (3 terminais)

**Terminal 1 — Backend:**
```bash
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — BFF:**
```bash
cd bff && npm run dev
```

**Terminal 3 — Frontend:**
```bash
cd frontend && npm run dev
```

### URLs

| Serviço           | URL                           |
|-------------------|-------------------------------|
| Frontend          | http://localhost:5173         |
| BFF               | http://localhost:3001         |
| Backend (FastAPI) | http://localhost:8000         |
| Swagger UI        | http://localhost:8000/docs    |

---

## Funcionalidades

### Dashboard
Visão geral com partidas do dia, próximas partidas e total de ligas disponíveis.

### Ao Vivo
Partidas em andamento com atualização automática a cada 30 segundos. Exibe placar, minuto, status e ícones dos times. Botão de pausa/retomada do auto-refresh.

### Ligas
Listagem de todas as ligas retornadas pela API com busca por nome. Clique numa liga para navegar diretamente à tabela de classificação com a temporada 2024 pré-selecionada.

### Tabela de Classificação
Tabela completa com colunas **J, V, E, D, GF, GC, Saldo e Pts**. As linhas recebem coloração por zona competitiva:

| Cor | Zona |
|-----|------|
| Âmbar | Candidato ao título (top ~10%) |
| Azul | Zona europeia (top ~30%) |
| Cinza | Meio-tabela |
| Vermelho | Zona de rebaixamento (bottom ~20%) |

As ligas disponíveis nos selects são carregadas dinamicamente da API — todas as ligas presentes na sua conta são exibidas automaticamente.

Clique em qualquer time para abrir o **Perfil do Time** (forma recente e próximas partidas).

### Artilheiros
Top artilheiros por liga e temporada. Cada card exibe gols, assistências, jogos disputados e média de gols por jogo. Ligas carregadas dinamicamente.

### Exportar Dados
Exportação em CSV com filtros por liga, temporada, período de datas e campos selecionáveis.

Tipos disponíveis: **Partidas · Classificação · Artilheiros · Lesões**

### Análise ML
Motor de análise estatística e machine learning. Detalhes na próxima seção.

---

## Análise ML — Detalhes

A aba Análise é dividida em 5 grupos de sub-abas separados visualmente:

**Grupo 1 — Estatísticas base**

| Sub-aba | Algoritmos | Gráficos |
|---------|------------|----------|
| Classificação | Isolation Forest · Z-Score · LOF | Scatter Posição×Pontos · Z-Score bar · **Boxplot por zona** |
| Artilheiros | Isolation Forest · Z-Score · LOF | Bubble Gols×Assist · Eficiência bar · **Boxplot Gols** |

**Grupo 2 — Análises avançadas**

| Sub-aba | Algoritmos | Gráficos |
|---------|------------|----------|
| Lesões | Z-Score por time | Bar times · Doughnut tipos |
| Multi-Liga | Normalização min-max | Radar comparativo · Bar gols/jogo |
| Previsões | Regressão Linear (R²) | Scatter + curva · Bar projetado · **Linha trajetória** |

**Grupo 3 — Machine Learning clássico**

| Sub-aba | Algoritmos | Gráficos |
|---------|------------|----------|
| Clusters | K-Means (4 grupos) | Scatter Ataque×Defesa · Bar contagem |
| Monte Carlo | 10.000 simulações | Bar probabilidade título · Bar Top-4/Rebaixamento |

**Grupo 4 — Random Forest + SHAP**

| Sub-aba | Algoritmos | Gráficos |
|---------|------------|----------|
| Zonas RF | Random Forest · Logistic Regression · SHAP | Feature importance · Doughnut zonas · **Scatter Pts/J×Gols/J por zona** |
| Arquétipos | Random Forest · Logistic Regression · SHAP | Feature importance · Scatter G/J×A/J por arquétipo |

> Ao clicar em um time (Zonas RF) ou jogador (Arquétipos), abre painel com SHAP individual horizontal bar chart.

**Grupo 5 — Comparação**

| Sub-aba | Modo | Gráficos |
|---------|------|----------|
| Comparação | Times (até 4) | Radar normalizado · Bar absoluto · **Scatter contexto na liga** |
| Comparação | Jogadores (até 4) | Radar normalizado · Bar absoluto · **Scatter contexto na liga** |

> O scatter de contexto posiciona todos os times/jogadores da liga em cinza e destaca os selecionados em cor — permite ver onde cada entidade se situa dentro do universo completo da liga.

---

### Classificações Zonas RF

| Zona | Descrição |
|------|-----------|
| Candidato ao Título | ~10% superiores em pts_rate |
| Zona Europeia | ~10–30% |
| Meio-Tabela | ~30–80% |
| Rebaixamento | ~20% inferiores |

### Arquétipos de Jogadores

| Arquétipo | Perfil |
|-----------|--------|
| Artilheiro Puro | Alto volume de gols, baixa contribuição em assistências |
| Polivalente | Equilíbrio entre gols e assistências |
| Criador | Foco em assistências e criação |
| Contribuição Limitada | Volume e eficiência reduzidos |

---

## Estrutura do Projeto

```
score-lgmRicardo/
│
├── backend/                        # FastAPI — Python
│   ├── main.py                     # App principal e todos os endpoints
│   ├── analysis_service.py         # Motor de ML (IF, Z-Score, LOF, RF, LR, SHAP, K-Means, Monte Carlo, Regressão)
│   ├── export_data.py              # Serviço de exportação CSV
│   ├── cache_manager.py            # Cache SQLite persistente com TTL
│   └── requirements.txt
│
├── bff/                            # Back-For-Front — Express/Node.js
│   ├── server.js                   # Proxy com cache em memória para o backend
│   └── package.json
│
├── frontend/                       # Vue.js 3 + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.vue                 # Layout principal, navegação, Tabela e Artilheiros
│   │   ├── AnalyticsTab.vue        # Dashboard ML completo (Chart.js — scatter, bar, radar, boxplot, linha)
│   │   ├── LiveTab.vue             # Partidas ao vivo (auto-refresh 30s)
│   │   ├── ExportData.vue          # Exportação de dados em CSV
│   │   ├── TeamProfile.vue         # Painel lateral de perfil do time
│   │   ├── main.js
│   │   └── style.css
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
│
├── start.sh                        # Script de inicialização
└── README.md
```

---

## Endpoints da API

### Backend (FastAPI) — porta 8000

**Dados gerais**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status do backend |
| GET | `/leagues` | Lista de ligas disponíveis |
| GET | `/fixtures/today` | Partidas do dia |
| GET | `/fixtures/next` | Próximas partidas |
| GET | `/fixtures/live` | Partidas ao vivo |
| GET | `/standings/{league_id}/{season}` | Tabela de classificação |
| GET | `/players/topscorers/{league_id}/{season}` | Artilheiros |
| GET | `/players/topassists/{league_id}/{season}` | Assistentes |
| GET | `/team/profile/{team_id}/{season}` | Perfil e histórico do time |

**Análise ML**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/analysis/standings/{league_id}/{season}` | Outliers na classificação (IF + Z-Score + LOF) |
| GET | `/analysis/topscorers/{league_id}/{season}` | Outliers nos artilheiros (IF + Z-Score + LOF) |
| GET | `/analysis/injuries/{league_id}/{season}` | Análise de lesões por time |
| POST | `/analysis/compare-leagues` | Comparação multi-liga (normalização radar) |
| GET | `/analysis/predictions/{league_id}/{season}` | Previsão de pontos finais (Regressão Linear) |
| GET | `/analysis/clusters/{league_id}/{season}` | K-Means por perfil de time |
| GET | `/analysis/monte-carlo/{league_id}/{season}` | 10.000 simulações de temporada |
| GET | `/analysis/zone-classifier/{league_id}/{season}` | Zonas competitivas (RF + LR + SHAP) |
| GET | `/analysis/player-archetypes/{league_id}/{season}` | Arquétipos de jogadores (RF + LR + SHAP) |

**Exportação**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/export/leagues` | Ligas disponíveis |
| POST | `/export/fixtures` | Exportar partidas |
| POST | `/export/standings` | Exportar classificação |
| POST | `/export/topscorers` | Exportar artilheiros |
| POST | `/export/injuries` | Exportar lesões |

**Sistema**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/cache/stats` | Estatísticas do cache |
| GET | `/docs` | Swagger UI interativo |

---

## Variáveis de Ambiente

### `backend/.env`
```env
API_KEY=sua_chave_do_api_sports_aqui
DEBUG=True
CACHE_TTL=3600
```

### `bff/.env`
```env
BACKEND_URL=http://localhost:8000
PORT=3001
NODE_ENV=development
```

### `frontend/.env` (opcional)
```env
VITE_BFF_URL=http://localhost:3001
```

---

## Arquitetura

```
Navegador (:5173)
     │
     ▼
Vue.js 3 + Tailwind CSS
     │  HTTP
     ▼
Express BFF (:3001)   ←── cache em memória (TTL 1h)
     │  HTTP
     ▼
FastAPI (:8000)        ←── cache SQLite + pipeline ML
     │  HTTPS
     ▼
API-Football v3
```

**Fluxo de dados:**
O frontend nunca acessa a API-Football diretamente. Todo tráfego passa pelo BFF (cache em memória) → Backend (processa, enriquece com ML e retorna JSON normalizado). O BFF expõe uma rota para cada endpoint do backend; qualquer endpoint novo no backend precisa de rota correspondente no `bff/server.js`.

**Cache em duas camadas:**
- BFF: cache em memória, 1 hora de TTL — evita round-trips ao backend
- Backend: cache SQLite persistente — evita chamadas à API-Football (plano gratuito tem limite de 100 req/dia)

---

## Troubleshooting

### Porta em uso

```bash
lsof -i :8000          # verificar qual processo usa a porta
lsof -ti:8000 | xargs kill -9   # encerrar
```

### `ModuleNotFoundError` no Python

```bash
cd backend && source venv/bin/activate
pip install -r requirements.txt
```

### `npm: command not found`

```bash
brew install node   # macOS via Homebrew
```

### SHAP não disponível

```bash
pip install shap

# Se houver erro de compilação (macOS):
xcode-select --install
pip install shap
```

O sistema funciona sem SHAP. Quando não instalado, o gráfico de Feature Importance exibe apenas RF Importance (a barra SHAP é omitida automaticamente).

### Tela em branco no navegador

1. Abra o DevTools (`F12`) e verifique o console
2. Confirme que backend (`:8000`) e BFF (`:3001`) estão ativos
3. Reinicie com `./start.sh restart`

### API Key inválida ou sem dados

1. Verifique `backend/.env` — a variável deve se chamar `API_KEY`
2. Confirme o plano em [api-sports.io](https://api-sports.io) — planos gratuitos têm limite de ligas e endpoints
3. Reinicie o backend após alterar o `.env`

### Endpoint novo no backend não funciona no frontend

Toda rota nova do FastAPI precisa de uma rota correspondente no BFF (`bff/server.js`). O frontend sempre chama `localhost:3001`, nunca `localhost:8000` diretamente.

---

**Última atualização:** Junho 2026
