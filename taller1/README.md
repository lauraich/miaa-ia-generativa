# Taller Práctico #1 — EcoMarket: Optimización de Atención al Cliente con IA Generativa
---

## Fase 1: Selección y Justificación del Modelo de IA

### Modelo propuesto: Arquitectura híbrida RAG + LLM

Se propone una **arquitectura en tres capas**:

1. **Clasificador de intención** — Un LLM ligero (GPT-5-nano o un modelo fine-tuned pequeño como `distilbert-base`) que clasifica cada consulta entrante en una de dos rutas: *automatizable* (80%) o *requiere humano* (20%). Esta clasificación es rápida, económica y suficiente para un problema de enrutamiento binario.

2. **Módulo RAG** para las consultas se propone utilizar un modelo pequeño de cualquier proveedor cómo GPT-5.4-mini o Gemini 3 Flash. El modelo tendría tendría dos formas de obtener información: a través de una tool puede recuperar información en tiempo real de la base de datos de EcoMarket con el fin de verificar información sobre el estado de un pedido y puede hacer una busqueda RAG para obtener información sobre  políticas de devolución o catálogo de productos (documentos de la empresa). Esto elimina las alucinaciones sobre datos transaccionales.

3. **Interfaz de asistencia al agente humano** — Para el 20% complejo, el mismo LLM genera un *borrador de respuesta* sugerido que el agente humano puede editar, reduciendo su carga cognitiva sin eliminar el toque humano.

### ¿Por qué este modelo y no otro?

| Criterio | Fine-tuned LLM dedicado | GPT-5.4 completo | **RAG + modelo pequeño (propuesta)** |
|---|---|---|---|
| **Costo** | Alto (entrenamiento) | Alto (por token) | **Bajo** — modelo pequeño + contexto dinámico |
| **Escalabilidad** | Requiere re-entrenamiento ante cambios | Alta | **Alta** — la BD se actualiza sin reentrenar |
| **Precisión en datos transaccionales** | Media (depende del fine-tuning) | Media (puede alucinar) | **Alta** — datos frescos via tool call + RAG |
| **Facilidad de integración** | Compleja | Moderada | **Alta** — API estándar (OpenAI / Google / Ollama) |
| **Calidad de respuesta** | Alta en dominio específico | Muy alta | **Alta** para el 80% repetitivo |

**Justificación central:** El problema de EcoMarket no es un problema de comprensión del lenguaje natural avanzada, sino de precisión en datos transaccionales y velocidad. Un modelo fine-tuned sería costoso de mantener cada vez que cambia el catálogo o las políticas. La arquitectura propuesta resuelve esto: el LLM aporta la fluidez lingüística, la **tool call** recupera datos transaccionales en tiempo real (estado de pedidos), y la búsqueda RAG aporta la información sobre políticas y catálogo, o cualquier documento de la empresa. Modelos como GPT-5.4-mini o Gemini 3 Flash ofrecen el balance óptimo entre costo y calidad para este tipo de respuestas estructuradas.

### Comparación de modelos candidatos

| Criterio | GPT-5.4-mini | Gemini 3 Flash |
|---|---|---|
| **Precio input** | $0.75 / 1M tokens | $0.50 / 1M tokens |
| **Precio output** | $4.50 / 1M tokens | $3.00 / 1M tokens |
| **Costo estimado por consulta** (~500 tokens input, ~200 output) | ~$0.00128 | ~$0.00085 |
| **Capa gratuita** | No | Sí (Google AI Studio) |
| **Ventana de contexto** | 400K tokens | 1M tokens |
| **Velocidad** | Alta | Muy alta (3× más rápido que modelos Pro) |
| **Ecosistema de integración** | Muy maduro (OpenAI SDK) | Bueno (Google AI SDK) |
| **Rendimiento en español** | Muy bueno | Muy bueno |
| **Veredicto** | Sólido si ya se usa infraestructura OpenAI | **Mejor precio/calidad** para proyecto nuevo |

> **Elección para este taller:** Se usa **Llama 3.1 8B via Ollama** (open-source, sin costo) para la Fase 3, lo que permite demostrar la arquitectura de prompts sin depender de APIs de pago. En un entorno de producción real, se recomendaría **Gemini 3 Flash** por su relación precio/calidad y su capa gratuita para desarrollo.

---

## Fase 2: Fortalezas, Limitaciones y Riesgos Éticos

### Fortalezas

