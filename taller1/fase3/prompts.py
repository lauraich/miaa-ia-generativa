"""
Taller Práctico #1 — Fase 3: Ingeniería de Prompts
EcoMarket — Sistema de atención al cliente con IA generativa

Requiere:
    pip install ollama   (y tener corriendo: ollama pull llama3.1)
    o
    pip install openai   (con variable de entorno OPENAI_API_KEY)

Por defecto usa Ollama (open-source, sin costo).

Ejecución:
    python prompts.py                      # demo completa (incluye comparación A/B)
    python prompts.py --comparar ECO-003   # solo comparar pedido básico vs mejorado
    python prompts.py --comparar-notable   # solo ECO-003 y ECO-999 + criterios
    python prompts.py --comparar-devolucion  # ejemplo fijo de comparación devolución
    python prompts.py --interactivo        # menú (opciones 3 y 4 = comparación A/B)
"""

import os

# ─────────────────────────────────────────────
# CONFIGURACIÓN DEL MODELO
# ─────────────────────────────────────────────
USAR_OPENAI = False  # Cambiar a True para usar GPT-4o-mini

if USAR_OPENAI:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    MODEL = "gpt-4o-mini"
else:
    import ollama
    MODEL = "llama3:8b"


def llamar_modelo(system_prompt: str, user_message: str) -> str:
    """Función unificada para llamar al modelo (Ollama u OpenAI)."""
    if USAR_OPENAI:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    else:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            options={"temperature": 0.3},
        )
        return response["message"]["content"]


# ─────────────────────────────────────────────
# IMPORTAR BASE DE DATOS SIMULADA
# ─────────────────────────────────────────────
from database import (
    buscar_pedido,
    formatear_pedido_para_contexto,
    formatear_politica_para_contexto,
)


# ══════════════════════════════════════════════════════════════
# EJERCICIO 1: CONSULTA DE ESTADO DE PEDIDO
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT_PEDIDO_BASICO = (
    "Responde en español"
)

SYSTEM_PROMPT_PEDIDO = """Eres un agente de servicio al cliente amable, empático y profesional de EcoMarket, \
una tienda en línea de productos sostenibles y ecológicos.

Tu tarea es responder consultas sobre el estado de pedidos usando ÚNICAMENTE la información \
que se te proporciona como contexto. No inventes fechas, números de seguimiento ni \
información que no esté explícitamente en el contexto.

Reglas de respuesta:
- Saluda al cliente por su nombre si está disponible.
- Proporciona el estado actual del pedido de forma clara.
- Si hay una fecha estimada de entrega, menciónala.
- Si hay un enlace de seguimiento, compártelo.
- Si el pedido está RETRASADO, ofrece una disculpa sincera y explica brevemente el motivo.
- Si el pedido fue CANCELADO, informa el estado del reembolso.
- Si el pedido fue ENTREGADO, felicita al cliente y pregunta si hay algo más en que puedas ayudar.
- Mantén un tono cálido, alineado con los valores ecológicos de EcoMarket.
- Responde en español, de forma concisa (máximo 5 oraciones).
- Si no encuentras el pedido en el contexto, dilo honestamente y ofrece alternativas de contacto."""


def _contexto_pedido(numero_pedido: str) -> str:
    """Texto de contexto (mismos datos para prompt básico y mejorado)."""
    numero_limpio = numero_pedido.strip()
    pedido = buscar_pedido(numero_limpio)
    if pedido:
        return f"""INFORMACIÓN DEL PEDIDO (usa solo estos datos para responder):
{formatear_pedido_para_contexto(pedido)}"""
    return f"""No se encontró ningún pedido con el número '{numero_limpio}' en el sistema."""


def _prompt_final_con_consulta(contexto: str, mensaje_consulta: str) -> str:
    return f"{contexto}\n\n---\nConsulta del cliente:\n{mensaje_consulta}"


def consultar_pedido_basico(numero_pedido: str) -> str:
    """Misma información de pedido que `consultar_pedido`, con instrucciones mínimas (comparación A/B)."""
    contexto = _contexto_pedido(numero_pedido)
    numero_limpio = numero_pedido.strip()
    mensaje_usuario = f"Dame el estado del pedido {numero_limpio}."
    return llamar_modelo(
        SYSTEM_PROMPT_PEDIDO_BASICO,
        _prompt_final_con_consulta(contexto, mensaje_usuario),
    )


