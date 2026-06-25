from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
import asyncio

# ============================================================================
# IMPORTS DO EXPORT
# ============================================================================

try:
    from export_data import (
        LEAGUES, DATA_TYPES,
        get_fixtures as export_get_fixtures,
        get_standings as export_get_standings,
        get_top_scorers as export_get_top_scorers,
        get_injuries as export_get_injuries,
        save_csv, EXPORTS_DIR
    )
except ImportError:
    print("⚠️  export_data.py não encontrado. Endpoints de export desabilitados.")
    LEAGUES = {}
    DATA_TYPES = {}
    EXPORTS_DIR = None
    export_get_fixtures = export_get_standings = export_get_top_scorers = export_get_injuries = None

try:
    from analysis_service import (
        analyze_standings   as ml_analyze_standings,
        analyze_topscorers  as ml_analyze_topscorers,
        analyze_injuries    as ml_analyze_injuries,
        compare_leagues     as ml_compare_leagues,
        predict_season      as ml_predict_season,
        cluster_teams       as ml_cluster_teams,
        monte_carlo_season  as ml_monte_carlo_season,
    )
except ImportError:
    print("⚠️  analysis_service.py não encontrado. Endpoints de análise desabilitados.")
    ml_analyze_standings = ml_analyze_topscorers = None
    ml_analyze_injuries  = ml_compare_leagues = ml_predict_season = None
    ml_cluster_teams = ml_monte_carlo_season = None

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"

if not API_KEY:
    raise ValueError("API_KEY não configurada no .env")

# ============================================================================
# INICIALIZAR APP
# ============================================================================

