#!/usr/bin/env python3

"""
Football Data Exporter
Extrai dados de ligas da API-Football v3 e exporta para CSV
"""

import os
import csv
import json
import httpx
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://v3.football.api-sports.io"
DATA_DIR = Path(__file__).parent.parent / "data"
EXPORTS_DIR = DATA_DIR / "exports"
CACHE_DIR = DATA_DIR / "cache"

# Criar diretórios se não existirem
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

if not API_KEY:
    print("❌ ERRO: API_KEY não configurada no .env")
    exit(1)

# ============================================================================
# LIGAS SUPORTADAS
# ============================================================================

LEAGUES = {
    "39": {"name": "Premier League", "country": "England"},
    "61": {"name": "Ligue 1", "country": "France"},
    "78": {"name": "Bundesliga", "country": "Germany"},
    "135": {"name": "Serie A", "country": "Italy"},
    "71": {"name": "Série A", "country": "Brazil"},
    "140": {"name": "La Liga", "country": "Spain"},
    "203": {"name": "Super Lig", "country": "Turkey"},
    "262": {"name": "Eredivisie", "country": "Netherlands"},
    "307": {"name": "Primeira Liga", "country": "Portugal"},
}

# ============================================================================
# TIPOS DE DADOS
# ============================================================================

DATA_TYPES = {
    "1": {
        "name": "Fixtures (Partidas)",
        "endpoint": "fixtures",
        "fields": ["id", "league", "season", "timestamp", "date", "status", "home", "away", "goals_home", "goals_away", "halftime_home", "halftime_away"]
    },
    "2": {
        "name": "Standings (Tabela)",
        "endpoint": "standings",
        "fields": ["position", "team", "played", "wins", "draws", "losses", "points", "goals_for", "goals_against", "goal_difference"]
    },
    "3": {
        "name": "Top Scorers (Artilheiros)",
        "endpoint": "players/topscorers",
        "fields": ["rank", "player", "team", "season", "goals", "assists", "appearances"]
    },
    "4": {
        "name": "Injuries (Lesões)",
        "endpoint": "injuries",
        "fields": ["player", "team", "season", "fixture_id", "reason", "until"]
    },
    "5": {
        "name": "Statistics (Estatísticas)",
        "endpoint": "statistics",
        "fields": ["team", "matches", "wins", "draws", "losses", "goals_for", "goals_against"]
    },
}

# ============================================================================
# CORES PARA TERMINAL
# ============================================================================

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def print_header(text: str):
    """Imprimir cabeçalho"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}  {text}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

def print_success(text: str):
    """Imprimir mensagem de sucesso"""
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")

def print_error(text: str):
    """Imprimir mensagem de erro"""
    print(f"{Colors.RED}❌ {text}{Colors.NC}")

def print_info(text: str):
    """Imprimir mensagem informativa"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.NC}")