def consultar_pedido(numero_pedido: str) -> str:
    """
    Ejercicio 1: Consulta el estado de un pedido usando RAG + LLM (prompt mejorado).

    Parámetros:
        numero_pedido: El número de pedido (ej: 'ECO-003')

    Retorna:
        La respuesta generada por el modelo.
    """
    contexto = _contexto_pedido(numero_pedido)
    numero_limpio = numero_pedido.strip()
    mensaje_usuario = (
        f"Hola, me gustaría saber el estado de mi pedido número {numero_limpio}."
    )
    return llamar_modelo(
        SYSTEM_PROMPT_PEDIDO,
        _prompt_final_con_consulta(contexto, mensaje_usuario),
    )


def comparar_pedido(numero_pedido: str) -> tuple[str, str]:
    """Devuelve (respuesta_prompt_basico, respuesta_prompt_mejorado) para el mismo pedido."""
    return consultar_pedido_basico(numero_pedido), consultar_pedido(numero_pedido)



# ══════════════════════════════════════════════════════════════
# EJERCICIO 2: PROCESO DE DEVOLUCIÓN
# ══════════════════════════════════════════════════════════════

SYSTEM_PROMPT_DEVOLUCION_BASICO = (
    "Responde en español"
)

SYSTEM_PROMPT_DEVOLUCION = """Eres un agente de servicio al cliente amable, empático y profesional de EcoMarket, \
una tienda en línea de productos sostenibles y ecológicos.

Tu tarea es guiar al cliente en el proceso de devolución de un producto.

INSTRUCCIONES CRÍTICAS:
1. Determina si el producto mencionado es devolvible según la política que se te proporciona.
2. Si el producto ES devolvible: explica el proceso paso a paso de forma clara y alentadora.
3. Si el producto NO es devolvible (por ejemplo: productos de higiene abiertos, perecederos): 
   - Explica con empatía por qué no es posible la devolución.
   - NO inventes excepciones que no existan en la política.
   - Ofrece una alternativa útil si es posible (ej: contactar al equipo de calidad si hay un defecto de fábrica).
4. Usa ÚNICAMENTE la información de la política que se te proporciona.
5. Mantén un tono cálido, comprensivo y alineado con los valores sostenibles de EcoMarket.
6. Responde en español, de forma clara y estructurada.
7. Si no tienes certeza sobre si un producto específico es devolvible, indica que se contacte 
   al equipo de soporte en soporte@ecomarket.co."""


def _contexto_politica_devolucion() -> str:
    return f"""POLÍTICA DE DEVOLUCIONES DE ECOMARKET (usa solo esta información):
{formatear_politica_para_contexto()}"""


def consultar_devolucion_basico(producto: str, motivo: str, numero_pedido: str = None) -> str:
    """Misma política que `consultar_devolucion`, con instrucciones mínimas (comparación A/B)."""
    contexto_politica = _contexto_politica_devolucion()
    partes = [f"¿Puedo devolver {producto}?", f"Motivo: {motivo}."]
    if numero_pedido:
        partes.append(f"Pedido: {numero_pedido}.")
    mensaje_usuario = " ".join(partes)
    prompt_final = f"{contexto_politica}\n\n---\nConsulta del cliente:\n{mensaje_usuario}"
    return llamar_modelo(SYSTEM_PROMPT_DEVOLUCION_BASICO, prompt_final)


def consultar_devolucion(producto: str, motivo: str, numero_pedido: str = None) -> str:
    """
    Ejercicio 2: Guía al cliente en el proceso de devolución usando RAG + LLM (prompt mejorado).

    Parámetros:
        producto: El nombre del producto a devolver.
        motivo: El motivo de la devolución.
        numero_pedido: (opcional) El número de pedido.

    Retorna:
        La respuesta generada por el modelo.
    """
    contexto_politica = _contexto_politica_devolucion()

    partes_consulta = [
        f"Hola, compré '{producto}' y me gustaría solicitar una devolución.",
        f"Motivo: {motivo}.",
    ]
    if numero_pedido:
        partes_consulta.append(f"Mi número de pedido es {numero_pedido}.")

    mensaje_usuario = " ".join(partes_consulta)

    prompt_final = f"{contexto_politica}\n\n---\nConsulta del cliente:\n{mensaje_usuario}"
    return llamar_modelo(SYSTEM_PROMPT_DEVOLUCION, prompt_final)