app = FastAPI(
    title="Football API",
    description="API para dados de futebol em tempo real",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache persistente (SQLite)
try:
    from cache_manager import PersistentCache as _PCache
    cache = _PCache()
    print("[CACHE] SQLite persistente em data/cache/football_cache.db")
except Exception as _ce:
    print(f"⚠️  cache_manager: {_ce}. Usando cache em memória.")
    cache = {}
CACHE_TTL = 3600       # 1 hora (cache geral)
LIVE_CACHE_TTL = 60    # 60s para dados ao vivo

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

async def fazer_requisicao(endpoint: str, params: dict):
    """Fazer requisição à API-Football"""
    headers = {
        "x-apisports-key": API_KEY,
        "x-apisports-host": "v3.football.api-sports.io"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{BASE_URL}/{endpoint}"
            response = await client.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            remaining = response.headers.get("x-ratelimit-requests-remaining", "?")
            print(f"[API] {endpoint} | Rate limit: {remaining}")
            
            return data
    
    except Exception as e:
        print(f"[ERROR] Requisição falhou: {e}")
        return None

def get_cache_key(endpoint: str, params: dict) -> str:
    """Gerar chave de cache"""
    params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
    return f"{endpoint}_{params_str}"

def is_cache_valid(key: str) -> bool:
    """Verificar se cache é válido"""
    if key not in cache:
        return False
    
    timestamp, _ = cache[key]
    if datetime.now().timestamp() - timestamp > CACHE_TTL:
        del cache[key]
        return False
    
    return True

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check do backend"""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "api_key_configured": bool(API_KEY)
    }

# ============================================================================
# ENDPOINTS PRINCIPAIS
# ============================================================================

@app.get("/fixtures/today")
async def get_fixtures_today():
    """Partidas de hoje"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "date": today,
        "timezone": "America/Sao_Paulo"
    }
    
    cache_key = get_cache_key("fixtures", params)
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    result = await fazer_requisicao("fixtures", params)
    
    fixtures = []
    for fixture in result.get("response", []):
        fixtures.append({
            "id": fixture.get("id"),
            "league": fixture.get("league", {}).get("name"),
            "date": fixture.get("fixture", {}).get("date"),
            "status": fixture.get("fixture", {}).get("status", {}).get("short"),
            "home": {
                "name": fixture.get("teams", {}).get("home", {}).get("name"),
                "logo": fixture.get("teams", {}).get("home", {}).get("logo"),
            },
            "away": {
                "name": fixture.get("teams", {}).get("away", {}).get("name"),
                "logo": fixture.get("teams", {}).get("away", {}).get("logo"),
            },
            "goals": {
                "home": fixture.get("goals", {}).get("home"),
                "away": fixture.get("goals", {}).get("away"),
            },
        })
    
    response_data = {
        "fixtures": fixtures,
        "count": len(fixtures)
    }
    
    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

@app.get("/fixtures/next")
async def get_fixtures_next(days: int = 7):
    """Próximas partidas"""
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    
    params = {
        "from": today,
        "to": future,
        "timezone": "America/Sao_Paulo"
    }
    
    cache_key = get_cache_key("fixtures", params)
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    result = await fazer_requisicao("fixtures", params)
    
    fixtures = []
    for fixture in result.get("response", []):
        fixtures.append({
            "id": fixture.get("id"),
            "league": fixture.get("league", {}).get("name"),
            "date": fixture.get("fixture", {}).get("date"),
            "status": fixture.get("fixture", {}).get("status", {}).get("short"),
            "home": {
                "name": fixture.get("teams", {}).get("home", {}).get("name"),
                "logo": fixture.get("teams", {}).get("home", {}).get("logo"),
            },
            "away": {
                "name": fixture.get("teams", {}).get("away", {}).get("name"),
                "logo": fixture.get("teams", {}).get("away", {}).get("logo"),
            },
            "goals": {
                "home": fixture.get("goals", {}).get("home"),
                "away": fixture.get("goals", {}).get("away"),
            },
        })
    
    response_data = {
        "fixtures": fixtures,
        "count": len(fixtures)
    }
    
    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

@app.get("/standings/{league_id}/{season}")
async def get_standings(league_id: str, season: str):
    """Tabela de classificação"""
    params = {
        "league": league_id,
        "season": season
    }
    
    cache_key = get_cache_key("standings", params)
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    result = await fazer_requisicao("standings", params)
    if not result:
        return {"standings": [], "count": 0}

    standings = []
    for item in result.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            standings.extend(group)

    response_data = {
        "standings": standings,
        "count": len(standings)
    }

    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

@app.get("/players/topscorers/{league_id}/{season}")
async def get_top_scorers(league_id: str, season: str):
    """Artilheiros"""
    params = {
        "league": league_id,
        "season": season
    }
    
    cache_key = get_cache_key("topscorers", params)
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    result = await fazer_requisicao("players/topscorers", params)
    if not result:
        return {"scorers": [], "count": 0}

    scorers = result.get("response", [])

    response_data = {
        "scorers": scorers,
        "count": len(scorers)
    }

    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

@app.get("/players/topassists/{league_id}/{season}")
async def get_top_assists(league_id: str, season: str):
    """Top assistentes"""
    params = {
        "league": league_id,
        "season": season
    }
    
    cache_key = get_cache_key("topassists", params)
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    result = await fazer_requisicao("players/topassists", params)
    
    assists = []
    for idx, player in enumerate(result.get("response", []), 1):
        stats = player.get("statistics", [{}])[0] if player.get("statistics") else {}
        assists.append({
            "rank": idx,
            "player": player.get("player", {}).get("name"),
            "team": stats.get("team", {}).get("name"),
            "goals": stats.get("goals", {}).get("total"),
            "assists": stats.get("goals", {}).get("assists"),
            "appearances": stats.get("games", {}).get("appearences"),
        })
    
    response_data = {
        "assists": assists,
        "count": len(assists)
    }
    
    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

@app.get("/leagues")
async def get_leagues():
    """Lista de ligas"""
    cache_key = "leagues"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data
    
    params = {}
    result = await fazer_requisicao("leagues", params)
    
    leagues = []
    for league in result.get("response", []):
        if league.get("league", {}).get("id") in [39, 61, 78, 135, 71, 140]:
            leagues.append({
                "id": league.get("league", {}).get("id"),
                "name": league.get("league", {}).get("name"),
                "country": league.get("country", {}).get("name"),
                "logo": league.get("league", {}).get("logo"),
            })
    
    response_data = {
        "leagues": leagues,
        "count": len(leagues)
    }
    
    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data

# ============================================================================
# ENDPOINTS DE ANÁLISE ML
# ============================================================================

@app.get("/analysis/standings/{league_id}/{season}")
async def get_analysis_standings(league_id: str, season: str):
    """Análise ML da tabela de classificação (Isolation Forest + Z-Score + LOF)"""
    if not ml_analyze_standings:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_standings_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("standings", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    standings = []
    for item in result.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            standings.extend(group)

    if not standings:
        return {"error": "Sem dados de classificação para esta liga/temporada"}

    analysis = ml_analyze_standings(standings)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.get("/analysis/topscorers/{league_id}/{season}")
async def get_analysis_topscorers(league_id: str, season: str):
    """Análise ML dos artilheiros (Isolation Forest + Z-Score + LOF)"""
    if not ml_analyze_topscorers:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_topscorers_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("players/topscorers", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    scorers = result.get("response", [])
    if not scorers:
        return {"error": "Sem dados de artilheiros para esta liga/temporada"}

    analysis = ml_analyze_topscorers(scorers)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.get("/analysis/injuries/{league_id}/{season}")
async def get_analysis_injuries(league_id: str, season: str):
    """Análise de lesões com detecção de times anômalos"""
    if not ml_analyze_injuries:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_injuries_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("injuries", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    injuries = result.get("response", [])
    analysis = ml_analyze_injuries(injuries)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.post("/analysis/compare-leagues")
async def get_analysis_compare_leagues(body: dict):
    """Comparar múltiplas ligas lado a lado"""
    if not ml_compare_leagues:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    leagues_input = body.get("leagues", [])
    if len(leagues_input) < 2:
        return {"error": "Selecione pelo menos 2 ligas"}

    leagues_data = []

    async def _fetch_one(lg):
        lid    = str(lg.get("id", ""))
        season = str(lg.get("season", ""))
        ckey   = get_cache_key("standings", {"league": lid, "season": season})

        if is_cache_valid(ckey):
            _, cached = cache[ckey]
            standings = cached.get("standings", [])
        else:
            result = await fazer_requisicao("standings", {"league": lid, "season": season})
            if not result:
                return
            standings = []
            for item in result.get("response", []):
                for group in item.get("league", {}).get("standings", []):
                    standings.extend(group)

        if standings:
            leagues_data.append({
                "id":       lg.get("id"),
                "name":     lg.get("name", f"Liga {lid}"),
                "season":   season,
                "standings": standings,
            })

    await asyncio.gather(*[_fetch_one(lg) for lg in leagues_input])

    if len(leagues_data) < 2:
        return {"error": "Dados insuficientes — verifique as ligas selecionadas"}

    return ml_compare_leagues(leagues_data)


@app.get("/analysis/predictions/{league_id}/{season}")
async def get_analysis_predictions(league_id: str, season: str):
    """Previsão de fim de temporada por regressão linear"""
    if not ml_predict_season:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_predictions_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("standings", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    standings = []
    for item in result.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            standings.extend(group)

    if not standings:
        return {"error": "Sem dados de classificação para esta liga/temporada"}

    analysis = ml_predict_season(standings)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.get("/analysis/clusters/{league_id}/{season}")
async def get_analysis_clusters(league_id: str, season: str):
    """K-Means clustering de times por estilo de jogo"""
    if not ml_cluster_teams:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_clusters_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("standings", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    standings = []
    for item in result.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            standings.extend(group)

    if not standings:
        return {"error": "Sem dados de classificação para esta liga/temporada"}

    analysis = ml_cluster_teams(standings)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.get("/analysis/monte-carlo/{league_id}/{season}")
async def get_analysis_monte_carlo(league_id: str, season: str):
    """Simulação Monte Carlo da temporada (10.000 iterações)"""
    if not ml_monte_carlo_season:
        return JSONResponse(status_code=503, content={"error": "Serviço de análise indisponível"})

    cache_key = f"analysis_montecarlo_{league_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    result = await fazer_requisicao("standings", {"league": league_id, "season": season})
    if not result:
        return JSONResponse(status_code=502, content={"error": "Falha na API externa"})

    standings = []
    for item in result.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            standings.extend(group)

    if not standings:
        return {"error": "Sem dados de classificação para esta liga/temporada"}

    analysis = ml_monte_carlo_season(standings)
    cache[cache_key] = (datetime.now().timestamp(), analysis)
    return analysis


@app.get("/fixtures/live")
async def get_fixtures_live():
    """Partidas ao vivo (cache de 60s)"""
    cache_key = "fixtures_live"
    if cache_key in cache:
        ts, data = cache[cache_key]
        if datetime.now().timestamp() - ts <= LIVE_CACHE_TTL:
            return data

    result = await fazer_requisicao("fixtures", {"live": "all"}) or {}
    fixtures = []
    for f in result.get("response", []):
        fix    = f.get("fixture", {})
        status = fix.get("status", {})
        fixtures.append({
            "id":          fix.get("id"),
            "league":      f.get("league", {}).get("name"),
            "league_logo": f.get("league", {}).get("logo"),
            "status":      status.get("short"),
            "status_long": status.get("long"),
            "elapsed":     status.get("elapsed"),
            "home": {
                "name": f.get("teams", {}).get("home", {}).get("name"),
                "logo": f.get("teams", {}).get("home", {}).get("logo"),
            },
            "away": {
                "name": f.get("teams", {}).get("away", {}).get("name"),
                "logo": f.get("teams", {}).get("away", {}).get("logo"),
            },
            "goals": {
                "home": f.get("goals", {}).get("home"),
                "away": f.get("goals", {}).get("away"),
            },
        })

    response_data = {
        "fixtures":   fixtures,
        "count":      len(fixtures),
        "updated_at": datetime.now().isoformat(),
    }
    cache[cache_key] = (datetime.now().timestamp(), response_data)
    return response_data


@app.get("/team/profile/{team_id}/{season}")
async def get_team_profile(team_id: str, season: str):
    """Perfil de time: últimas 10 partidas + próximas 5"""
    cache_key = f"team_profile_{team_id}_{season}"
    if is_cache_valid(cache_key):
        _, data = cache[cache_key]
        return data

    past, nxt = await asyncio.gather(
        fazer_requisicao("fixtures", {"team": team_id, "season": season, "last": 10}),
        fazer_requisicao("fixtures", {"team": team_id, "next": 5}),
    )

    def _parse(result, tid_str: str):
        tid = int(tid_str)
        out = []
        for f in (result or {}).get("response", []):
            home_id = f.get("teams", {}).get("home", {}).get("id")
            is_home = (home_id == tid)
            g  = f.get("goals", {})
            gf = g.get("home") if is_home else g.get("away")
            ga = g.get("away") if is_home else g.get("home")
            gf = gf or 0
            ga = ga or 0
            res = "W" if gf > ga else ("D" if gf == ga else "L")
            side = "away" if is_home else "home"
            out.append({
                "date":          f.get("fixture", {}).get("date"),
                "is_home":       is_home,
                "opponent":      f.get("teams", {}).get(side, {}).get("name"),
                "opponent_logo": f.get("teams", {}).get(side, {}).get("logo"),
                "goals_for":     gf,
                "goals_against": ga,
                "result":        res,
                "status":        f.get("fixture", {}).get("status", {}).get("short"),
                "league":        f.get("league", {}).get("name"),
            })
        return out

    data = {
        "recent":   _parse(past, team_id),
        "upcoming": _parse(nxt,  team_id),
    }
    cache[cache_key] = (datetime.now().timestamp(), data)
    return data


@app.get("/cache/stats")
async def get_cache_stats():
    """Estatísticas do cache persistente"""
    if hasattr(cache, "stats"):
        return cache.stats()
    return {"entries": len(cache), "ttl_seconds": CACHE_TTL, "type": "in-memory"}


# ============================================================================
# ENDPOINTS DE EXPORT (CSV)
# ============================================================================

@app.get("/export/leagues")
async def export_get_leagues():
    """Retorna lista de ligas disponíveis"""
    return {
        "leagues": [
            {
                "id": key,
                "name": value["name"],
                "country": value["country"]
            }
            for key, value in LEAGUES.items()
        ]
    }

@app.get("/export/data-types")
async def export_get_data_types():
    """Retorna tipos de dados disponíveis"""
    return {
        "types": [
            {
                "id": key,
                "name": value["name"],
                "endpoint": value["endpoint"],
                "fields": value["fields"]
            }
            for key, value in DATA_TYPES.items()
        ]
    }

@app.post("/export/fixtures")
async def export_fixtures(
    league_id: str = Query(...),
    season: str = Query(...),
    from_date: str = Query(...),
    to_date: str = Query(...)
):
    """Exportar fixtures e retornar CSV"""
    try:
        print(f"[EXPORT] Fixtures: Liga {league_id}, {from_date} a {to_date}")
        
        data = await export_get_fixtures(league_id, season, from_date, to_date)
        
        if not data:
            return {
                "success": False,
                "message": "Nenhum dado encontrado",
                "data": []
            }
        
        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{league_id}_fixtures_{season}_{timestamp}.csv"
        
        fields = DATA_TYPES["1"]["fields"]
        save_csv(data, filename, fields)
        
        return {
            "success": True,
            "message": f"{len(data)} fixtures exportadas com sucesso",
            "filename": filename,
            "data": data,
            "count": len(data)
        }
    
    except Exception as e:
        print(f"[ERROR] Export fixtures: {e}")
        return {
            "success": False,
            "message": f"Erro ao exportar: {str(e)}",
            "data": []
        }

@app.post("/export/standings")
async def export_standings(
    league_id: str = Query(...),
    season: str = Query(...)
):
    """Exportar tabela de classificação"""
    try:
        print(f"[EXPORT] Standings: Liga {league_id}, Temporada {season}")
        
        data = await export_get_standings(league_id, season)

        if not data:
            return {
                "success": False,
                "message": "Nenhum dado encontrado",
                "data": []
            }

        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{league_id}_standings_{season}_{timestamp}.csv"
        
        fields = DATA_TYPES["2"]["fields"]
        save_csv(data, filename, fields)
        
        return {
            "success": True,
            "message": f"{len(data)} times exportados com sucesso",
            "filename": filename,
            "data": data,
            "count": len(data)
        }
    
    except Exception as e:
        print(f"[ERROR] Export standings: {e}")
        return {
            "success": False,
            "message": f"Erro ao exportar: {str(e)}",
            "data": []
        }

@app.post("/export/topscorers")
async def export_topscorers(
    league_id: str = Query(...),
    season: str = Query(...)
):
    """Exportar artilheiros"""
    try:
        print(f"[EXPORT] Top Scorers: Liga {league_id}, Temporada {season}")
        
        data = await export_get_top_scorers(league_id, season)

        if not data:
            return {
                "success": False,
                "message": "Nenhum dado encontrado",
                "data": []
            }

        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{league_id}_topscorers_{season}_{timestamp}.csv"
        
        fields = DATA_TYPES["3"]["fields"]
        save_csv(data, filename, fields)
        
        return {
            "success": True,
            "message": f"{len(data)} artilheiros exportados com sucesso",
            "filename": filename,
            "data": data,
            "count": len(data)
        }
    
    except Exception as e:
        print(f"[ERROR] Export topscorers: {e}")
        return {
            "success": False,
            "message": f"Erro ao exportar: {str(e)}",
            "data": []
        }

@app.post("/export/injuries")
async def export_injuries(
    league_id: str = Query(...),
    season: str = Query(...)
):
    """Exportar lesões"""
    try:
        print(f"[EXPORT] Injuries: Liga {league_id}, Temporada {season}")
        
        data = await export_get_injuries(league_id, season)
        
        if not data:
            return {
                "success": False,
                "message": "Nenhum dado encontrado",
                "data": []
            }
        
        from datetime import datetime as dt
        timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{league_id}_injuries_{season}_{timestamp}.csv"
        
        fields = DATA_TYPES["4"]["fields"]
        save_csv(data, filename, fields)
        
        return {
            "success": True,
            "message": f"{len(data)} lesões exportadas com sucesso",
            "filename": filename,
            "data": data,
            "count": len(data)
        }
    
    except Exception as e:
        print(f"[ERROR] Export injuries: {e}")
        return {
            "success": False,
            "message": f"Erro ao exportar: {str(e)}",
            "data": []
        }

@app.get("/export/downloads")
async def export_list_downloads():
    """Listar arquivos exportados"""
    try:
        if not EXPORTS_DIR:
            return {"success": False, "exports": []}
        
        files = list(EXPORTS_DIR.glob("*.csv"))
        
        exports = []
        for file in sorted(files, reverse=True):
            exports.append({
                "filename": file.name,
                "size_kb": file.stat().st_size / 1024,
                "created": file.stat().st_mtime
            })
        
        return {
            "success": True,
            "exports": exports,
            "count": len(exports)
        }
    
    except Exception as e:
        print(f"[ERROR] List downloads: {e}")
        return {
            "success": False,
            "message": f"Erro ao listar arquivos: {str(e)}",
            "exports": []
        }

# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Football API v1.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================================
# EXECUTAR
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
