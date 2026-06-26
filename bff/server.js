const express = require('express');
const axios = require('axios');
const cors = require('cors');
require('dotenv').config();

// ============================================================================
// CONFIGURAÇÕES
// ============================================================================

const app = express();
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const PORT = process.env.PORT || 3001;
const CACHE_TTL = process.env.CACHE_TTL || 3600000; // 1 hora em ms

// ============================================================================
// MIDDLEWARE
// ============================================================================

app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:3000'],
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Cache em memória
const cache = {};

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

const getCacheKey = (endpoint, params) => {
  const paramStr = Object.keys(params)
    .sort()
    .map(key => `${key}_${params[key]}`)
    .join('_');
  return `${endpoint}_${paramStr}`;
};

const isCacheValid = (key) => {
  if (!cache[key]) return false;
  
  const { timestamp } = cache[key];
  if (Date.now() - timestamp > CACHE_TTL) {
    delete cache[key];
    return false;
  }
  
  return true;
};

const setCache = (key, data) => {
  cache[key] = { data, timestamp: Date.now() };
};

const getCache = (key) => {
  return cache[key]?.data || null;
};

// ============================================================================
// HEALTH CHECK
// ============================================================================

app.get('/health', (req, res) => {
  res.json({
    status: 'online',
    timestamp: new Date().toISOString(),
    backend: BACKEND_URL
  });
});

// ============================================================================
// ROTAS PRINCIPAIS
// ============================================================================

// Fixtures de hoje
app.get('/fixtures/today', async (req, res) => {
  try {
    const cacheKey = 'fixtures_today';
    
    if (isCacheValid(cacheKey)) {
      console.log('[CACHE] fixtures/today');
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(`${BACKEND_URL}/fixtures/today`);
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] fixtures/today:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar fixtures',
      message: error.message 
    });
  }
});

// Próximas fixtures
app.get('/fixtures/next', async (req, res) => {
  try {
    const days = req.query.days || 7;
    const cacheKey = `fixtures_next_${days}`;
    
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] fixtures/next?days=${days}`);
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(`${BACKEND_URL}/fixtures/next`, { 
      params: { days } 
    });
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] fixtures/next:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar próximas fixtures',
      message: error.message 
    });
  }
});

// Tabela de classificação
app.get('/standings/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `standings_${league_id}_${season}`;
    
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] standings/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(
      `${BACKEND_URL}/standings/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] standings:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar standings',
      message: error.message 
    });
  }
});

// Top scorers
app.get('/players/topscorers/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `topscorers_${league_id}_${season}`;
    
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] players/topscorers/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(
      `${BACKEND_URL}/players/topscorers/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] topscorers:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar top scorers',
      message: error.message 
    });
  }
});

// Top assists
app.get('/players/topassists/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `topassists_${league_id}_${season}`;
    
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] players/topassists/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(
      `${BACKEND_URL}/players/topassists/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] topassists:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar top assists',
      message: error.message 
    });
  }
});

// Ligas
app.get('/leagues', async (req, res) => {
  try {
    const cacheKey = 'leagues';
    
    if (isCacheValid(cacheKey)) {
      console.log('[CACHE] leagues');
      return res.json(getCache(cacheKey));
    }
    
    const response = await axios.get(`${BACKEND_URL}/leagues`);
    setCache(cacheKey, response.data);
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] leagues:', error.message);
    res.status(500).json({ 
      error: 'Erro ao buscar ligas',
      message: error.message 
    });
  }
});

// ============================================================================
// ROTAS DE EXPORT
// ============================================================================

// Obter ligas disponíveis
app.get('/export/leagues', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/export/leagues`);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/leagues:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao obter ligas',
      error: error.message 
    });
  }
});

// Obter tipos de dados
app.get('/export/data-types', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/export/data-types`);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/data-types:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao obter tipos de dados',
      error: error.message 
    });
  }
});

// Exportar fixtures
app.post('/export/fixtures', async (req, res) => {
  try {
    const { league_id, season, from_date, to_date } = { ...req.body, ...req.query };

    console.log(`[EXPORT] Fixtures: ${league_id} ${season} ${from_date} to ${to_date}`);
    
    const response = await axios.post(`${BACKEND_URL}/export/fixtures`, null, {
      params: { league_id, season, from_date, to_date }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/fixtures:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao exportar fixtures',
      error: error.message 
    });
  }
});

// Exportar standings
app.post('/export/standings', async (req, res) => {
  try {
    const { league_id, season } = { ...req.body, ...req.query };

    console.log(`[EXPORT] Standings: ${league_id} ${season}`);
    
    const response = await axios.post(`${BACKEND_URL}/export/standings`, null, {
      params: { league_id, season }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/standings:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao exportar standings',
      error: error.message 
    });
  }
});

// Exportar top scorers
app.post('/export/topscorers', async (req, res) => {
  try {
    const { league_id, season } = { ...req.body, ...req.query };

    console.log(`[EXPORT] Top Scorers: ${league_id} ${season}`);
    
    const response = await axios.post(`${BACKEND_URL}/export/topscorers`, null, {
      params: { league_id, season }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/topscorers:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao exportar top scorers',
      error: error.message 
    });
  }
});

// Exportar injuries
app.post('/export/injuries', async (req, res) => {
  try {
    const { league_id, season } = { ...req.body, ...req.query };

    console.log(`[EXPORT] Injuries: ${league_id} ${season}`);
    
    const response = await axios.post(`${BACKEND_URL}/export/injuries`, null, {
      params: { league_id, season }
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/injuries:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao exportar injuries',
      error: error.message 
    });
  }
});