def comparar_devolucion(producto: str, motivo: str, numero_pedido: str = None) -> tuple[str, str]:
    """Devuelve (respuesta_prompt_basico, respuesta_prompt_mejorado) para la misma consulta."""
    return consultar_devolucion_basico(producto, motivo, numero_pedido), consultar_devolucion(
        producto, motivo, numero_pedido
    )


# ══════════════════════════════════════════════════════════════
# DEMOSTRACIÓN INTERACTIVA
# ══════════════════════════════════════════════════════════════

def separador(titulo: str):
    print("\n" + "═" * 60)
    print(f"  {titulo}")
    print("═" * 60)


def _imprimir_comparacion_pedido(numero: str, descripcion: str):
    separador(f"EJERCICIO 1 — Comparación A/B — {descripcion}")
    print(f"  Número de pedido: {numero}\n")
    basico, mejorado = comparar_pedido(numero)
    print("  --- Salida: prompt básico ---\n")
    print(basico)
    print("\n  --- Salida: prompt mejorado ---\n")
    print(mejorado)


def _imprimir_comparacion_devolucion(producto: str, motivo: str, numero_pedido: str, descripcion: str):
    separador(f"EJERCICIO 2 — Comparación A/B — {descripcion}")
    print(f"  Producto: {producto}")
    print(f"  Motivo: {motivo}\n")
    basico, mejorado = comparar_devolucion(producto, motivo, numero_pedido)
    print("  --- Salida: prompt básico ---\n")
    print(basico)
    print("\n  --- Salida: prompt mejorado ---\n")
    print(mejorado)


def demo_completo():
    """Ejecuta una demostración de los dos ejercicios con casos de prueba variados."""

    print("\n🌿 EcoMarket — Sistema de Atención al Cliente con IA")
    print(f"   Modelo: {MODEL} ({'OpenAI' if USAR_OPENAI else 'Ollama — open-source'})\n")

    # ── Ejercicio 1: comparación prompt básico vs mejorado (mismos datos) ──
    # Casos notables (retraso / inexistente): tras cada A/B se imprimen criterios para evaluar la brecha.

    print(
        "  Comparación A/B en casos notables: ECO-003 (retraso) y ECO-999 (inexistente). "
        "Después de cada par de respuestas se listan criterios para contrastar básico vs mejorado.\n"
    )

    _imprimir_comparacion_pedido("ECO-003", "Pedido retrasado — debe incluir disculpa (A/B)")
    _imprimir_comparacion_pedido("ECO-999", "Número de pedido inexistente (A/B)")

    # ── Ejercicio 1: solo prompt mejorado (evita duplicar llamadas en los A/B anteriores) ──

    casos_pedido_solo_mejorado = [
        ("ECO-002", "Pedido en camino — caso normal"),
        ("ECO-005", "Pedido ya entregado"),
        ("ECO-008", "Pedido cancelado — debe informar reembolso"),
    ]

    for numero, descripcion in casos_pedido_solo_mejorado:
        separador(f"EJERCICIO 1 — {descripcion}")
        print(f"  Número de pedido: {numero}\n")
        print(consultar_pedido(numero))

    # ── Ejercicio 2: una comparación A/B (higiene / no devolvible) ──

    _imprimir_comparacion_devolucion(
        producto="Shampoo sólido sin sulfatos",
        motivo="el olor no me agradó y ya lo usé una vez",
        numero_pedido="ECO-007",
        descripcion="Producto de higiene personal abierto — NO devolvible",
    )

    # ── Ejercicio 2: solo prompt mejorado ──

    casos_devolucion = [
        {
            "producto": "Termo de acero inoxidable 500ml",
            "motivo": "llegó con una abolladura visible y no cierra bien",
            "numero_pedido": "ECO-005",
            "descripcion": "Producto devolvible — defecto físico",
        },
        {
            "producto": "Vela aromática de cera de soya",
            "motivo": "quiero cambiarla por otra fragancia, aún no la he abierto",
            "numero_pedido": "ECO-009",
            "descripcion": "Vela sin usar — devolvible",
        },
        {
            "producto": "Semillas orgánicas para huerta urbana",
            "motivo": "no germinaron correctamente",
            "numero_pedido": "ECO-006",
            "descripcion": "Producto perecedero — caso límite — debe ser empático",
        },
    ]

    for caso in casos_devolucion:
        separador(f"EJERCICIO 2 — {caso['descripcion']}")
        print(f"  Producto: {caso['producto']}")
        print(f"  Motivo: {caso['motivo']}\n")
        print(
            consultar_devolucion(
                producto=caso["producto"],
                motivo=caso["motivo"],
                numero_pedido=caso["numero_pedido"],
            )
        )


