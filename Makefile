# TrustGraph - Makefile
# Comandos útiles para gestionar TrustGraph

.PHONY: help up down logs status load query clean setup makeenv install-cli uninstall-cli

# Colores para output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Muestra esta ayuda
	@echo "$(BLUE)TrustGraph - Comandos disponibles:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'

setup: ## Configuración inicial (setup básico)
	@echo "$(BLUE)🔧 Configurando TrustGraph...$(RESET)"
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(YELLOW)⚠️  Edita .env con tus API keys$(RESET)"; \
	fi
	@mkdir -p data/{cassandra,qdrant,garage,pulsar,prometheus,grafana,loki}
	@echo "$(GREEN)✅ Configuración lista$(RESET}"
	@echo "$(YELLOW)📝 Próximos pasos:$(RESET)"
	@echo "   1. make makeenv    # Wizard interactivo (recomendado)"
	@echo "   2. make up"
	@echo "   3. make load"

makeenv: ## Wizard interactivo para configurar proveedor LLM
	@echo "$(BLUE)🧙‍♂️ Iniciando wizard de configuración...$(RESET)"
	@python3 scripts/setup_env.py

up: ## Inicia TrustGraph
	@echo "$(BLUE)🚀 Iniciando TrustGraph...$(RESET)"
	@docker compose up -d
	@echo "$(GREEN)✅ Servicios iniciados$(RESET)"
	@echo "$(YELLOW)⏳ Esperando a que estén listos...$(RESET)"
	@sleep 10
	@docker compose ps
	@echo ""
	@echo "$(GREEN)📊 Servicios disponibles:$(RESET)"
	@echo "   Workbench: http://localhost:8888"
	@echo "   API:       http://localhost:8080"
	@echo "   Grafana:   http://localhost:3000"

down: ## Detiene TrustGraph
	@echo "$(BLUE)🛑 Deteniendo TrustGraph...$(RESET)"
	@docker compose down
	@echo "$(GREEN)✅ Servicios detenidos$(RESET)"

logs: ## Muestra logs
	@docker compose logs -f

status: ## Estado de los servicios
	@echo "$(BLUE)📊 Estado de servicios:$(RESET)"
	@docker compose ps

health: ## Verifica salud de TrustGraph
	@echo "$(BLUE)🏥 Verificando salud...$(RESET)"
	@curl -s http://localhost:8080/api/v1/health && echo " $(GREEN)✅ OK$(RESET)" || echo " $(RED)❌ No responde$(RESET)"

load: ## Carga documentación del workspace
	@echo "$(BLUE)📚 Cargando documentación...$(RESET)"
	@python scripts/load_docs.py

query: ## Modo interactivo de consultas
	@echo "$(BLUE)💬 Iniciando modo interactivo...$(RESET)"
	@python scripts/query_graphrag.py --interactive

search: ## Búsqueda rápida (usar: make search QUERY="tu búsqueda")
	@if [ -z "$(QUERY)" ]; then \
		echo "$(RED)❌ Usa: make search QUERY='tu búsqueda'$(RESET)"; \
	else \
		python scripts/query_graphrag.py --search "$(QUERY)"; \
	fi

