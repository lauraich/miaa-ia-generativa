# Taller Práctico #1 — EcoMarket: Optimización de Atención al Cliente con IA Generativa
---

## Fase 1: Selección y Justificación del Modelo de IA

### Modelo propuesto: Arquitectura híbrida RAG + LLM

Se propone una **arquitectura en tres capas**:

1. **Clasificador de intención** : Un LLM ligero cómo GPT-5-nano que clasifica cada consulta entrante en una de dos rutas: automatizable (80%) o requiere humano (20%). Esta clasificación es rápida, económica y suficiente para un problema de enrutamiento binario.

2. **Módulo RAG**: para las consultas se propone utilizar un modelo pequeño de cualquier proveedor cómo GPT-5.4-mini o Gemini 3 Flash. El modelo tendría dos formas de obtener información: a través de una tool recuperar información en tiempo real de la base de datos de EcoMarket con el fin de verificar información sobre el estado de un pedido y hacer una busqueda RAG para obtener información sobre  políticas de devolución o catálogo de productos (documentos de la empresa). Esto elimina las alucinaciones sobre datos transaccionales.

3. **Interfaz de asistencia al agente humano**: Para el 20% complejo, el mismo LLM genera un borrador de respuesta sugerido que el agente humano puede editar, reduciendo su carga cognitiva sin eliminar el toque humano.

### ¿Por qué este modelo y no otro?

| Criterio | Fine-tuned LLM dedicado | RAG + GPT-5.4 completo | **RAG + modelo pequeño (propuesta)** |
|---|---|---|---|
| **Precio** | Alto (entrenamiento) | Alto (por token) | Bajo — modelo pequeño + contexto dinámico |
| **Escalabilidad** | Requiere re-entrenamiento ante cambios | Alta | **Alta** — la BD se actualiza sin reentrenar |
| **Precisión en datos transaccionales** | Alta — datos actualizados via tool call |Alta — datos actualizados via tool call + RAG | Alta — datos actualizados via tool call + RAG |
| **Facilidad de integración** | Media | Alta — API estándar | Alta — API estándar (OpenAI / Google / Ollama) |
| **Calidad de respuesta** | Alta en dominio específico | Muy alta | Alta |

#### Precio

Un modelo fine-tuned requiere GPU costosa para el entrenamiento y re-entrenamiento cada vez que cambian productos o políticas. GPT-5.4 completo, a $2.50/1M tokens de entrada y $15/1M de salida, supera los $3,000 USD mensuales a 5,000 consultas diarias con prompts típicos de aprox. 800 tokens. La propuesta RAG con un modelo pequeño como GPT-5.4-mini (aprox. $0.00128/consulta) o Gemini 3 Flash (~$0.00085/consulta) reduce ese gasto a entre $130 y $192 USD mensuales, es decir, más de 15 veces más barato que usar el modelo completo.

#### Escalabilidad

Con un modelo fine-tuned, cada vez que EcoMarket lanza un producto nuevo, cambia una política o ajusta precios, el modelo debe re-entrenarse. En un e-commerce de crecimiento rápido esto puede ocurrir semanalmente, convirtiendo el mantenimiento en un cuello de botella operativo. GPT-5.4 completo escala bien en volumen, pero su costo por token hace que crecer sea financieramente insostenible. Con RAG, la base de datos y los documentos indexados se actualizan de forma completamente independiente al modelo: EcoMarket puede agregar 100 productos nuevos al catálogo sin modificar el LLM, solo actualizando los documentos de recuperación.

#### Precisión en datos transaccionales

La propuesta elimina este riesgo de forma estructural: mediante tool calling, el sistema consulta la base de datos en el momento exacto de cada solicitud, reduciendo significativamente la probabilidad de generar una respuesta incorrecta. Cabe resaltar que el uso de modelos de mayor tamaño aporta una mejor capacidad de comprensión del contexto, lo que les permite interpretar con mayor precisión las instrucciones, reforzando la calidad y fiabilidad de las respuestas.

