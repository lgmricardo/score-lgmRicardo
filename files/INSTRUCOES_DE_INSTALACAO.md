# 📋 GUIA DE INSTALAÇÃO - MÓDULO DE EXPORT

Este documento detalha como copiar os arquivos gerados para as pastas corretas do seu projeto.

---

## 🎯 Resumo dos Arquivos

| Arquivo | Destino | Descrição |
|---------|---------|-----------|
| `main.py` | `backend/` | Backend FastAPI com endpoints de export |
| `server.js` | `bff/` | BFF Express com rotas de export |
| `ExportData.vue` | `frontend/src/` | Componente Vue para interface de export |
| `export_data.py` | `backend/` | Script CLI de export (já deve estar lá) |

---

## 📂 ESTRUTURA DO PROJETO

```
score-lgmRicardo/
├── backend/
│   ├── main.py              👈 SUBSTITUIR
│   ├── export_data.py       ✅ Já deve estar aqui
│   ├── requirements.txt      ✅ OK
│   └── .env                  ✅ OK
│
├── bff/
│   ├── server.js            👈 SUBSTITUIR
│   ├── package.json          ✅ OK
│   └── .env                  ✅ OK
│
├── frontend/
│   └── src/
│       ├── App.vue           👈 MODIFICAR
│       ├── ExportData.vue    👈 CRIAR
│       ├── main.js           ✅ OK
│       └── style.css         ✅ OK
│
└── data/
    ├── exports/              ✅ Será criada automaticamente
    └── cache/                ✅ Será criada automaticamente
```

---

## 🔧 PASSO 1: Substituir `backend/main.py`

### Local:
```bash
/Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py
```

### Como fazer:

**OPÇÃO A - Via Terminal:**

```bash
# Faça backup do arquivo atual
cp /Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py \
   /Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py.backup

# Copie o novo arquivo
cp /mnt/user-data/outputs/main.py \
   /Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py
```

**OPÇÃO B - Manual:**

1. Abra o arquivo em `/mnt/user-data/outputs/main.py`
2. Copie todo o conteúdo
3. Abra `backend/main.py` no seu editor favorito (VS Code, nano, etc)
4. Apague o conteúdo atual
5. Cole o novo conteúdo
6. Salve

---

## 🔧 PASSO 2: Substituir `bff/server.js`

### Local:
```bash
/Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js
```

### Como fazer:

**OPÇÃO A - Via Terminal:**

```bash
# Faça backup do arquivo atual
cp /Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js \
   /Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js.backup

# Copie o novo arquivo
cp /mnt/user-data/outputs/server.js \
   /Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js
```

**OPÇÃO B - Manual:**

1. Abra o arquivo em `/mnt/user-data/outputs/server.js`
2. Copie todo o conteúdo
3. Abra `bff/server.js` no seu editor favorito
4. Apague o conteúdo atual
5. Cole o novo conteúdo
6. Salve

---

## 🔧 PASSO 3: Criar `frontend/src/ExportData.vue`

### Local:
```bash
/Users/lgmricardo/Documents/score-lgmRicardo/frontend/src/ExportData.vue
```

### Como fazer:

**OPÇÃO A - Via Terminal:**

```bash
# Copie o arquivo
cp /mnt/user-data/outputs/ExportData.vue \
   /Users/lgmricardo/Documents/score-lgmRicardo/frontend/src/ExportData.vue
```

**OPÇÃO B - Manual:**

1. Abra o arquivo em `/mnt/user-data/outputs/ExportData.vue`
2. Copie todo o conteúdo
3. Crie um novo arquivo `ExportData.vue` em `frontend/src/`
4. Cole o conteúdo
5. Salve

---

## 🔧 PASSO 4: Modificar `frontend/src/App.vue`

Agora você precisa modificar o arquivo `App.vue` para adicionar a aba de export.

### Como fazer:

1. Abra `frontend/src/App.vue`

2. **Procure por:** 
```javascript
import { ... componentes ... } from 'vue'
```

3. **Adicione após os imports de componentes:**
```javascript
import ExportData from './ExportData.vue'
```

**Exemplo completo:**
```javascript
import { ref } from 'vue'
import Dashboard from './Dashboard.vue'
import LeaguesTab from './LeaguesTab.vue'
import StandingsTab from './StandingsTab.vue'
import TopScorersTab from './TopScorersTab.vue'
import ExportData from './ExportData.vue'  // 👈 ADICIONE ISTO
```

