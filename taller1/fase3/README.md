# Fase 3 — Ingeniería de Prompts: Código

## Estructura

```
fase3/
├── database.py      # Base de datos simulada de pedidos + política de devoluciones
├── prompts.py       # Prompts y lógica principal
└── README.md        # Este archivo
```

## Requisitos

### Opción A — Modelo open-source (recomendado para el taller)

```bash
# 1. Instalar Ollama
# macOS / Linux:
curl -fsSL https://ollama.com/install.sh | sh
# Windows: descargar desde https://ollama.com

# 2. Descargar el modelo Llama 3.1 (4.7 GB)
ollama pull llama3.1

# 3. Instalar dependencia Python
pip install ollama
```

### Opción B — OpenAI (requiere API key de pago)

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
# En prompts.py: cambiar USAR_OPENAI = True
```

## Ejecución

```bash
cd fase3

# Modo demo automático (ejecuta todos los casos de prueba)
python prompts.py

# Modo interactivo (el usuario escribe sus propias consultas)
python prompts.py --interactivo
```

## Casos de prueba incluidos

### Ejercicio 1 — Estado de pedido

| Número | Situación |
|--------|-----------|
| ECO-002 | Pedido en camino — respuesta normal |
| ECO-003 | Pedido retrasado — incluye disculpa y motivo |
| ECO-005 | Pedido entregado — cierre positivo |
| ECO-008 | Pedido cancelado — informa estado del reembolso |
| ECO-999 | Número inexistente — manejo elegante del error |

### Ejercicio 2 — Proceso de devolución

| Producto | Resultado esperado |
|----------|-------------------|
| Termo de acero (con defecto) | Guía completa de devolución |
| Shampoo sólido (abierto y usado) | Explica con empatía que no es posible |
| Vela aromática (sin abrir) | Guía completa de devolución |
| Semillas orgánicas (no germinaron) | Caso límite — empático pero honesto |

## Decisiones de diseño de prompts

### ¿Por qué RAG y no fine-tuning?

Los datos de pedidos cambian constantemente. Con RAG, el modelo siempre accede a información actualizada sin necesidad de reentrenamiento. El `system_prompt` define el *comportamiento*, y el contexto inyectado proporciona los *hechos*.

### Elementos clave del system prompt

1. **Rol explícito** — "Eres un agente de servicio al cliente amable..." establece el tono y la persona.
2. **Instrucción de no inventar** — "usa ÚNICAMENTE la información que se te proporciona" previene alucinaciones.
3. **Reglas condicionales claras** — Se distinguen explícitamente los casos (entregado / retrasado / cancelado) para que el modelo no generalice incorrectamente.
4. **Restricción de longitud** — "máximo 5 oraciones" evita respuestas excesivamente largas en un contexto de chat.
5. **Fallback honesto** — Se instruye al modelo a admitir cuando no tiene la información en lugar de inventarla.
