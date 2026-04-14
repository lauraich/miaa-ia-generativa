# Fase 3 — Ingeniería de Prompts: Código

## Estructura

```
taller1/                 # raíz del taller (pyproject, uv, Makefile)
├── Makefile             # atajos: demo, interactivo, comparaciones A/B
├── main.py
└── fase3/
    ├── database.py      # Base de datos simulada de pedidos + política de devoluciones
    ├── prompts.py       # Prompts, demo, comparación básico vs mejorado, modo interactivo
    └── README.md        # Este archivo
```

## Requisitos

### Entorno Python (recomendado)

Desde la carpeta `taller1` del repositorio:

```bash
uv sync
# o: pip install -r requirements.txt
```

### Opción A — Modelo open-source (recomendado para el taller)

```bash
# 1. Instalar Ollama
# macOS / Linux:
curl -fsSL https://ollama.com/install.sh | sh
# Windows: descargar desde https://ollama.com

# 2. Descargar el modelo usado por el código (Ollama)
ollama pull llama3:8b

# 3. Dependencia Python (si no usas solo uv sync)
pip install ollama
```

Por defecto, `prompts.py` usa **Ollama** con el modelo `llama3:8b` (ver variable `MODEL` en el código).

### Opción B — OpenAI (requiere API key de pago)

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
# En prompts.py: cambiar USAR_OPENAI = True
```

## Ejecución

Los comandos siguientes asumen que estás en la carpeta `taller1` (un nivel **arriba** de `fase3`), salvo que indiques `cd fase3` y llames a `python prompts.py` directamente.

### Con Python / uv

```bash
cd taller1

# Demo completa (ejercicios 1 y 2 + comparaciones A/B integradas en el flujo)
uv run python fase3/prompts.py
# o, desde fase3:
cd fase3 && python prompts.py
```

**Modo comparación (CLI)**

```bash
uv run python fase3/prompts.py --comparar ECO-003          # un pedido: básico vs mejorado
uv run python fase3/prompts.py --comparar-notable          # ECO-003 y ECO-999 + criterios
uv run python fase3/prompts.py --comparar-devolucion       # ejemplo fijo (Shampoo / ECO-007)
```

**Modo interactivo** (menú con opciones 1–4; escribe `salir` para terminar)

```bash
uv run python fase3/prompts.py --interactivo
```

- **1** — Estado de pedido (prompt mejorado)  
- **2** — Devolución (prompt mejorado)  
- **3** — Comparar básico vs mejorado para un pedido que indiques  
- **4** — Comparar básico vs mejorado para una devolución que indiques  

### Con Makefile (en `taller1/`)

Requiere **GNU Make** (por ejemplo Git Bash en Windows) y **uv** en el `PATH`. En PowerShell sin `make`, usa los mismos comandos que en la sección anterior.

```bash
cd taller1

make install          # uv sync
make demo             # demo completa
make interactivo      # menú interactivo
make comparar         # por defecto PEDIDO=ECO-003
make comparar PEDIDO=ECO-005
make comparar-notable
make comparar-devolucion
make main             # ejecuta main.py en la raíz del taller
make help             # lista objetivos y variables
```

#### ¿Para qué sirve cada modo del Makefile?

- `make help`: muestra todos los objetivos disponibles y variables útiles (`UV`, `PEDIDO`).
- `make install` / `make sync`: prepara el entorno e instala dependencias con `uv sync`.
- `make demo`: corre la demostración completa de `fase3/prompts.py` (casos de pedido y devolución, con comparaciones A/B incluidas en la demo).
- `make interactivo`: abre el menú interactivo para probar consultas manuales.
- `make comparar`: compara prompt básico vs mejorado para un pedido puntual (usa `PEDIDO`, por defecto `ECO-003`).
- `make comparar-notable`: ejecuta comparación en casos “notables” (`ECO-003` y `ECO-999`).
- `make comparar-devolucion`: compara básico vs mejorado en un caso fijo de devolución (shampoo usado, `ECO-007`).
- `make main`: ejecuta `main.py` de la raíz del taller (útil para validar que el proyecto base corre).

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

### Comparación “básico vs mejorado”

Además del prompt mejorado con contexto y reglas, el código incluye un **prompt mínimo** (`SYSTEM_PROMPT_PEDIDO_BASICO` / equivalente en devoluciones) para contrastar tono, uso del contexto y cumplimiento de políticas frente a la versión completa.

### Elementos clave del system prompt

1. **Rol explícito** — "Eres un agente de servicio al cliente amable..." establece el tono y la persona.
2. **Instrucción de no inventar** — "usa ÚNICAMENTE la información que se te proporciona" previene alucinaciones.
3. **Reglas condicionales claras** — Se distinguen explícitamente los casos (entregado / retrasado / cancelado) para que el modelo no generalice incorrectamente.
4. **Restricción de longitud** — "máximo 5 oraciones" evita respuestas excesivamente largas en un contexto de chat.
5. **Fallback honesto** — Se instruye al modelo a admitir cuando no tiene la información en lugar de inventarla.