4. **Procure por:** 
```vue
<div class="flex flex-wrap gap-2 mb-8">
  <!-- Botões das abas -->
</div>
```

5. **Adicione este botão DENTRO dessa `<div>`:**
```vue
<button
  v-if="activeTab !== 'export'"
  @click="activeTab = 'export'"
  class="px-4 py-2 rounded-lg bg-slate-700 text-white hover:bg-slate-600 transition"
>
  📊 Export
</button>
```

6. **Procure por:**
```vue
<div class="mt-8">
  <!-- Componentes das abas -->
</div>
```

7. **Adicione DENTRO dessa `<div>`, ao final:**
```vue
<ExportData v-if="activeTab === 'export'" />
```

**Exemplo de como ficará:**
```vue
<div class="mt-8">
  <Dashboard v-if="activeTab === 'dashboard'" />
  <LeaguesTab v-if="activeTab === 'leagues'" />
  <StandingsTab v-if="activeTab === 'standings'" />
  <TopScorersTab v-if="activeTab === 'topscorers'" />
  <ExportData v-if="activeTab === 'export'" />  <!-- 👈 ADICIONE ISTO -->
</div>
```

8. **Salve o arquivo**

---

## ✅ VERIFICAR SE TUDO ESTÁ CERTO

### Verifique os arquivos com os comandos:

```bash
# Verificar se main.py existe e tem conteúdo correto
ls -lh /Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py
grep "export/leagues" /Users/lgmricardo/Documents/score-lgmRicardo/backend/main.py

# Verificar se server.js existe e tem conteúdo correto
ls -lh /Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js
grep "export/leagues" /Users/lgmricardo/Documents/score-lgmRicardo/bff/server.js

# Verificar se ExportData.vue existe
ls -lh /Users/lgmricardo/Documents/score-lgmRicardo/frontend/src/ExportData.vue
```

Se tudo mostrar caminhos e arquivos válidos, está tudo certo! ✅

---

## 🚀 PASSO 5: Reiniciar os Serviços

Depois de copiar todos os arquivos, reinicie:

```bash
# Com script
startfootball restart

# Ou manualmente:

# Terminal 1
cd /Users/lgmricardo/Documents/score-lgmRicardo/backend
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2
cd /Users/lgmricardo/Documents/score-lgmRicardo/bff
npm run dev

# Terminal 3
cd /Users/lgmricardo/Documents/score-lgmRicardo/frontend
npm run dev
```

---

## 🎉 TESTAR A INTERFACE

1. Abra `http://localhost:5173` no navegador
2. Procure por uma nova aba chamada **"📊 Export"**
3. Selecione:
   - Tipo de Dados (Fixtures, Standings, Top Scorers, Injuries)
   - Liga
   - Temporada
   - Período (se for Fixtures)
4. Clique em **"📥 Exportar"**
5. Veja os dados na tabela
6. Clique em **"💾 Download CSV"** para baixar

---

## 🐛 TROUBLESHOOTING

### "Module not found: ExportData"
- Verificar se `ExportData.vue` está em `frontend/src/`
- Verificar a import em `App.vue`

### "404 Not Found" ao clicar em Export
- Verificar se `main.py` foi atualizado corretamente
- Verificar se `server.js` foi atualizado corretamente
- Reiniciar os serviços

### "CORS error"
- Verificar se backend está rodando em `localhost:8000`
- Verificar se BFF está rodando em `localhost:3001`
- Verificar se frontend está rodando em `localhost:5173`

### Dados não aparecem
- Verificar console do navegador (F12)
- Verificar logs dos serviços
- Verificar se a API key está configurada em `backend/.env`

---

## 📝 RESUMO DOS ARQUIVOS GERADOS

Os arquivos estão disponíveis em:
```
/mnt/user-data/outputs/
├── main.py
├── server.js
├── ExportData.vue
└── README.md (este arquivo)
```

---

## ✨ PRÓXIMOS PASSOS

Depois que tudo estiver funcionando:

1. ✅ Testar exportação de Fixtures
2. ✅ Testar exportação de Standings
3. ✅ Testar exportação de Top Scorers
4. ✅ Testar download dos CSVs
5. 🔄 Customizar campos de export
6. 📊 Adicionar gráficos dos dados
7. 💾 Integrar banco de dados

---

**Se tiver problemas, execute os comandos de verificação acima e me mostre a saída!** 🚀⚽