reset: ## Limpia y recarga documentación
	@echo "$(YELLOW)⚠️  Esto eliminará los datos existentes$(RESET)"
	@read -p "¿Continuar? [y/N] " confirm && [ $$confirm = y ] || exit 1
	@docker compose down -v
	@rm -rf data/*
	@mkdir -p data/{cassandra,qdrant,garage,pulsar,prometheus,grafana,loki}
	@docker compose up -d
	@sleep 15
	@python scripts/load_docs.py

clean: ## Limpia contenedores y volúmenes
	@echo "$(YELLOW)⚠️  Esto eliminará TODOS los datos$(RESET)"
	@read -p "¿Continuar? [y/N] " confirm && [ $$confirm = y ] || exit 1
	@docker compose down -v
	@docker system prune -f
	@rm -rf data/*
	@echo "$(GREEN)✅ Limpieza completa$(RESET)"

update: ## Actualiza imágenes
	@echo "$(BLUE)🔄 Actualizando imágenes...$(RESET)"
	@docker compose pull
	@docker compose up -d
	@echo "$(GREEN)✅ Actualizado$(RESET)"

cli: ## Abre shell en el contenedor API Gateway
	@docker compose exec api-gateway /bin/sh

dev: ## Modo desarrollo (logs verbosos)
	@echo "$(BLUE)🛠️  Modo desarrollo...$(RESET)"
	@LOG_LEVEL=DEBUG docker compose up

# Comandos de backup/restore
backup: ## Crea backup de datos
	@echo "$(BLUE)💾 Creando backup...$(RESET)"
	@mkdir -p backups
	@tar czf backups/trustgraph-backup-$$(date +%Y%m%d-%H%M%S).tar.gz data/
	@echo "$(GREEN)✅ Backup creado en backups/$(RESET)"

restore: ## Restaura último backup
	@echo "$(BLUE)📂 Restaurando backup...$(RESET)"
	@latest_backup=$$(ls -t backups/*.tar.gz 2>/dev/null | head -1); \
	if [ -z "$$latest_backup" ]; then \
		echo "$(RED)❌ No hay backups disponibles$(RESET)"; \
	else \
		echo "Restaurando: $$latest_backup"; \
		docker compose down; \
		rm -rf data/*; \
		tar xzf $$latest_backup; \
		docker compose up -d; \
		echo "$(GREEN)✅ Backup restaurado$(RESET)"; \
	fi

# Comandos de proveedor LLM

# Uso general: make provider USE=zai (o kimi, minimax, openai, anthropic, ollama)
# Ejemplos:
#   make provider USE=zai       # Cambia a Z.AI (GLM)
#   make provider USE=kimi      # Cambia a Kimi
#   make provider USE=minimax   # Cambia a MiniMax
#   make provider USE=openai    # Cambia a OpenAI
#   make provider USE=ollama    # Cambia a Ollama local
provider: ## Cambia de proveedor LLM (usar: make provider USE=nombre)
	@if [ -z "$(USE)" ]; then \
		echo "$(BLUE)📊 Proveedores disponibles:$(RESET)"; \
		echo ""; \
		echo "  Uso: $(GREEN)make provider USE=nombre$(RESET)"; \
		echo ""; \
		echo "  Proveedores:"; \
		echo "    $(GREEN)openai$(RESET)    - OpenAI GPT-4/GPT-4o"; \
		echo "    $(GREEN)anthropic$(RESET) - Anthropic Claude"; \
		echo "    $(GREEN)zai$(RESET)       - Z.AI GLM-5/GLM-4.6V"; \
		echo "    $(GREEN)kimi$(RESET)      - Kimi K2/Kimi Code"; \
		echo "    $(GREEN)minimax$(RESET)   - MiniMax-M2.5"; \
		echo "    $(GREEN)ollama$(RESET)    - Modelos locales"; \
		echo ""; \
		python3 scripts/switch_provider.py; \
	else \
		echo "$(BLUE)🔧 Cambiando a proveedor: $(USE)$(RESET)"; \
		python3 scripts/switch_provider.py $(USE); \
		echo ""; \
		echo "$(YELLOW)🔄 Para aplicar cambios, ejecuta:$(RESET)"; \
		echo "   make down && make up"; \
	fi

# Alias para compatibilidad hacia atrás
provider-openai: ## [Alias] Cambia a OpenAI
	@$(MAKE) provider USE=openai

provider-zai: ## [Alias] Cambia a Z.AI (GLM)
	@$(MAKE) provider USE=zai

provider-kimi: ## [Alias] Cambia a Kimi
	@$(MAKE) provider USE=kimi

provider-minimax: ## [Alias] Cambia a MiniMax
	@$(MAKE) provider USE=minimax

provider-ollama: ## [Alias] Cambia a Ollama (local)
	@$(MAKE) provider USE=ollama

# ═══════════════════════════════════════════════════════════════
# COMANDOS CLI
# ═══════════════════════════════════════════════════════════════

install-cli: ## Instala la CLI 'trus' en el sistema
	@echo "$(BLUE)📦 Instalando TrustGraph CLI...$(RESET)"
	@./install/install-cli.sh

uninstall-cli: ## Desinstala la CLI 'trus'
	@echo "$(BLUE)🗑️  Desinstalando TrustGraph CLI...$(RESET)"
	@./install/uninstall-cli.sh

setup-master: ## Ejecuta el menú maestro de setup
	@echo "$(BLUE)🧙‍♂️ Iniciando menú maestro...$(RESET)"
	@./install/setup-master.sh

# ═══════════════════════════════════════════════════════════════
# COMANDOS WRAPPER PARA CLI (si está instalada)
# ═══════════════════════════════════════════════════════════════

recordar: ## Guarda archivos en TrustGraph (usar: make recordar RUTA=archivo.txt)
	@if [ -z "$(RUTA)" ]; then \
		echo "$(RED)❌ Usa: make recordar RUTA='archivo.txt'$(RESET)"; \
		echo "$(CYAN)   O: make recordar RUTA='directorio/'$(RESET)"; \
	else \
		trus recordar archivo "$(RUTA)" 2>/dev/null || python3 scripts/load_docs.py "$(RUTA)"; \
	fi

ask: ## Consulta TrustGraph (usar: make ask Q="tu pregunta")
	@if [ -z "$(Q)" ]; then \
		echo "$(RED)❌ Usa: make ask Q='tu pregunta'$(RESET)"; \
	else \
		trus query "$(Q)" 2>/dev/null || python3 scripts/query_graphrag.py "$(Q)"; \
	fi