#### Facilidad de integración

Ambos enfoques se integran mediante APIs; sin embargo, la complejidad del modelo fine-tuned no radica en su consumo, sino en su preparación. Requiere la construcción de pipelines de datos, procesos de entrenamiento y múltiples configuraciones previas, lo que implica mayor esfuerzo técnico y tiempos de implementación más largos. En contraste, modelos como GPT-5.4 y GPT-5.4-mini pueden consumirse directamente vía API, sin necesidad de ese proceso previo, facilitando una adopción mucho más rápida.

La propuesta se basa en una API estándar, independiente del proveedor, y en componentes modulares: clasificador, tool calling y RAG, que agilizan su implementación.

#### Calidad de respuesta

El modelo fine-tuned ofrece alta calidad únicamente para los patrones vistos durante el entrenamiento; ante una consulta inusual la respuesta puede ser incorrecta sin que el modelo lo señale. GPT-5.4 completo ofrece la calidad más alta del mercado, pero es un uso de recursos desproporcionado para responder preguntas como "¿dónde está mi pedido ECO-003?" — equivalente a contratar un experto senior para contestar FAQs. Para el 80% de consultas repetitivas de EcoMarket (pedidos, devoluciones, catálogo), un modelo pequeño con contexto RAG inyectado produce respuestas similares a las de un modelo grande.

### Justificación central:

El problema de EcoMarket no radica en la comprensión avanzada del lenguaje natural, sino en la precisión de los datos transaccionales y la velocidad de respuesta. Un modelo fine-tuned implicaría altos costos de mantenimiento ante cambios en preguntas frecuentes, en el catálogo o en las políticas.

La arquitectura propuesta aborda este reto de forma eficiente: el LLM aporta la fluidez lingüística, el tool calling permite recuperar datos transaccionales en tiempo real (como el estado de los pedidos) y el enfoque RAG facilita el acceso a información actualizada sobre políticas, catálogo u otros documentos de la empresa.

En este contexto, modelos como GPT-5.4-mini o Gemini 3 Flash ofrecen un balance óptimo entre costo y calidad para gestionar este tipo de respuestas estructuradas.

### Comparación de modelos candidatos

| Criterio | GPT-5.4-mini | Gemini 3 Flash |
|---|---|---|
| **Precio input** | $0.75 / 1M tokens | $0.50 / 1M tokens |
| **Precio output** | $4.50 / 1M tokens | $3.00 / 1M tokens |
| **Costo estimado por consulta** (~500 tokens input, ~200 output) | ~$0.00128 | ~$0.00085 |
| **Capa gratuita** | No | Sí (Google AI Studio) |
| **Ventana de contexto** | 400K tokens | 1M tokens |
| **Velocidad** | Alta | Alta |
| **Ecosistema de integración** | Bueno (OpenAI SDK) | Bueno (Google AI SDK) |
| **Rendimiento en español** | Muy bueno | Muy bueno |

**Elección para este taller:** Se usa **Llama 3.1 8B via Ollama** (open-source, sin costo) para la Fase 3, lo que permite demostrar la arquitectura de prompts sin depender de APIs de pago. Cabe resaltar que en un entorno de producción real, se recomendaría **Gemini 3 Flash** por su relación precio/calidad y su capa gratuita para desarrollo.

---
## Fase 2: Fortalezas, Limitaciones y Riesgos Éticos

### 1. Fortalezas

#### Disponibilidad, escalabilidad y operación continua
El sistema ofrece disponibilidad 24/7 sin costo incremental, ya que no requiere turnos ni descansos, lo que le permite operar de manera continua. Además, tiene la capacidad de atender picos de demanda como son eventos tipo Black Friday o día sin IVA sin necesidad de ampliar el equipo humano. Esto se complementa con una arquitectura modular y escalable que permite aumentar la capacidad por componentes específicos, optimizando tanto los costos como el rendimiento del sistema.