# ── Modo interactivo opcional ──

def modo_interactivo():
    """Permite al usuario hacer consultas manuales."""
    print("\n🌿 EcoMarket — Modo interactivo")
    print("   Escribe 'salir' para terminar.\n")

    while True:
        print("\n¿Qué deseas consultar?")
        print("  1. Estado de un pedido (prompt mejorado)")
        print("  2. Proceso de devolución (prompt mejorado)")
        print("  3. Comparar prompt básico vs mejorado — pedido")
        print("  4. Comparar prompt básico vs mejorado — devolución")
        opcion = input("Opción (1/2/3/4): ").strip()

        if opcion == "salir":
            break
        elif opcion == "1":
            numero = input("Número de pedido (ej: ECO-003): ").strip()
            print("\n" + consultar_pedido(numero))
        elif opcion == "2":
            producto = input("Nombre del producto: ").strip()
            motivo = input("Motivo de devolución: ").strip()
            numero = input("Número de pedido (opcional, Enter para omitir): ").strip() or None
            print("\n" + consultar_devolucion(producto, motivo, numero))
        elif opcion == "3":
            numero = input("Número de pedido (ej: ECO-003): ").strip()
            basico, mejorado = comparar_pedido(numero)
            print("\n--- Salida: prompt básico ---\n")
            print(basico)
            print("\n--- Salida: prompt mejorado ---\n")
            print(mejorado)
        elif opcion == "4":
            producto = input("Nombre del producto: ").strip()
            motivo = input("Motivo de devolución: ").strip()
            numero = input("Número de pedido (opcional, Enter para omitir): ").strip() or None
            basico, mejorado = comparar_devolucion(producto, motivo, numero)
            print("\n--- Salida: prompt básico ---\n")
            print(basico)
            print("\n--- Salida: prompt mejorado ---\n")
            print(mejorado)
        else:
            print("Opción no válida.")


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactivo":
        modo_interactivo()
    elif len(sys.argv) > 2 and sys.argv[1] == "--comparar":
        numero = sys.argv[2]
        print("\n🌿 EcoMarket — Comparación prompt básico vs mejorado (pedido)")
        print(f"   Modelo: {MODEL}\n")
        print(f"   Número de pedido: {numero}\n")
        basico, mejorado = comparar_pedido(numero)
        print("--- Salida: prompt básico ---\n")
        print(basico)
        print("\n--- Salida: prompt mejorado ---\n")
        print(mejorado)
    elif len(sys.argv) > 1 and sys.argv[1] == "--comparar-notable":
        print("\n🌿 EcoMarket — Comparación notable (ECO-003 retraso, ECO-999 inexistente)")
        print(f"   Modelo: {MODEL}\n")
        print(
            "   Mismo contexto en ambos prompts; los criterios al final ayudan a ver "
            "dónde suele ampliarse la brecha.\n"
        )
        for num, desc in (
            ("ECO-003", "Pedido retrasado"),
            ("ECO-999", "Pedido inexistente"),
        ):
            _imprimir_comparacion_pedido(num, desc)
    elif len(sys.argv) > 1 and sys.argv[1] == "--comparar-devolucion":
        print("\n🌿 EcoMarket — Comparación prompt básico vs mejorado (devolución)")
        print(f"   Modelo: {MODEL}\n")
        producto = "Shampoo sólido sin sulfatos"
        motivo = "el olor no me agradó y ya lo usé una vez"
        numero = "ECO-007"
        print(f"   Producto: {producto}")
        print(f"   Motivo: {motivo}")
        print(f"   Pedido: {numero}\n")
        basico, mejorado = comparar_devolucion(producto, motivo, numero)
        print("--- Salida: prompt básico ---\n")
        print(basico)
        print("\n--- Salida: prompt mejorado ---\n")
        print(mejorado)
    else:
        demo_completo()
