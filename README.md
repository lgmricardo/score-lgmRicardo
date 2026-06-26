# Football App ⚽

Aplicação web moderna para visualização e análise de dados de futebol em tempo real via API-Football v3.

**Stack:** Vue.js 3 + Tailwind CSS (Frontend) · Express/Node.js (BFF) · FastAPI/Python (Backend)

---

## Índice

- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Iniciar](#como-iniciar)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
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

> A biblioteca `shap` é opcional — o sistema funciona sem ela, porém os valores SHAP ficam indisponíveis.

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

# .env (opcional — a URL padrão já é localhost:3001)
cat > .env << 'EOF'
VITE_BFF_URL=http://localhost:3001
EOF
```

---

## Como Iniciar

### Opção A — Script automático (recomendado)

```bash
# Dar permissão de execução (apenas na primeira vez)
chmod +x start.sh

# Iniciar todos os serviços
./start.sh start

# Outros comandos
./start.sh stop       # Parar tudo
./start.sh restart    # Reiniciar tudo
./start.sh status     # Ver status de cada serviço
```

O script abre abas no Terminal para cada serviço e verifica dependências automaticamente.

### Opção B — Manual (3 terminais)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 — BFF:**
```bash
cd bff
npm run dev
```

**Terminal 3 — Frontend:**
```bash
cd frontend
npm run dev
```

### Acessar a aplicação

| Serviço          | URL                          |
|------------------|------------------------------|
| Frontend         | http://localhost:5173        |
| BFF              | http://localhost:3001        |
| Backend (FastAPI)| http://localhost:8000        |
| API Docs (Swagger)| http://localhost:8000/docs  |

---

## Funcionalidades

### Dashboard
Visão geral com partidas do dia, próximas partidas e ligas disponíveis.

### Ao Vivo
Partidas em andamento com atualização automática a cada 30 segundos. Exibe placar, minuto e status de cada jogo.

### Ligas
Listagem de todas as ligas disponíveis na API com busca por nome. Clique numa liga para ir direto à tabela de classificação.

### Tabela de Classificação
Classificação completa com vitórias, empates, derrotas e pontos. Clique em um time para abrir o **Perfil do Time** (painel lateral com forma recente e próximas partidas).

Ligas disponíveis nos selects:

| Liga | País | ID |
|------|------|----|
| Premier League | England | 39 |
| Ligue 1 | France | 61 |
| Bundesliga | Germany | 78 |
| Serie A | Italy | 135 |
| Serie A | Brazil | 71 |

### Artilheiros
Top artilheiros por liga e temporada com total de gols.

### Exportar Dados
Exportação em CSV com filtros por liga, temporada, período de datas e campos selecionáveis. Tipos disponíveis: Partidas · Classificação · Artilheiros · Lesões.

### Análise ML
Motor de análise estatística e machine learning com os seguintes módulos:

| Sub-aba | Algoritmos |
|---------|------------|
| Classificação | Isolation Forest · Z-Score · LOF |
| Artilheiros | Isolation Forest · Z-Score · LOF |
| Lesões | Z-Score por time |
| Multi-Liga | Comparação por radar e gols/jogo |
| Previsões | Regressão Linear (R²) |
| Clusters | K-Means (4 grupos: Ataque/Defesa/Pts) |
| Monte Carlo | 10.000 simulações por liga |
| Zonas RF | Random Forest + Logistic Regression + SHAP |
| Arquétipos | Random Forest + Logistic Regression + SHAP |

---

## Estrutura do Projeto

```
score-lgmRicardo/
│
├── backend/                        # FastAPI — Python
│   ├── main.py                     # App principal e todos os endpoints
│   ├── analysis_service.py         # Motor de ML e análise estatística
│   ├── export_data.py              # Serviço de exportação CSV
│   ├── cache_manager.py            # Cache em memória com TTL
│   └── requirements.txt
│
├── bff/                            # Back-For-Front — Express/Node.js
│   ├── server.js                   # Proxy com cache para o backend
│   └── package.json
│
├── frontend/                       # Vue.js 3 + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.vue                 # Layout principal e navegação por abas
│   │   ├── LiveTab.vue             # Partidas ao vivo (auto-refresh 30s)
│   │   ├── ExportData.vue          # Exportação de dados em CSV
│   │   ├── AnalyticsTab.vue        # Dashboard de análise ML (Chart.js)
│   │   ├── TeamProfile.vue         # Painel lateral de perfil do time
│   │   ├── main.js
│   │   └── style.css
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
│
├── start.sh                        # Script de inicialização com menu
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
| GET | `/analysis/standings/{league_id}/{season}` | Outliers na classificação |
| GET | `/analysis/topscorers/{league_id}/{season}` | Outliers nos artilheiros |
| GET | `/analysis/injuries/{league_id}/{season}` | Análise de lesões |
| POST | `/analysis/compare-leagues` | Comparação multi-liga |
| GET | `/analysis/predictions/{league_id}/{season}` | Previsão de pontos finais |
| GET | `/analysis/clusters/{league_id}/{season}` | K-Means por time |
| GET | `/analysis/monte-carlo/{league_id}/{season}` | 10k simulações de temporada |
| GET | `/analysis/zone-classifier/{league_id}/{season}` | Zonas RF + SHAP por time |
| GET | `/analysis/player-archetypes/{league_id}/{season}` | Arquétipos RF + SHAP por jogador |

**Exportação**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/export/leagues` | Ligas disponíveis para exportar |
| POST | `/export/fixtures` | Exportar partidas |
| POST | `/export/standings` | Exportar classificação |
| POST | `/export/topscorers` | Exportar artilheiros |
| POST | `/export/injuries` | Exportar lesões |

**Sistema**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/cache/stats` | Estatísticas do cache |
| GET | `/docs` | Documentação interativa (Swagger UI) |

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

## Troubleshooting

### Porta em uso

```bash
# Verificar qual processo usa a porta
lsof -i :8000

# Encerrar processo
lsof -ti:8000 | xargs kill -9
```

### `ModuleNotFoundError` no Python

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### `npm: command not found`

```bash
# Instalar via Homebrew (macOS)
brew install node
```

### SHAP não disponível

A análise SHAP requer a biblioteca `shap`, que tem dependências nativas. Se falhar na instalação:

```bash
# Instalar manualmente
pip install shap

# Se houver erro de compilação, instale Xcode Command Line Tools (macOS)
xcode-select --install
```

O sistema funciona normalmente sem o SHAP — os valores SHAP ficam exibidos como "não disponível".

### Tela em branco no navegador

1. Abra o DevTools (`F12`) e verifique o console
2. Confirme que backend (`:8000`) e BFF (`:3001`) estão respondendo
3. Reinicie com `./start.sh restart`

### API Key inválida

1. Verifique `backend/.env` — a variável deve se chamar `API_KEY`
2. Acesse [api-sports.io](https://api-sports.io) para gerar ou verificar sua chave
3. Reinicie o backend após alterar o `.env`

---

## Arquitetura

```
Navegador (:5173)
     │
     ▼
Vue.js 3 + Tailwind CSS
     │  HTTP
     ▼
Express BFF (:3001)   ←── cache em memória
     │  HTTP
     ▼
FastAPI (:8000)        ←── cache em memória + análise ML
     │  HTTPS
     ▼
API-Football v3
```

**Fluxo de dados:**  
O frontend nunca acessa a API-Football diretamente. Todo tráfego passa pelo BFF (que adiciona cache) → Backend (que processa e enriquece os dados com ML).

---

**Última atualização:** Junho 2026