#### Eficiencia operativa y tiempos de respuesta
La implementación permite una reducción drástica del tiempo de respuesta, pasando de aproximadamente 24 horas a solo segundos o minutos en el 80% de las consultas automatizables. Esto genera un impacto directo en la satisfacción del cliente, al ofrecer respuestas más rápidas y oportunas, y al mismo tiempo reduce significativamente la carga operativa de los agentes humanos, permitiéndoles enfocarse en casos de mayor complejidad.

También se debe considerar que se dispone de monitoreo inmediato ante volúmenes de consultas, tiempos de respuesta, tasas de resolución automática, entre otras, lo que facilita tomar decisiones operativas rápidas.

#### Precisión y confiabilidad en información
El uso de una arquitectura hibrida propuesta permite recuperar datos directamente desde las fuentes propias de la compañía, como pedidos, entregas y devoluciones, evitando depender únicamente del conocimiento preentrenado del modelo. Esto no solo mejora la precisión de las respuestas, sino que también facilita la trazabilidad y garantiza la actualidad de la información transaccional utilizada en cada interacción.

#### Consistencia y estandarización del servicio
El sistema garantiza respuestas homogéneas en cuanto a la forma en que se atiende a los usuarios, alineándose con las políticas definidas por la organización. Esto elimina la variabilidad propia de los agentes humanos y contribuye a una mejora consistente en la calidad percibida del servicio.

Además puede integrarse en múltiples canales como Chat web, WhatsApp, email y redes sociales. Manteniendo consistencia en todos los canales de atención.

#### Eficiencia del agente humano
En el 20% de los casos más complejos, el sistema genera borradores de respuesta que pueden ser editados por los agentes humanos, lo que reduce su carga cognitiva y les permite enfocarse en tareas de mayor valor como la empatía, la negociación y la resolución de problemas. La solución propuesta potencia las capacidades del agente humano en lugar de sustituirlo.

#### Mejora continua
El sistema permite identificar patrones de consulta, detectar productos con alta tasa de devolución y reconocer fallas logísticas o de catálogo, convirtiéndose en una base sólida para la analítica y la optimización continua del negocio.

### 2. Limitaciones

#### Complejidad humana
El modelo no puede reemplazar la empatía humana, lo que limita su efectividad en la atención de quejas emocionales, clientes frustrados o situaciones ambiguas y sensibles. En estos casos, existe el riesgo de que las respuestas sean percibidas como mecánicas si no hay una intervención humana adecuada que aporte comprensión y adaptación al contexto. 

#### Costo inicial
La implementación de una arquitectura que integra RAG, LLM y sistemas internos conlleva un costo inicial elevado y una alta complejidad técnica. Este proceso requiere una inversión en infraestructura y desarrollo, así como la participación de talento especializado lo que puede representar una barrera importante para su adopción.

#### Dependencia de la calidad de los datos
El sistema depende completamente de la calidad de los datos siguiendo el principio de garbage in, garbage out. Problemas como estados de pedidos incorrectos o políticas desactualizadas no solo afectan las respuestas, sino que el modelo no está en capacidad de corregirlos, lo que puede generar desinformación y afectar la experiencia del cliente.

#### Limitaciones técnicas del modelo y la arquitectura
Los LLMs presentan una ventana de contexto finita, lo que dificulta el manejo de historiales extensos de interacción. Además, existen desafíos de latencia, especialmente en consultas complejas con arquitectura RAG, donde las respuestas  pueden tomar más tiempo, y aumentar aún más en flujos híbridos que involucran clasificador, generación y revisión humana. A esto se suma la dificultad para procesar consultas ambiguas o de múltiples intenciones, como serían solicitudes que combinan devolución y estado del pedido, lo que puede derivar en respuestas incompletas o incorrectamente enroutadas.

#### Lenguaje, contexto cultural y entrada del usuario
El sistema presenta sensibilidad a modismos regionales y al uso de español coloquial o con errores ortográficos, lo que puede afectar la correcta interpretación de las consultas. Como resultado, existe el riesgo de generar respuestas que, aunque técnicamente correctas, resulten culturalmente inadecuadas o fuera de contexto para el usuario.


