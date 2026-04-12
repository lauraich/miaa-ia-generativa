# Base de datos simulada de pedidos — EcoMarket
# Este archivo actúa como la "base de datos" que el modelo consulta via RAG

PEDIDOS = [
    {
        "numero": "ECO-001",
        "cliente": "María González",
        "producto": "Kit de limpieza biodegradable",
        "estado": "Entregado",
        "fecha_pedido": "2025-06-01",
        "fecha_entrega": "2025-06-05",
        "transportista": "Servientrega",
        "tracking_url": "https://tracking.servientrega.com/ECO-001",
        "retrasado": False,
    },
    {
        "numero": "ECO-002",
        "cliente": "Carlos Ramírez",
        "producto": "Bolsas reutilizables de tela orgánica (pack x10)",
        "estado": "En camino",
        "fecha_pedido": "2025-06-05",
        "fecha_estimada_entrega": "2025-06-12",
        "transportista": "Deprisa",
        "tracking_url": "https://tracking.deprisa.com/ECO-002",
        "retrasado": False,
    },
    {
        "numero": "ECO-003",
        "cliente": "Ana Martínez",
        "producto": "Cepillo de dientes de bambú (pack x4)",
        "estado": "Retrasado",
        "fecha_pedido": "2025-06-02",
        "fecha_estimada_entrega": "2025-06-15",
        "transportista": "TCC",
        "tracking_url": "https://tracking.tcc.com.co/ECO-003",
        "retrasado": True,
        "motivo_retraso": "Demoras en aduana por inspección de materiales naturales",
    },
    {
        "numero": "ECO-004",
        "cliente": "Luis Herrera",
        "producto": "Jabón artesanal de aceite de coco",
        "estado": "Procesando",
        "fecha_pedido": "2025-06-08",
        "fecha_estimada_entrega": "2025-06-14",
        "transportista": "Envia",
        "tracking_url": "https://tracking.envia.com/ECO-004",
        "retrasado": False,
    },
    {
        "numero": "ECO-005",
        "cliente": "Sofía Torres",
        "producto": "Termo de acero inoxidable 500ml",
        "estado": "Entregado",
        "fecha_pedido": "2025-05-28",
        "fecha_entrega": "2025-06-02",
        "transportista": "Servientrega",
        "tracking_url": "https://tracking.servientrega.com/ECO-005",
        "retrasado": False,
    },
    {
        "numero": "ECO-006",
        "cliente": "Andrés López",
        "producto": "Semillas orgánicas para huerta urbana",
        "estado": "En camino",
        "fecha_pedido": "2025-06-06",
        "fecha_estimada_entrega": "2025-06-13",
        "transportista": "Coordinadora",
        "tracking_url": "https://tracking.coordinadora.com/ECO-006",
        "retrasado": False,
    },
    {
        "numero": "ECO-007",
        "cliente": "Valentina Ruiz",
        "producto": "Shampoo sólido sin sulfatos",
        "estado": "Retrasado",
        "fecha_pedido": "2025-06-01",
        "fecha_estimada_entrega": "2025-06-16",
        "transportista": "Interrapidísimo",
        "tracking_url": "https://tracking.interrapidisimo.com/ECO-007",
        "retrasado": True,
        "motivo_retraso": "Problema logístico en la bodega central de Bogotá",
    },
    {
        "numero": "ECO-008",
        "cliente": "Jorge Moreno",
        "producto": "Esponja vegetal de lufa",
        "estado": "Cancelado",
        "fecha_pedido": "2025-06-03",
        "motivo_cancelacion": "Solicitud del cliente",
        "reembolso_estado": "Procesado — 3-5 días hábiles",
    },
    {
        "numero": "ECO-009",
        "cliente": "Isabella Castro",
        "producto": "Vela aromática de cera de soya",
        "estado": "En camino",
        "fecha_pedido": "2025-06-07",
        "fecha_estimada_entrega": "2025-06-13",
        "transportista": "Servientrega",
        "tracking_url": "https://tracking.servientrega.com/ECO-009",
        "retrasado": False,
    },
    {
        "numero": "ECO-010",
        "cliente": "David Vargas",
        "producto": "Contenedor hermético de vidrio borosilicato",
        "estado": "Procesando",
        "fecha_pedido": "2025-06-09",
        "fecha_estimada_entrega": "2025-06-15",
        "transportista": "TCC",
        "tracking_url": "https://tracking.tcc.com.co/ECO-010",
        "retrasado": False,
    },
]

