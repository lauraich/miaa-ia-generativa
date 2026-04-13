# Taller Práctico #1 — EcoMarket (taller1)
# Requiere: GNU Make (p. ej. Git Bash) y uv en PATH.
# En Windows PowerShell sin `make`, puedes usar los mismos comandos que las recetas.

UV ?= uv
FASE3 := fase3
PYTHON := $(UV) run python
# Pedido de ejemplo para la comparación A/B (override: make comparar PEDIDO=ECO-005)
PEDIDO ?= ECO-003

.DEFAULT_GOAL := help

.PHONY: help install sync demo interactivo comparar comparar-notable comparar-devolucion main

help:
	@echo "Objetivos disponibles:"
	@echo "  make install            - Instalar dependencias (uv sync)"
	@echo "  make demo               - Fase 3: demo completa (prompts.py)"
	@echo "  make interactivo        - Fase 3: menú interactivo"
	@echo "  make comparar           - Comparar prompt básico vs mejorado (pedido); PEDIDO=$(PEDIDO)"
	@echo "  make comparar-notable   - Solo ECO-003 y ECO-999 + criterios de evaluación"
	@echo "  make comparar-devolucion - Comparación fija devolución (Shampoo / ECO-007)"
	@echo "  make main               - Ejecutar main.py de la raíz del proyecto"
	@echo ""
	@echo "Variables útiles: UV=$(UV), PEDIDO=<número> para comparar"

install sync:
	$(UV) sync

demo:
	$(PYTHON) $(FASE3)/prompts.py

interactivo:
	$(PYTHON) $(FASE3)/prompts.py --interactivo

comparar:
	$(PYTHON) $(FASE3)/prompts.py --comparar $(PEDIDO)

comparar-notable:
	$(PYTHON) $(FASE3)/prompts.py --comparar-notable

comparar-devolucion:
	$(PYTHON) $(FASE3)/prompts.py --comparar-devolucion

main:
	$(PYTHON) main.py
