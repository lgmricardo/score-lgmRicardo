import requests
import json
from datetime import datetime, timedelta

# Sua chave API
API_KEY = "a01a2d1d96031b27f0ea1c79c045e83e"
BASE_URL = "https://v3.football.api-sports.io"

# Headers obrigatórios
HEADERS = {
    "x-apisports-key": API_KEY
}

def fazer_requisicao(endpoint, parametros=None):
    """Faz uma requisição à API e retorna os dados"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=5)
        response.raise_for_status()
        dados = response.json()
        
        if dados.get("errors"):
            print(f"❌ Erro na API: {dados['errors']}")
            return None
        
        # Verifica se chegou ao limite de requisições
        remaining = response.headers.get("x-ratelimit-requests-remaining")
        if remaining:
            print(f"ℹ️  Requisições restantes hoje: {remaining}")
        
        return dados
    except requests.exceptions.Timeout:
        print("❌ Timeout: A API demorou muito para responder")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return None

def formatar_data(data):
    """Formata data para o padrão YYYY-MM-DD"""
    return data.strftime("%Y-%m-%d")

def listar_proximas_partidas():
    """Lista as próximas partidas usando a data atual"""
    hoje = datetime.utcnow().date()
    print(f"\n{'='*60}")
    print(f"⚽ PRÓXIMAS PARTIDAS - {formatar_data(hoje)}")
    print(f"{'='*60}\n")

    params = {
        "date": formatar_data(hoje)
    }
    dados = fazer_requisicao("/fixtures", params)
    
    if not dados:
        print("❌ Erro ao buscar partidas")
        return

    fixtures = dados.get("response", [])
    if not fixtures:
        print("Nenhuma partida encontrada para a data informada.")
        return
    
    for fixture in fixtures:
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]
        data = fixture["fixture"]["date"]
        status = fixture["fixture"]["status"]["short"]
        
        print(f"{home_team} vs {away_team}")
        print(f"   Data: {data}")
        print(f"   Status: {status}")
        print()

def listar_resultados_recentes():
    """Lista os resultados finais de hoje"""
    hoje = datetime.utcnow().date()
    print(f"\n{'='*60}")
    print(f"🏆 RESULTADOS RECENTES - {formatar_data(hoje)}")
    print(f"{'='*60}\n")
    
    params = {
        "date": formatar_data(hoje),
        "status": "FT"
    }
    dados = fazer_requisicao("/fixtures", params)
    
    if not dados:
        print("❌ Erro ao buscar resultados")
        return

    fixtures = dados.get("response", [])
    if not fixtures:
        print("Nenhum resultado finalizado encontrado para hoje.")
        return
    
    for fixture in fixtures:
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]
        goals_home = fixture["goals"]["home"]
        goals_away = fixture["goals"]["away"]
        data = fixture["fixture"]["date"]
        
        print(f"{home_team} {goals_home} x {goals_away} {away_team}")
        print(f"   Data: {data}")
        print()

def listar_partidas_intervalo():
    """Lista partidas entre duas datas"""
    hoje = datetime.utcnow().date()
    proximos_dias = hoje + timedelta(days=7)
    
    print(f"\n{'='*60}")
    print(f"⚽ PARTIDAS (próximos 7 dias)")
    print(f"{'='*60}\n")
    
    params = {
        "from": formatar_data(hoje),
        "to": formatar_data(proximos_dias)
    }
    dados = fazer_requisicao("/fixtures", params)
    
    if not dados:
        print("❌ Erro ao buscar partidas")
        return

    fixtures = dados.get("response", [])
    if not fixtures:
        print("Nenhuma partida encontrada para os próximos 7 dias.")
        return
    
    for fixture in fixtures:
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]
        data = fixture["fixture"]["date"]
        status = fixture["fixture"]["status"]["short"]
        
        print(f"{home_team} vs {away_team}")
        print(f"   Data: {data} | Status: {status}")
        print()

def listar_proximas_do_time(team_id):
    """Lista próximas partidas de um time"""
    print(f"\n{'='*60}")
    print(f"⚽ PRÓXIMAS PARTIDAS DO TIME ID {team_id}")
    print(f"{'='*60}\n")
    
    params = {
        "team": team_id,
        "next": 10
    }
    dados = fazer_requisicao("/fixtures", params)
    
    if not dados:
        print("❌ Erro ao buscar partidas")
        return

    fixtures = dados.get("response", [])
    if not fixtures:
        print(f"Nenhuma partida encontrada para o time {team_id}.")
        return
    
    for fixture in fixtures:
        home_team = fixture["teams"]["home"]["name"]
        away_team = fixture["teams"]["away"]["name"]
        data = fixture["fixture"]["date"]
        status = fixture["fixture"]["status"]["short"]
        
        print(f"{home_team} vs {away_team}")
        print(f"   Data: {data} | Status: {status}")
        print()

def listar_tabela(liga_id, temporada):
    """Mostra a tabela de uma liga"""
    print(f"\n{'='*60}")
    print(f"📊 TABELA - LIGA ID {liga_id} - TEMPORADA {temporada}")
    print(f"{'='*60}\n")
    
    params = {"league": liga_id, "season": temporada}
    dados = fazer_requisicao("/standings", params)
    
    if not dados:
        print("❌ Erro ao buscar tabela")
        return
    
    standings = dados.get("response", [])
    if not standings:
        print("Sem dados de tabela")
        return
    
    league_data = standings[0]["league"]
    grupos = standings[0]["standings"]
    
    for i, grupo in enumerate(grupos):
        if len(grupos) > 1:
            print(f"\n--- {grupo[0]['group']} ---\n")
        
        print(f"{'Pos':<4} {'Time':<25} {'P':<3} {'V':<3} {'E':<3} {'D':<3} {'GF':<3} {'GC':<3} {'SG':<4} {'Pts':<4}")
        print("-" * 80)
        
        for team in grupo:
            pos = team["rank"]
            nome = team["team"]["name"][:24]
            jogos = team["all"]["played"]
            vitorias = team["all"]["win"]
            empates = team["all"]["draw"]
            derrotas = team["all"]["lose"]
            gf = team["all"]["goals"]["for"]
            gc = team["all"]["goals"]["against"]
            sg = gf - gc
            pts = team["points"]
            
            print(f"{pos:<4} {nome:<25} {jogos:<3} {vitorias:<3} {empates:<3} {derrotas:<3} {gf:<3} {gc:<3} {sg:<4} {pts:<4}")

def listar_ligas(busca=""):
    """Lista ligas disponíveis"""
    print(f"\n{'='*60}")
    print(f"🌍 LIGAS DISPONÍVEIS")
    print(f"{'='*60}\n")
    
    params = {}
    if busca:
        params["search"] = busca
    
    dados = fazer_requisicao("/leagues", params)
    
    if not dados:
        print("❌ Erro ao buscar ligas")
        return
    
    for league in dados.get("response", [])[:20]:
        liga_id = league["league"]["id"]
        nome = league["league"]["name"]
        pais = league["country"]["name"]
        tipo = league["league"]["type"]
        
        print(f"ID: {liga_id:<4} | {nome:<30} | {pais:<20} | Tipo: {tipo}")

def listar_times(liga_id, temporada):
    """Lista todos os times de uma liga"""
    print(f"\n{'='*60}")
    print(f"🏟️  TIMES - LIGA ID {liga_id} - TEMPORADA {temporada}")
    print(f"{'='*60}\n")
    
    params = {
        "league": liga_id,
        "season": temporada
    }
    dados = fazer_requisicao("/teams", params)
    
    if not dados:
        print("❌ Erro ao buscar times")
        return

    times = dados.get("response", [])
    if not times:
        print("Nenhum time encontrado.")
        return
    
    print(f"{'ID':<6} {'Nome':<35} {'País':<20}")
    print("-" * 65)
    
    for time in times:
        team_id = time["team"]["id"]
        nome = time["team"]["name"][:34]
        pais = time["country"] if time.get("country") else "N/A"
        
        print(f"{team_id:<6} {nome:<35} {pais:<20}")

def artilheiros(liga_id, temporada):
    """Mostra top 10 artilheiros de uma liga"""
    print(f"\n{'='*60}")
    print(f"🎯 TOP 10 ARTILHEIROS - LIGA {liga_id} - {temporada}")
    print(f"{'='*60}\n")
    
    params = {"league": liga_id, "season": temporada}
    dados = fazer_requisicao("/players/topscorers", params)
    
    if not dados:
        print("❌ Erro ao buscar artilheiros")
        return
    
    print(f"{'Pos':<4} {'Jogador':<30} {'Time':<25} {'Gols':<4} {'Pen':<4}")
    print("-" * 70)
    
    for i, player in enumerate(dados.get("response", []), 1):
        nome = player["player"]["name"][:29]
        time = player["statistics"][0]["team"]["name"][:24]
        gols = player["statistics"][0]["goals"]["total"] or 0
        penaltis = player["statistics"][0]["goals"]["penalties"] or 0
        
        print(f"{i:<4} {nome:<30} {time:<25} {gols:<4} {penaltis:<4}")

def assistentes(liga_id, temporada):
    """Mostra top 10 assistentes de uma liga"""
    print(f"\n{'='*60}")
    print(f"🅰️  TOP 10 ASSISTENTES - LIGA {liga_id} - {temporada}")
    print(f"{'='*60}\n")
    
    params = {"league": liga_id, "season": temporada}
    dados = fazer_requisicao("/players/topassists", params)
    
    if not dados:
        print("❌ Erro ao buscar assistentes")
        return
    
    print(f"{'Pos':<4} {'Jogador':<30} {'Time':<25} {'Assistências':<4}")
    print("-" * 65)
    
    for i, player in enumerate(dados.get("response", []), 1):
        nome = player["player"]["name"][:29]
        time = player["statistics"][0]["team"]["name"][:24]
        assists = player["statistics"][0]["goals"]["assists"] or 0
        
        print(f"{i:<4} {nome:<30} {time:<25} {assists:<4}")

def menu():
    """Menu interativo"""
    while True:
        print(f"\n{'='*60}")
        print("⚽ API-FOOTBALL - TERMINAL v2.0")
        print(f"{'='*60}")
        print("\n🔷 PARTIDAS E RESULTADOS")
        print("  1. Próximas partidas (hoje)")
        print("  2. Últimos resultados (hoje)")
        print("  3. Partidas dos próximos 7 dias")
        print("  4. Próximas partidas de um time")
        print("\n🔶 LIGAS E TABELAS")
        print("  5. Ver tabela de uma liga")
        print("  6. Listar ligas")
        print("  7. Listar times de uma liga")
        print("\n🔴 JOGADORES")
        print("  8. Top artilheiros")
        print("  9. Top assistentes")
        print("\n⚪ SAIR")
        print("  0. Sair")
        print()
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            listar_proximas_partidas()
        
        elif opcao == "2":
            listar_resultados_recentes()
        
        elif opcao == "3":
            listar_partidas_intervalo()
        
        elif opcao == "4":
            print("\nExemplos de team_id:")
            print("  33 = Manchester United")
            print("  34 = Newcastle")
            print("  39 = Liverpool")
            print("  40 = Manchester City")
            print("  85 = Paris Saint-Germain")
            
            team_id = input("\nDigite o ID do time: ").strip()
            if team_id.isdigit():
                listar_proximas_do_time(int(team_id))
            else:
                print("❌ ID inválido")
        
        elif opcao == "5":
            print("\nExemplos de liga_id:")
            print("  39 = Premier League (Inglaterra)")
            print("  61 = Ligue 1 (França)")
            print("  78 = Bundesliga (Alemanha)")
            print("  135 = Serie A (Itália)")
            print("  71 = Serie A (Brasil)")
            
            liga_id = input("\nDigite o ID da liga: ").strip()
            temporada = input("Digite a temporada (ex: 2024): ").strip()
            
            if liga_id.isdigit() and temporada.isdigit():
                listar_tabela(int(liga_id), int(temporada))
            else:
                print("❌ Entrada inválida")
        
        elif opcao == "6":
            busca = input("Digite parte do nome da liga (deixe em branco para todas): ").strip()
            listar_ligas(busca)
        
        elif opcao == "7":
            liga_id = input("Digite o ID da liga: ").strip()
            temporada = input("Digite a temporada (ex: 2024): ").strip()
            
            if liga_id.isdigit() and temporada.isdigit():
                listar_times(int(liga_id), int(temporada))
            else:
                print("❌ Entrada inválida")
        
        elif opcao == "8":
            liga_id = input("Digite o ID da liga: ").strip()
            temporada = input("Digite a temporada (ex: 2024): ").strip()
            
            if liga_id.isdigit() and temporada.isdigit():
                artilheiros(int(liga_id), int(temporada))
            else:
                print("❌ Entrada inválida")
        
        elif opcao == "9":
            liga_id = input("Digite o ID da liga: ").strip()
            temporada = input("Digite a temporada (ex: 2024): ").strip()
            
            if liga_id.isdigit() and temporada.isdigit():
                assistentes(int(liga_id), int(temporada))
            else:
                print("❌ Entrada inválida")
        
        elif opcao == "0":
            print("\n👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    menu()