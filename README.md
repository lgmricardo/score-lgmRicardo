# Football App ⚽🚀

Uma aplicação web moderna para visualizar dados de futebol em tempo real usando a API-Football v3.

**Stack:** Vue.js 3 (Frontend) + Express (BFF) + FastAPI (Backend)

---

## 📋 Índice

- [Requisitos](#requisitos)
- [Instalação Passo a Passo](#instalação-passo-a-passo)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints da API](#endpoints-da-api)
- [Troubleshooting](#troubleshooting)
- [Informações Técnicas](#informações-técnicas)

---

## ✅ Requisitos

### Mínimos do Sistema

- **macOS** 10.13+ (ou Linux/Windows com adaptações)
- **RAM:** 4GB no mínimo
- **Espaço em disco:** 500MB

### Software Necessário

| Software | Versão Mínima | Verificar |
|----------|---------------|----------|
| Python | 3.8+ | `python3 --version` |
| Node.js | 16.0+ | `node --version` |
| npm | 8.0+ | `npm --version` |
| Git | 2.0+ | `git --version` |

### Chave da API

- **API-Football v3**: Obtenha em [api-sports.io](https://api-sports.io)
- A chave será configurada no arquivo `.env` do backend

---

## 🛠️ Instalação Passo a Passo

### **PASSO 1: Verificar Dependências**

Abra o Terminal e execute:

```bash
# Verificar Python
python3 --version
# Esperado: Python 3.8 ou superior

# Verificar Node.js
node --version
# Esperado: v16.0 ou superior

# Verificar npm
npm --version
# Esperado: 8.0 ou superior
```

Se alguma dependência estiver faltando, veja [Instalando Dependências](#instalando-dependências).

---

### **PASSO 2: Clonar ou Extrair o Projeto**

Se você recebeu um arquivo `.zip`:

```bash
# Navegue até a pasta Downloads (ou onde salvou)
cd ~/Downloads

# Descompacte
unzip projeto-football.zip

# Mova para o local desejado
mv projeto-football /Users/SEU_USER/Documents/score-lgmRicardo/
```

Se o projeto já está em `score-lgmRicardo`, apenas navegue até lá:

```bash
cd /Users/SEU_USER/Documents/score-lgmRicardo
```

---

### **PASSO 3: Configurar Backend (FastAPI)**

```bash
# 1. Navegue até o backend
cd /Users/SEU_USER/Documents/score-lgmRicardo/backend

# 2. Criar ambiente virtual Python
python3 -m venv venv

# 3. Ativar ambiente virtual
source venv/bin/activate

# Você deve ver "(venv)" no prompt do Terminal

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Criar arquivo .env com sua chave da API
cat > .env << 'EOF'
API_KEY=sua_chave_da_api_aqui
DEBUG=True
EOF

# ⚠️ IMPORTANTE: Substitua "sua_chave_da_api_aqui" por sua chave real do api-sports.io
```

**Arquivo `requirements.txt` esperado:**
```
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
python-dotenv==1.0.0
```

---

### **PASSO 4: Configurar BFF (Express)**

```bash
# 1. Navegue até o BFF
cd /Users/SEU_USER/Documents/score-lgmRicardo/bff

# 2. Instalar dependências npm
npm install

# 3. Criar arquivo .env
cat > .env << 'EOF'
BACKEND_URL=http://localhost:8000
PORT=3001
NODE_ENV=development
EOF
```

**Pacotes npm que serão instalados:**
```json
{
  "express": "^4.18.2",
  "axios": "^1.6.1",
  "cors": "^2.8.5",
  "dotenv": "^16.3.1",
  "nodemon": "^3.0.1"
}
```

---

### **PASSO 5: Configurar Frontend (Vue.js)**

```bash
# 1. Navegue até o frontend
cd /Users/SEU_USER/Documents/score-lgmRicardo/frontend

# 2. Instalar dependências npm
npm install

# 3. Instalar Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# 4. Inicializar Tailwind
npx tailwindcss init -p

# 5. Criar arquivo .env
cat > .env << 'EOF'
VITE_BFF_URL=http://localhost:3001
EOF
```

**Pacotes npm que serão instalados:**
```json
{
  "vue": "^3.3.0",
  "vite": "^5.0.0"
}
```

---

### **PASSO 6: Instalar Script de Inicialização (Opcional)**

Para facilitar, crie um script que inicia tudo automaticamente:

```bash
# 1. Abra o nano para editar
nano /Users/SEU_USER/Documents/score-lgmRicardo/start.sh
```

Cole o conteúdo do script sofisticado (veja a seção anterior) e salve.

```bash
# 2. Dê permissão de execução
chmod +x /Users/SEU_USER/Documents/score-lgmRicardo/start.sh

# 3. (Opcional) Crie um alias no .zshrc
echo "alias startfootball='/Users/SEU_USER/Documents/score-lgmRicardo/start.sh'" >> ~/.zshrc
source ~/.zshrc
```

---

## 🚀 Como Usar

### **OPÇÃO A: Iniciar Manualmente (3 Terminais)**

Abra **3 abas diferentes** no Terminal (⌘+T) e execute em cada uma:

#### **Terminal 1 - Backend:**
```bash
cd /Users/SEU_USER/Documents/score-lgmRicardo/backend
source venv/bin/activate
uvicorn main:app --reload
```

Você deve ver:
```
Uvicorn running on http://127.0.0.1:8000
```

#### **Terminal 2 - BFF:**
```bash
cd /Users/SEU_USER/Documents/score-lgmRicardo/bff
npm run dev
```

Você deve ver:
```
Server running on port 3001
```

#### **Terminal 3 - Frontend:**
```bash
cd /Users/SEU_USER/Documents/score-lgmRicardo/frontend
npm run dev
```

Você deve ver:
```
Local: http://localhost:5173
```

---

### **OPÇÃO B: Iniciar com Script (Recomendado)**

```bash
# Menu interativo
/Users/SEU_USER/Documents/score-lgmRicardo/start.sh

# Ou com alias
startfootball
```

**Comandos disponíveis:**

```bash
startfootball start      # Iniciar todos os serviços
startfootball stop       # Parar todos os serviços
startfootball restart    # Reiniciar todos
startfootball status     # Ver status de cada serviço
```

---

### **PASSO 3: Acessar a Aplicação**

Abra seu navegador e acesse:

```
http://localhost:5173
```

Você deve ver a interface com as opções:
- 📊 Dashboard
- 🏆 Ligas
- 📋 Tabelas
- ⚽ Artilheiros

---

## 📖 Como Usar a Aplicação

### **Dashboard**

Na primeira aba, você pode visualizar:

- **Próximas Partidas**: Jogos agendados para hoje
- **Últimos Resultados**: Resultados mais recentes
- **Filtros**: Pesquisar por time, data ou liga

### **Ligas**

Explore as principais ligas de futebol:

- Premier League (Inglaterra)
- La Liga (Espanha)
- Serie A (Itália)
- Bundesliga (Alemanha)
- Ligue 1 (França)
- Série A (Brasil)

### **Tabelas**

Visualize as tabelas de classificação:

1. Selecione uma **liga** no dropdown
2. Escolha a **temporada**
3. Veja a tabela com:
   - Posição
   - Time
   - Pontos
   - Vitórias/Empates/Derrotas
   - Gols

### **Artilheiros**

Confira os principais atacantes e assistentes:

- Top Scorers
- Top Assists
- Top Yellow Cards
- Top Red Cards

Filtre por liga e temporada.

---

## 📁 Estrutura do Projeto

```
score-lgmRicardo/
│
├── backend/                    # FastAPI Backend (Python)
│   ├── main.py                # App principal
│   ├── requirements.txt        # Dependências Python
│   ├── .env                   # Variáveis de ambiente
│   └── venv/                  # Ambiente virtual (criado na instalação)
│
├── bff/                        # BFF - Express (Node.js)
│   ├── server.js              # Servidor Express
│   ├── package.json           # Dependências npm
│   ├── .env                   # Variáveis de ambiente
│   └── node_modules/          # Pacotes (criado na instalação)
│
├── frontend/                   # Vue.js 3 Frontend
│   ├── src/
│   │   ├── App.vue           # Componente principal
│   │   ├── main.js           # Entrada da app
│   │   └── style.css         # Estilos globais
│   ├── index.html            # HTML base
│   ├── package.json          # Dependências npm
│   ├── vite.config.js        # Config Vite
│   ├── tailwind.config.js    # Config Tailwind CSS
│   ├── postcss.config.js     # Config PostCSS
│   ├── .env                  # Variáveis de ambiente
│   └── node_modules/         # Pacotes (criado na instalação)
│
├── start.sh                    # Script sofisticado de inicialização
├── README.md                   # Este arquivo
└── .gitignore                 # Arquivos ignorados pelo Git
```

---

## 🔌 Endpoints da API

### **Backend (FastAPI) - Porta 8000**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/docs` | GET | Documentação interativa (Swagger) |
| `/fixtures/today` | GET | Partidas de hoje |
| `/fixtures/next?days=7` | GET | Próximas partidas (próximos N dias) |
| `/fixtures/results-today` | GET | Resultados de hoje |
| `/fixtures/team/{team_id}` | GET | Partidas de um time |
| `/standings/{league_id}/{season}` | GET | Tabela de uma liga |
| `/teams/{league_id}/{season}` | GET | Times de uma liga |
| `/players/topscorers/{league_id}/{season}` | GET | Top artilheiros |
| `/players/topassists/{league_id}/{season}` | GET | Top assistentes |
| `/leagues` | GET | Lista de ligas |

**Exemplo de requisição:**
```bash
curl -X GET "http://localhost:8000/fixtures/today" \
  -H "accept: application/json"
```

### **BFF (Express) - Porta 3001**

Mesmos endpoints do backend, com cache e formatação adicional.

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Status da aplicação |
| `/fixtures/today` | GET | Partidas de hoje |
| `/standings/{league_id}/{season}` | GET | Tabela formatada |
| ... | ... | (Mesmos do backend) |

---

## 🐛 Troubleshooting

### **Problema: "Porta 8000 já está em uso"**

```bash
# Liberar a porta (macOS)
lsof -ti:8000 | xargs kill -9

# Ou mudar a porta no backend
uvicorn main:app --reload --port 8001
```

### **Problema: "npm command not found"**

```bash
# Instalar Node.js via Homebrew
brew install node

# Ou fazer download em https://nodejs.org
```

### **Problema: "ModuleNotFoundError: No module named 'fastapi'"**

```bash
# Certifique-se de que o venv está ativado
cd backend
source venv/bin/activate

# Reinstale as dependências
pip install -r requirements.txt
```

### **Problema: "CORS error no navegador"**

Verifique se:
1. Backend está rodando em `http://localhost:8000`
2. BFF está rodando em `http://localhost:3001`
3. Frontend está rodando em `http://localhost:5173`

Se tudo estiver rodando, reinicie com:
```bash
startfootball restart
```

### **Problema: "API Key inválida"**

1. Verifique se sua chave está correta em `backend/.env`
2. Acesse [api-sports.io](https://api-sports.io) e gere uma nova chave
3. Reinicie o backend

### **Problema: "Blank screen no navegador"**

1. Abra o DevTools (F12)
2. Verifique o console para erros
3. Verifique o Network tab
4. Se houver erro CORS, reinicie os serviços

---

## 💻 Informações Técnicas

### **Versões Utilizadas**

```
Python: 3.8+
Node.js: 16.0+
npm: 8.0+
Vue.js: 3.3+
FastAPI: 0.104.1
Express: 4.18.2
Tailwind CSS: 3.x
```

### **Portas Utilizadas**

| Serviço | Porta | URL |
|---------|-------|-----|
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| BFF (Express) | 3001 | http://localhost:3001 |
| Frontend (Vite) | 5173 | http://localhost:5173 |

### **Arquitetura**

```
┌──────────────┐
│   Browser    │
│ (localhost   │
│    :5173)    │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│  Vue.js 3    │
│  Frontend    │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│   Express    │
│  (BFF)       │
│  :3001       │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐
│   FastAPI    │
│  Backend     │
│   :8000      │
└──────┬───────┘
       │ HTTPS
       ▼
┌──────────────┐
│ API-Football │
│   v3 API     │
└──────────────┘
```

### **Caching**

- Backend: Cache em memória (1 hora)
- BFF: Cache em memória (1 hora)
- Frontend: Cache local do navegador

### **Variáveis de Ambiente**

#### Backend (`.env`)
```
API_KEY=sua_chave_aqui
DEBUG=True
CACHE_TTL=3600
```

#### BFF (`.env`)
```
BACKEND_URL=http://localhost:8000
PORT=3001
NODE_ENV=development
CACHE_TTL=3600
```

#### Frontend (`.env`)
```
VITE_BFF_URL=http://localhost:3001
```

---

## 📞 Suporte

### **Recursos Úteis**

- [API-Football Docs](https://api-sports.io/documentation/football)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vue.js 3 Docs](https://vuejs.org/)
- [Express Docs](https://expressjs.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/)

### **Verificar Logs**

Cada terminal mostra os logs em tempo real:

```bash
# Backend
# Logs de requisições, erros, e status HTTP

# BFF
# Logs de requisições, cache, e erros

# Frontend
# Logs de build, desenvolvimento, e erros no console
```

---

## 📝 Notas Importantes

⚠️ **Antes de começar:**

1. Você precisa de uma chave válida do [api-sports.io](https://api-sports.io)
2. Verifique se as portas 8000, 3001 e 5173 estão livres
3. A internet deve estar ativa (requisições para API externa)
4. Python 3.8+ e Node.js 16.0+ são obrigatórios

✅ **Quando tudo estiver funcionando:**

- Backend estará em: `http://localhost:8000` (com docs em `/docs`)
- BFF estará em: `http://localhost:3001`
- Frontend estará em: `http://localhost:5173`
- Os dados virão da API-Football em tempo real

---

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais.

---

## 👨‍💻 Desenvolvido com ❤️

Football App - Uma forma moderna de acompanhar futebol mundial.

**Última atualização:** Junho 2026

---

## 🎯 Próximos Passos

Depois de instalado, você pode:

1. ✅ Explorar a interface
2. ✅ Adicionar mais ligas
3. ✅ Customizar os estilos (Tailwind CSS)
4. ✅ Adicionar mais endpoints na API
5. ✅ Integrar banco de dados (MongoDB, PostgreSQL)
6. ✅ Fazer deploy em um servidor

---

**Aproveite a aplicação!** ⚽🚀