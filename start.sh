#!/bin/bash

################################################################################
# Football App Launcher - Script Sofisticado
# Autor: Script Automático
# Descrição: Gerencia Backend (FastAPI), BFF (Express) e Frontend (Vue.js)
################################################################################

set -e

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

BASE_DIR="/Users/lgmricardo/Documents/score-lgmRicardo"
BACKEND_DIR="$BASE_DIR/backend"
BFF_DIR="$BASE_DIR/bff"
FRONTEND_DIR="$BASE_DIR/frontend"

BACKEND_PORT=8000
BFF_PORT=3001
FRONTEND_PORT=5173

# PIDs files
BACKEND_PID_FILE="/tmp/football_backend.pid"
BFF_PID_FILE="/tmp/football_bff.pid"
FRONTEND_PID_FILE="/tmp/football_frontend.pid"

# ============================================================================
# CORES E ESTILOS
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_info() {
    echo -e "${CYAN}ℹ️  ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✅ ${NC}$1"
}

print_error() {
    echo -e "${RED}❌ ${NC}$1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  ${NC}$1"
}

print_step() {
    echo -e "${MAGENTA}→${NC} $1"
}

separator() {
    echo -e "${GRAY}─────────────────────────────────────────────────────────────${NC}"
}

# ============================================================================
# VERIFICAÇÕES PRÉ-LAUNCH
# ============================================================================

check_dependencies() {
    print_header "VERIFICANDO DEPENDÊNCIAS"
    
    local missing=0
    
    # Checar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        print_success "Python: $PYTHON_VERSION"
    else
        print_error "Python3 não encontrado"
        missing=$((missing + 1))
    fi
    
    # Checar Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js: $NODE_VERSION"
    else
        print_error "Node.js não encontrado"
        missing=$((missing + 1))
    fi
    
    # Checar npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm: $NPM_VERSION"
    else
        print_error "npm não encontrado"
        missing=$((missing + 1))
    fi
    
    # Checar diretórios
    if [ -d "$BACKEND_DIR" ]; then
        print_success "Backend dir: $BACKEND_DIR"
    else
        print_error "Backend dir não encontrado: $BACKEND_DIR"
        missing=$((missing + 1))
    fi
    
    if [ -d "$BFF_DIR" ]; then
        print_success "BFF dir: $BFF_DIR"
    else
        print_error "BFF dir não encontrado: $BFF_DIR"
        missing=$((missing + 1))
    fi
    
    if [ -d "$FRONTEND_DIR" ]; then
        print_success "Frontend dir: $FRONTEND_DIR"
    else
        print_error "Frontend dir não encontrado: $FRONTEND_DIR"
        missing=$((missing + 1))
    fi
    
    if [ $missing -gt 0 ]; then
        print_error "Faltam $missing dependência(s). Corrija e tente novamente."
        exit 1
    fi
    
    print_success "Todas as dependências OK!"
    separator
}

# ============================================================================
# VERIFICAÇÃO DE PORTAS
# ============================================================================

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Porta em uso
    else
        return 1  # Porta livre
    fi
}

check_ports() {
    print_header "VERIFICANDO PORTAS"
    
    local ports_in_use=0
    
    if check_port $BACKEND_PORT; then
        print_warning "Porta $BACKEND_PORT já está em uso"
        ports_in_use=$((ports_in_use + 1))
    else
        print_success "Porta $BACKEND_PORT: LIVRE"
    fi
    
    if check_port $BFF_PORT; then
        print_warning "Porta $BFF_PORT já está em uso"
        ports_in_use=$((ports_in_use + 1))
    else
        print_success "Porta $BFF_PORT: LIVRE"
    fi
    
    if check_port $FRONTEND_PORT; then
        print_warning "Porta $FRONTEND_PORT já está em uso"
        ports_in_use=$((ports_in_use + 1))
    else
        print_success "Porta $FRONTEND_PORT: LIVRE"
    fi
    
    if [ $ports_in_use -gt 0 ]; then
        print_warning "Algumas portas estão em uso. Tentando limpar..."
        cleanup_old_processes
        sleep 2
    fi
    
    separator
}

# ============================================================================
# LIMPEZA DE PROCESSOS
# ============================================================================

cleanup_old_processes() {
    print_step "Limpando processos antigos..."
    
    # Kill by port
    if check_port $BACKEND_PORT; then
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        print_info "Processo na porta $BACKEND_PORT encerrado"
    fi
    
    if check_port $BFF_PORT; then
        lsof -ti:$BFF_PORT | xargs kill -9 2>/dev/null || true
        print_info "Processo na porta $BFF_PORT encerrado"
    fi
    
    if check_port $FRONTEND_PORT; then
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        print_info "Processo na porta $FRONTEND_PORT encerrado"
    fi
}

# ============================================================================
# INICIALIZAÇÃO DOS SERVIÇOS
# ============================================================================

start_backend() {
    print_step "Iniciando Backend (FastAPI)..."
    
    osascript <<EOF
tell application "Terminal"
    do script "cd $BACKEND_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port $BACKEND_PORT"
    set custom title of front window to "Football - Backend"
end tell
EOF
    
    print_success "Backend iniciado em nova aba"
    sleep 3
}

start_bff() {
    print_step "Iniciando BFF (Express)..."
    
    osascript <<EOF
tell application "Terminal"
    do script "cd $BFF_DIR && npm install && npm run dev"
    set custom title of front window to "Football - BFF"
end tell
EOF
    
    print_success "BFF iniciado em nova aba"
    sleep 3
}