### 3. Riesgos Éticos

#### Alucinaciones y confiabilidad
Existe el riesgo de generación de información incorrecta, como fechas de entrega, estados de pedidos o políticas inexistentes, lo cual puede ocurrir incluso en sistemas con RAG si el proceso de recuperación falla, la información es ambigua o incompleta, o la consulta está fuera del dominio del modelo. Para mitigar este riesgo, se proponen medidas como la implementación de un mecanismo explícito de “no sé”, el escalamiento automático a un agente humano cuando la confianza sea baja y la validación obligatoria de que toda respuesta transaccional esté respaldada por una fuente previamente recuperada.


#### Sesgo algorítmico
Existen posibles diferencias en el trato al cliente según el nivel de formalidad, el vocabulario utilizado o el perfil implícito del usuario, lo que puede derivar en experiencias desiguales. Para mitigar este riesgo, se plantean auditorías periódicas de las respuestas segmentadas por demografía o perfil, la evaluación de las tasas de escalamiento entre distintos segmentos y la inclusión de instrucciones explícitas en el prompt que garanticen un trato igualitario independientemente de las características del cliente.


#### Privacidad y protección de datos
El sistema implica el uso de datos sensibles como nombre, dirección, historial de compras y métodos de pago, lo que introduce riesgos especialmente cuando se emplean APIs externas que procesan la información en infraestructura de terceros. Este escenario debe evaluarse bajo marcos regulatorios. Para mitigar estos riesgos, se proponen estrategias como el uso de modelos on-premise o self-hosted, la pseudonimización o anonimización de datos, la revisión de las políticas de retención de datos de los proveedores y la obtención de consentimiento explícito por parte del cliente.

Además existe el riesgo de uso indebido del sistema por parte de usuarios, quienes pueden intentar manipular el modelo para acceder a información no autorizada. Para mitigar este tipo de amenazas, se recomienda implementar una validación estricta de los inputs, establecer controles robustos de acceso a los datos y aplicar procesos de sanitización de prompts que reduzcan la exposición a instrucciones maliciosas.

#### Impacto laboral
La implementación del sistema conlleva un riesgo de desplazamiento o incertidumbre laboral, lo que puede impactar negativamente en la motivación de los agentes humanos. Frente a esto, se propone una postura donde las tareas repetitivas se automatizan y el talento humano se enfoca en generar valor. Para gestionar este cambio de manera efectiva, se recomiendan buenas prácticas como una comunicación transparente desde el inicio, la capacitación en el uso de nuevas herramientas y la definición de métricas de éxito orientadas a la satisfacción del agente humano y la calidad de resolución, en lugar de la reducción de personal.

Se debe tener en cuenta que reducir la supervisión humana a medida que aumenta la automatización, puede derivar en errores no detectados y un deterioro progresivo de la calidad del servicio. Para mitigar este problema, se recomienda mantener un enfoque de human-in-the-loop en casos críticos y realizar revisiones periódicas de calidad.

#### Transparencia hacia el cliente
Existe el riesgo de que el cliente no tenga claridad sobre si está interactuando con un sistema automatizado o con un agente humano, lo cual puede considerarse una práctica engañosa en ciertos contextos. Para mitigar este problema, se recomienda identificar de forma explícita al asistente virtual desde el inicio de la interacción y ofrecer la opción de escalar la conversación a un agente humano en caso de ser necesario.

#### Riesgo reputacional
Un error como una respuesta incorrecta o inapropiada puede escalar rápidamente en redes sociales y generar un impacto desproporcionado frente al volumen total de aciertos del sistema, afectando la reputación de la marca. Para mitigar este riesgo, se recomienda implementar filtros de seguridad que prevengan respuestas sensibles y establecer un monitoreo en tiempo real de las interacciones críticas para detectar y corregir incidentes de forma oportuna.