// Listar downloads
app.get('/export/downloads', async (req, res) => {
  try {
    const response = await axios.get(`${BACKEND_URL}/export/downloads`);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] export/downloads:', error.message);
    res.status(500).json({ 
      success: false, 
      message: 'Erro ao listar downloads',
      error: error.message 
    });
  }
});

// ============================================================================
// ROTAS DE ANÁLISE ML
// ============================================================================

app.get('/analysis/standings/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_standings_${league_id}_${season}`;

    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/standings/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }

    const response = await axios.get(
      `${BACKEND_URL}/analysis/standings/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/standings:', error.message);
    res.status(500).json({ error: 'Erro ao buscar análise de standings', message: error.message });
  }
});

app.get('/analysis/topscorers/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_topscorers_${league_id}_${season}`;

    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/topscorers/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }

    const response = await axios.get(
      `${BACKEND_URL}/analysis/topscorers/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/topscorers:', error.message);
    res.status(500).json({ error: 'Erro ao buscar análise de artilheiros', message: error.message });
  }
});

app.get('/analysis/injuries/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_injuries_${league_id}_${season}`;

    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/injuries/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }

    const response = await axios.get(
      `${BACKEND_URL}/analysis/injuries/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/injuries:', error.message);
    res.status(500).json({ error: 'Erro ao buscar análise de lesões', message: error.message });
  }
});

app.post('/analysis/compare-leagues', async (req, res) => {
  try {
    const response = await axios.post(
      `${BACKEND_URL}/analysis/compare-leagues`,
      req.body
    );
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/compare-leagues:', error.message);
    res.status(500).json({ error: 'Erro ao comparar ligas', message: error.message });
  }
});

app.get('/analysis/predictions/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_predictions_${league_id}_${season}`;

    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/predictions/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }

    const response = await axios.get(
      `${BACKEND_URL}/analysis/predictions/${league_id}/${season}`
    );
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/predictions:', error.message);
    res.status(500).json({ error: 'Erro ao buscar previsões', message: error.message });
  }
});

app.get('/analysis/clusters/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_clusters_${league_id}_${season}`;
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/clusters/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    const response = await axios.get(`${BACKEND_URL}/analysis/clusters/${league_id}/${season}`);
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/clusters:', error.message);
    res.status(500).json({ error: 'Erro ao buscar clusters', message: error.message });
  }
});

app.get('/analysis/monte-carlo/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_mc_${league_id}_${season}`;
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/monte-carlo/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    const response = await axios.get(`${BACKEND_URL}/analysis/monte-carlo/${league_id}/${season}`);
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/monte-carlo:', error.message);
    res.status(500).json({ error: 'Erro ao buscar simulação Monte Carlo', message: error.message });
  }
});

app.get('/analysis/zone-classifier/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_zones_${league_id}_${season}`;
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/zone-classifier/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    const response = await axios.get(`${BACKEND_URL}/analysis/zone-classifier/${league_id}/${season}`);
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/zone-classifier:', error.message);
    res.status(500).json({ error: 'Erro ao classificar zonas RF', message: error.message });
  }
});

app.get('/analysis/player-archetypes/:league_id/:season', async (req, res) => {
  try {
    const { league_id, season } = req.params;
    const cacheKey = `analysis_archetypes_${league_id}_${season}`;
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] analysis/player-archetypes/${league_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    const response = await axios.get(`${BACKEND_URL}/analysis/player-archetypes/${league_id}/${season}`);
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] analysis/player-archetypes:', error.message);
    res.status(500).json({ error: 'Erro ao classificar arquétipos', message: error.message });
  }
});

app.get('/fixtures/live', async (req, res) => {
  try {
    const LIVE_TTL = 30000;
    const cacheKey = 'fixtures_live';
    if (cache[cacheKey] && Date.now() - cache[cacheKey].timestamp <= LIVE_TTL) {
      return res.json(cache[cacheKey].data);
    }
    const response = await axios.get(`${BACKEND_URL}/fixtures/live`);
    cache[cacheKey] = { data: response.data, timestamp: Date.now() };
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] fixtures/live:', error.message);
    res.status(500).json({ error: 'Erro ao buscar partidas ao vivo', message: error.message });
  }
});

app.get('/team/profile/:team_id/:season', async (req, res) => {
  try {
    const { team_id, season } = req.params;
    const cacheKey = `team_profile_${team_id}_${season}`;
    if (isCacheValid(cacheKey)) {
      console.log(`[CACHE] team/profile/${team_id}/${season}`);
      return res.json(getCache(cacheKey));
    }
    const response = await axios.get(`${BACKEND_URL}/team/profile/${team_id}/${season}`);
    setCache(cacheKey, response.data);
    res.json(response.data);
  } catch (error) {
    console.error('[ERROR] team/profile:', error.message);
    res.status(500).json({ error: 'Erro ao buscar perfil do time', message: error.message });
  }
});

// ============================================================================
// ROOT
// ============================================================================

app.get('/', (req, res) => {
  res.json({
    message: 'Football BFF API v1.0',
    backend: BACKEND_URL,
    health: '/health'
  });
});

// ============================================================================
// ERROR HANDLING
// ============================================================================

app.use((err, req, res, next) => {
  console.error('[ERROR] Unhandled error:', err);
  res.status(500).json({
    error: 'Erro interno do servidor',
    message: err.message
  });
});

// ============================================================================
// INICIAR SERVIDOR
// ============================================================================

app.listen(PORT, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`  🚀 BFF Server rodando em http://localhost:${PORT}`);
  console.log(`  📡 Backend: ${BACKEND_URL}`);
  console.log(`${'='.repeat(60)}\n`);
});

module.exports = app;