start_frontend() {
    print_step "Iniciando Frontend (Vue.js)..."
    
    osascript <<EOF
tell application "Terminal"
    do script "cd $FRONTEND_DIR && npm install && npm install -D tailwindcss postcss autoprefixer && npx tailwindcss init -p && npm run dev"
    set custom title of front window to "Football - Frontend"
end tell
EOF
    
    print_success "Frontend iniciado em nova aba"
    sleep 2
}

# ============================================================================
# HEALTH CHECK
# ============================================================================

health_check() {
    print_header "VERIFICANDO SAÚDE DOS SERVIÇOS"
    
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        attempts=$((attempts + 1))
        
        # Backend
        if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
            print_success "Backend: ONLINE ✓"
        else
            print_warning "Backend: aguardando... ($attempts/$max_attempts)"
        fi
        
        # BFF
        if curl -s http://localhost:$BFF_PORT/health > /dev/null 2>&1; then
            print_success "BFF: ONLINE ✓"
        else
            print_warning "BFF: aguardando... ($attempts/$max_attempts)"
        fi
        
        # Frontend
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            print_success "Frontend: ONLINE ✓"
            break
        else
            print_warning "Frontend: aguardando... ($attempts/$max_attempts)"
        fi
        
        sleep 2
    done
    
    separator
}

# ============================================================================
# MENU PRINCIPAL
# ============================================================================

show_menu() {
    echo ""
    echo -e "${WHITE}SELECIONE UMA OPÇÃO:${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} ▶️  Iniciar todos os serviços"
    echo -e "${CYAN}2)${NC} ⏹️  Parar todos os serviços"
    echo -e "${CYAN}3)${NC} 🔄 Reiniciar todos os serviços"
    echo -e "${CYAN}4)${NC} 🌐 Abrir no navegador (http://localhost:5173)"
    echo -e "${CYAN}5)${NC} 📊 Status dos serviços"
    echo -e "${CYAN}6)${NC} ❌ Sair"
    echo ""
    read -p "Digite sua escolha (1-6): " choice
}

# ============================================================================
# STATUS DOS SERVIÇOS
# ============================================================================

show_status() {
    print_header "STATUS DOS SERVIÇOS"
    
    echo -e "${WHITE}Backend (FastAPI):${NC}"
    if check_port $BACKEND_PORT; then
        echo -e "  Status: ${GREEN}✓ ONLINE${NC}"
        echo -e "  URL: http://localhost:$BACKEND_PORT"
        echo -e "  Docs: http://localhost:$BACKEND_PORT/docs"
    else
        echo -e "  Status: ${RED}✗ OFFLINE${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}BFF (Express):${NC}"
    if check_port $BFF_PORT; then
        echo -e "  Status: ${GREEN}✓ ONLINE${NC}"
        echo -e "  URL: http://localhost:$BFF_PORT"
    else
        echo -e "  Status: ${RED}✗ OFFLINE${NC}"
    fi
    
    echo ""
    echo -e "${WHITE}Frontend (Vue.js):${NC}"
    if check_port $FRONTEND_PORT; then
        echo -e "  Status: ${GREEN}✓ ONLINE${NC}"
        echo -e "  URL: http://localhost:$FRONTEND_PORT"
    else
        echo -e "  Status: ${RED}✗ OFFLINE${NC}"
    fi
    
    separator
}

# ============================================================================
# STOP SERVICES
# ============================================================================

stop_all() {
    print_header "PARANDO SERVIÇOS"
    
    cleanup_old_processes
    
    print_success "Todos os serviços foram parados!"
    separator
}

# ============================================================================
# RESTART SERVICES
# ============================================================================

restart_all() {
    print_header "REINICIANDO SERVIÇOS"
    
    stop_all
    sleep 2
    start_all
}

# ============================================================================
# START ALL
# ============================================================================

start_all() {
    print_header "INICIANDO FOOTBALL APP 🚀⚽"
    
    check_dependencies
    check_ports
    
    print_step "Iniciando serviços..."
    echo ""
    
    start_backend
    start_bff
    start_frontend
    
    health_check
    
    print_success "TODOS OS SERVIÇOS INICIADOS COM SUCESSO!"
    echo ""
    print_info "Acessar aplicação: ${GREEN}http://localhost:5173${NC}"
    print_info "API Docs: ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
    echo ""
    separator
}

# ============================================================================
# OPEN BROWSER
# ============================================================================

open_browser() {
    print_step "Abrindo navegador..."
    open "http://localhost:$FRONTEND_PORT"
    print_success "Navegador aberto!"
}

# ============================================================================
# MAIN LOOP
# ============================================================================

main() {
    clear
    
    # Se passou argumento, executar diretamente
    if [ $# -gt 0 ]; then
        case $1 in
            start)
                start_all
                ;;
            stop)
                stop_all
                ;;
            restart)
                restart_all
                ;;
            status)
                show_status
                ;;
            *)
                print_error "Comando desconhecido: $1"
                echo "Uso: $0 {start|stop|restart|status}"
                exit 1
                ;;
        esac
    else
        # Menu interativo
        while true; do
            show_menu
            
            case $choice in
                1)
                    start_all
                    ;;
                2)
                    stop_all
                    ;;
                3)
                    restart_all
                    ;;
                4)
                    open_browser
                    ;;
                5)
                    show_status
                    ;;
                6)
                    print_info "Até logo!"
                    exit 0
                    ;;
                *)
                    print_error "Opção inválida!"
                    sleep 1
                    clear
                    ;;
            esac
        done
    fi
}

# ============================================================================
# EXECUTAR
# ============================================================================

main "$@"