.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help up down restart logs ps clean test ui

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

up: ## Start Mailpit in the background
	$(COMPOSE) up -d
	@echo "Mailpit UI:  http://localhost:$${MP_UI_PORT:-8025}"
	@echo "SMTP:        localhost:$${MP_SMTP_PORT:-1025}"
	@echo "POP3:        localhost:$${MP_POP3_PORT:-1110}"

down: ## Stop Mailpit (keeps stored mail)
	$(COMPOSE) down

restart: ## Restart Mailpit
	$(COMPOSE) restart

logs: ## Tail Mailpit logs
	$(COMPOSE) logs -f mailpit

ps: ## Show container status
	$(COMPOSE) ps

clean: ## Stop and delete ALL stored mail (removes the volume)
	$(COMPOSE) down -v

test: ## Send a test email to Mailpit
	python3 scripts/send-test-email.py

ui: ## Print the Mailpit UI URL
	@echo "http://localhost:$${MP_UI_PORT:-8025}"