- **Disponibilidad 24/7 sin costo incremental** — El sistema no duerme, no toma descansos y escala automáticamente ante picos de demanda (ej. Black Friday), algo imposible con un equipo humano fijo.
- **Reducción drástica del tiempo de respuesta** — De 24 horas a un estimado de 1-2 minutos para el 80% de las consultas repetitivas, impactando directamente la satisfacción del cliente (CSAT).
- **Consistencia en las respuestas** — A diferencia de los agentes humanos, el modelo aplica las mismas políticas de devolución y el mismo tono de marca en cada interacción, eliminando la variabilidad.
- **Descarga cognitiva para agentes humanos** — El 20% complejo recibe un borrador generado por IA, permitiendo al agente enfocarse en la empatía y la resolución creativa en lugar de redactar desde cero.
- **Trazabilidad y mejora continua** — Cada interacción queda registrada, permitiendo analizar los patrones de consulta, detectar productos con alta tasa de devolución, o identificar problemas logísticos sistémicos.

### Limitaciones

- **El 20% complejo es una barrera real** — El modelo no puede reemplazar la empatía genuina en quejas emocionales, situaciones ambiguas o clientes en estado de frustración intensa. Forzar IA en esos casos puede escalar el conflicto.
- **Dependencia de la calidad de la base de datos** — Si la información de pedidos o el catálogo tiene errores, el modelo los amplifica y los presenta con confianza aparente. El principio *"garbage in, garbage out"* aplica directamente.
- **Límite del contexto del modelo** — Los LLMs tienen una ventana de contexto finita. Si un cliente tiene un historial de 50 interacciones previas, no todo puede inyectarse como contexto RAG, lo que puede llevar a respuestas que ignoran el historial.
- **Multilingüismo y modismos regionales** — EcoMarket puede tener clientes en distintas regiones con variantes del español o inglés. El modelo puede responder de forma técnicamente correcta pero culturalmente distante.
- **Latencia en consultas complejas** — La pipeline RAG (buscar en BD → construir prompt → generar respuesta) puede tardar 3-8 segundos en casos con mucho contexto, lo cual puede sentirse lento en un chat en vivo.

### Riesgos Éticos

#### 1. Alucinaciones
El riesgo más inmediato. Un LLM sin RAG puede inventar fechas de entrega, números de seguimiento o políticas de devolución inexistentes. La arquitectura RAG mitiga esto para datos transaccionales, pero persiste el riesgo en preguntas fuera del dominio ("¿este producto contiene tal componente químico?") donde el modelo podría inferir en lugar de admitir ignorancia.

**Mitigación propuesta:** Implementar un mecanismo de *"no sé"* explícito: si la confianza del retrieval es baja, el sistema debe escalar al agente humano en lugar de generar una respuesta especulativa.

#### 2. Sesgo algorítmico
Si el modelo fue pre-entrenado con datos sesgados (lo cual es inherente a todos los LLMs de gran escala), podría ofrecer respuestas más elaboradas o empáticas a ciertos perfiles de clientes. Por ejemplo, podría interpretar diferente un mismo mensaje dependiendo del nombre del remitente o del vocabulario utilizado.

**Mitigación propuesta:** Auditorías periódicas de respuestas segmentadas por demografía de clientes. Evaluar si la tasa de escalación humana es uniforme entre segmentos.

#### 3. Privacidad de datos
Este es el riesgo más grave desde el punto de vista regulatorio (GDPR, Ley 1581 en Colombia). Para que RAG funcione, el sistema necesita acceder a datos personales del cliente (nombre, dirección, historial de compras) e inyectarlos en el prompt. Si se usa una API externa (OpenAI), estos datos podrían ser procesados en servidores de terceros.

**Mitigación propuesta:**
- Usar modelos *on-premise* u *open-source* (Llama 3.1 en servidores propios) para no exfiltrar datos a terceros.
- Implementar pseudonimización: inyectar solo el ID de pedido en el prompt, no el nombre completo ni la dirección.
- Obtener consentimiento explícito del cliente para el procesamiento automatizado de su consulta.

#### 4. Impacto laboral
Este es el riesgo ético más humano y frecuentemente ignorado. EcoMarket tiene agentes de atención al cliente cuyo trabajo podría verse amenazado por esta implementación.

**Postura recomendada — "aumentación, no reemplazo":** El objetivo explícito del sistema debe ser liberar a los agentes de las tareas repetitivas para que puedan especializarse en resolución de conflictos, mejora del producto y construcción de relaciones con clientes VIP. La métrica de éxito no debería ser "número de agentes reducidos", sino "satisfacción del agente" y "calidad de resolución del 20% complejo". Cualquier reducción de personal debería hacerse de forma transparente, con reentrenamiento y tiempo suficiente.

---

*Para la implementación práctica de prompts, ver la carpeta [`/fase3`](./fase3/).*