def print_warning(text: str):
    """Imprimir aviso"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")

def print_step(text: str):
    """Imprimir passo"""
    print(f"{Colors.MAGENTA}→ {text}{Colors.NC}")

# ============================================================================
# REQUISIÇÕES À API
# ============================================================================

async def fazer_requisicao(endpoint: str, params: dict) -> Optional[Dict]:
    """Fazer requisição à API-Football"""
    headers = {
        "x-apisports-key": API_KEY,
        "x-apisports-host": "v3.football.api-sports.io"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            url = f"{BASE_URL}/{endpoint}"
            print_step(f"GET {url}")
            
            response = await client.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Mostrar rate limit
            remaining = response.headers.get("x-ratelimit-requests-remaining", "?")
            print_info(f"Rate limit restante: {remaining}")
            
            return data
    
    except httpx.HTTPError as e:
        print_error(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print_error(f"Erro inesperado: {e}")
        return None

# ============================================================================
# EXTRAÇÃO DE DADOS
# ============================================================================

async def get_fixtures(league_id: str, season: str, from_date: str, to_date: str) -> List[Dict]:
    """Extrair dados de fixtures (partidas)"""
    print_header("EXTRAINDO FIXTURES")
    
    fixtures = []
    
    params = {
        "league": league_id,
        "season": season,
        "from": from_date,
        "to": to_date
    }
    
    data = await fazer_requisicao("fixtures", params)
    
    if not data or data.get("errors"):
        print_error(f"Erro ao extrair fixtures: {data.get('errors') if data else 'Resposta vazia'}")
        return []
    
    print_info(f"Total de partidas encontradas: {data.get('results', 0)}")
    
    for fixture in data.get("response", []):
        fixtures.append({
            "id": fixture.get("id"),
            "league": fixture.get("league", {}).get("name"),
            "season": fixture.get("league", {}).get("season"),
            "timestamp": fixture.get("timestamp"),
            "date": fixture.get("fixture", {}).get("date"),
            "status": fixture.get("fixture", {}).get("status", {}).get("short"),
            "home": fixture.get("teams", {}).get("home", {}).get("name"),
            "away": fixture.get("teams", {}).get("away", {}).get("name"),
            "goals_home": fixture.get("goals", {}).get("home"),
            "goals_away": fixture.get("goals", {}).get("away"),
            "halftime_home": fixture.get("score", {}).get("halftime", {}).get("home"),
            "halftime_away": fixture.get("score", {}).get("halftime", {}).get("away"),
        })
    
    print_success(f"{len(fixtures)} partidas extraídas")
    return fixtures

async def get_standings(league_id: str, season: str) -> List[Dict]:
    """Extrair dados de tabela de classificação"""
    print_header("EXTRAINDO STANDINGS")
    
    standings = []
    
    params = {
        "league": league_id,
        "season": season
    }
    
    data = await fazer_requisicao("standings", params)
    
    if not data or data.get("errors"):
        print_error(f"Erro ao extrair standings: {data.get('errors') if data else 'Resposta vazia'}")
        return []
    
    for item in data.get("response", []):
        for group in item.get("league", {}).get("standings", []):
            for standing in group:
                standings.append({
                    "position": standing.get("rank"),
                    "team": standing.get("team", {}).get("name"),
                    "played": standing.get("all", {}).get("played"),
                    "wins": standing.get("all", {}).get("win"),
                    "draws": standing.get("all", {}).get("draw"),
                    "losses": standing.get("all", {}).get("lose"),
                    "points": standing.get("points"),
                    "goals_for": standing.get("all", {}).get("goals", {}).get("for"),
                    "goals_against": standing.get("all", {}).get("goals", {}).get("against"),
                    "goal_difference": standing.get("goalsDiff"),
                })
    
    print_success(f"{len(standings)} times na tabela")
    return standings

async def get_top_scorers(league_id: str, season: str) -> List[Dict]:
    """Extrair dados dos melhores artilheiros"""
    print_header("EXTRAINDO TOP SCORERS")
    
    scorers = []
    
    params = {
        "league": league_id,
        "season": season
    }
    
    data = await fazer_requisicao("players/topscorers", params)
    
    if not data or data.get("errors"):
        print_error(f"Erro ao extrair top scorers: {data.get('errors') if data else 'Resposta vazia'}")
        return []
    
    for idx, player in enumerate(data.get("response", []), 1):
        scorers.append({
            "rank": idx,
            "player": player.get("player", {}).get("name"),
            "team": player.get("statistics", [{}])[0].get("team", {}).get("name") if player.get("statistics") else None,
            "season": season,
            "goals": player.get("statistics", [{}])[0].get("goals", {}).get("total") if player.get("statistics") else None,
            "assists": player.get("statistics", [{}])[0].get("goals", {}).get("assists") if player.get("statistics") else None,
            "appearances": player.get("statistics", [{}])[0].get("games", {}).get("appearences") if player.get("statistics") else None,
        })
    
    print_success(f"{len(scorers)} artilheiros extraídos")
    return scorers

async def get_injuries(league_id: str, season: str) -> List[Dict]:
    """Extrair dados de lesões"""
    print_header("EXTRAINDO INJURIES")
    
    injuries = []
    
    params = {
        "league": league_id,
        "season": season
    }
    
    data = await fazer_requisicao("injuries", params)
    
    if not data or data.get("errors"):
        print_error(f"Erro ao extrair injuries: {data.get('errors') if data else 'Resposta vazia'}")
        return []
    
    for injury in data.get("response", []):
        injuries.append({
            "player": injury.get("player", {}).get("name"),
            "team": injury.get("team", {}).get("name"),
            "season": season,
            "fixture_id": injury.get("fixture", {}).get("id"),
            "reason": injury.get("player", {}).get("reason"),
            "until": injury.get("player", {}).get("until"),
        })
    
    print_success(f"{len(injuries)} lesões extraídas")
    return injuries

# ============================================================================
# SALVAR EM CSV
# ============================================================================

def save_csv(data: List[Dict], filename: str, fields: List[str]):
    """Salvar dados em arquivo CSV"""
    if not data:
        print_warning("Nenhum dado para salvar")
        return False
    
    filepath = EXPORTS_DIR / filename
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        
        file_size = filepath.stat().st_size / 1024  # KB
        print_success(f"Arquivo salvo: {filepath}")
        print_info(f"Tamanho: {file_size:.2f} KB")
        print_info(f"Linhas: {len(data)}")
        
        return True
    
    except Exception as e:
        print_error(f"Erro ao salvar CSV: {e}")
        return False

# ============================================================================
# MENU INTERATIVO
# ============================================================================

def show_leagues():
    """Mostrar menu de ligas"""
    print_header("SELECIONE UMA LIGA")
    
    for key, league in LEAGUES.items():
        print(f"  {Colors.CYAN}{key}{Colors.NC}) {league['name']} ({league['country']})")
    
    while True:
        choice = input(f"\n{Colors.WHITE}Digite o número da liga: {Colors.NC}").strip()
        if choice in LEAGUES:
            return choice
        print_error("Opção inválida")

def show_data_types():
    """Mostrar menu de tipos de dados"""
    print_header("SELECIONE O TIPO DE DADOS")
    
    for key, data_type in DATA_TYPES.items():
        print(f"  {Colors.CYAN}{key}{Colors.NC}) {data_type['name']}")
    
    while True:
        choice = input(f"\n{Colors.WHITE}Digite o número do tipo de dado: {Colors.NC}").strip()
        if choice in DATA_TYPES:
            return choice
        print_error("Opção inválida")

def input_year() -> str:
    """Input de ano"""
    while True:
        year = input(f"{Colors.WHITE}Digite o ano (ex: 2024): {Colors.NC}").strip()
        if year.isdigit() and len(year) == 4:
            return year
        print_error("Ano inválido")

def input_date(label: str) -> str:
    """Input de data"""
    while True:
        date = input(f"{Colors.WHITE}Digite a data {label} (YYYY-MM-DD): {Colors.NC}").strip()
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return date
        except ValueError:
            print_error("Formato de data inválido")

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Função principal"""
    print_header("FOOTBALL DATA EXPORTER 🚀⚽")
    
    # Seleções
    league_id = show_leagues()
    league_name = LEAGUES[league_id]["name"]
    
    data_type_id = show_data_types()
    data_type = DATA_TYPES[data_type_id]
    data_type_name = data_type["name"]
    
    season = input_year()
    
    # Datas (apenas para fixtures)
    if data_type_id == "1":
        from_date = input_date("inicial (YYYY-MM-DD)")
        to_date = input_date("final (YYYY-MM-DD)")
    else:
        from_date = None
        to_date = None
    
    print_header("RESUMO DA EXPORTAÇÃO")
    print_info(f"Liga: {league_name}")
    print_info(f"Tipo: {data_type_name}")
    print_info(f"Temporada: {season}")
    if from_date:
        print_info(f"Período: {from_date} a {to_date}")
    
    confirm = input(f"\n{Colors.WHITE}Deseja continuar? (s/n): {Colors.NC}").strip().lower()
    if confirm != 's':
        print_warning("Operação cancelada")
        return
    
    # Extrair dados
    print_header("PROCESSANDO")
    
    if data_type_id == "1":
        data = await get_fixtures(league_id, season, from_date, to_date)
    elif data_type_id == "2":
        data = await get_standings(league_id, season)
    elif data_type_id == "3":
        data = await get_top_scorers(league_id, season)
    elif data_type_id == "4":
        data = await get_injuries(league_id, season)
    
    if not data:
        print_error("Nenhum dado foi extraído")
        return
    
    # Salvar em CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{league_id}_{data_type_id}_{season}_{timestamp}.csv"
    
    if save_csv(data, filename, data_type["fields"]):
        print_success("Exportação concluída com sucesso!")
        print_info(f"📁 Pasta: {EXPORTS_DIR}")
    else:
        print_error("Erro ao exportar dados")

# ============================================================================
# EXECUTAR
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\nOperação cancelada pelo usuário")
    except Exception as e:
        print_error(f"Erro fatal: {e}")