# Política de devoluciones EcoMarket
POLITICA_DEVOLUCIONES = {
    "plazo_dias": 30,
    "productos_no_devolvibles": [
        "Productos perecederos (alimentos, semillas abiertas)",
        "Productos de higiene personal una vez abiertos (cepillos, esponjas, shampoo sólido)",
        "Productos personalizados",
    ],
    "productos_devolvibles": [
        "Utensilios de cocina (termos, contenedores)",
        "Velas (sin usar)",
        "Bolsas y accesorios textiles (sin lavar)",
        "Kits de limpieza (sin abrir)",
    ],
    "proceso": [
        "1. Contactar soporte en los primeros 30 días tras la entrega",
        "2. Indicar número de pedido y motivo de devolución",
        "3. EcoMarket envía etiqueta de devolución gratis por email",
        "4. Empacar el producto en su caja original o equivalente",
        "5. Dejar el paquete en el punto de recolección indicado",
        "6. Reembolso procesado en 5-7 días hábiles tras recibir el producto",
    ],
}


def buscar_pedido(numero_pedido: str) -> dict | None:
    """Busca un pedido por número y lo retorna, o None si no existe."""
    numero_pedido = numero_pedido.strip().upper()
    for pedido in PEDIDOS:
        if pedido["numero"].upper() == numero_pedido:
            return pedido
    return None


def formatear_pedido_para_contexto(pedido: dict) -> str:
    """Convierte un pedido en texto plano para inyectarlo en el prompt."""
    lineas = [f"Número de pedido: {pedido['numero']}"]
    lineas.append(f"Cliente: {pedido['cliente']}")
    lineas.append(f"Producto: {pedido['producto']}")
    lineas.append(f"Estado actual: {pedido['estado']}")

    if pedido["estado"] == "Entregado":
        lineas.append(f"Fecha de entrega: {pedido.get('fecha_entrega', 'N/A')}")
    elif pedido["estado"] == "Cancelado":
        lineas.append(f"Motivo de cancelación: {pedido.get('motivo_cancelacion', 'N/A')}")
        lineas.append(f"Estado del reembolso: {pedido.get('reembolso_estado', 'N/A')}")
    else:
        lineas.append(f"Fecha estimada de entrega: {pedido.get('fecha_estimada_entrega', 'N/A')}")
        lineas.append(f"Transportista: {pedido.get('transportista', 'N/A')}")
        lineas.append(f"Enlace de seguimiento: {pedido.get('tracking_url', 'N/A')}")
        if pedido.get("retrasado"):
            lineas.append(f"PEDIDO RETRASADO — Motivo: {pedido.get('motivo_retraso', 'Sin información')}")

    return "\n".join(lineas)


def formatear_politica_para_contexto() -> str:
    """Convierte la política de devoluciones en texto plano para el prompt."""
    lineas = [f"Plazo de devolución: {POLITICA_DEVOLUCIONES['plazo_dias']} días desde la entrega."]
    lineas.append("\nProductos que NO pueden devolverse:")
    for p in POLITICA_DEVOLUCIONES["productos_no_devolvibles"]:
        lineas.append(f"  - {p}")
    lineas.append("\nProductos que SÍ pueden devolverse:")
    for p in POLITICA_DEVOLUCIONES["productos_devolvibles"]:
        lineas.append(f"  - {p}")
    lineas.append("\nProceso de devolución:")
    for paso in POLITICA_DEVOLUCIONES["proceso"]:
        lineas.append(f"  {paso}")
    return "\n".join(lineas)
