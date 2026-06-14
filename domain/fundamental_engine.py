"""Motor fundamental: normaliza las metricas financieras crudas.
 
Recibe el dict que devuelve data_layer.obtener_fundamentales y lo deja en
unidades coherentes para el motor de scoring y la UI. No descarga nada ni
inventa valores: los ausentes se conservan como None.
"""
from __future__ import annotations
 
 
def procesar_fundamentales(crudos: dict) -> dict:
    """Devuelve las metricas fundamentales en unidades coherentes.
 
    Conversiones aplicadas (segun lo observado en la validacion de datos):
      - deuda_capital: Yahoo lo entrega en escala de porcentaje (p. ej. 79.5
        significa un ratio de 0.795). Aqui se divide entre 100 para tener un
        ratio comparable con el criterio de la propuesta "deuda/capital < 1.5".
      - roe y margen_neto se mantienen como fraccion (0.12 = 12%); el scoring
        solo necesita su signo/umbral.
 
    Los valores no disponibles se conservan como None; nunca se inventan.
    """
    crudos = crudos or {}
 
    deuda = crudos.get("deuda_capital")
    # bool es subclase de int en Python; lo excluimos explicitamente por seguridad.
    if isinstance(deuda, (int, float)) and not isinstance(deuda, bool):
        deuda_ratio = deuda / 100
    else:
        deuda_ratio = None
 
    return {
        "nombre": crudos.get("nombre"),
        "moneda": crudos.get("moneda"),
        "sector": crudos.get("sector"),
        "pe": crudos.get("pe"),
        "eps": crudos.get("eps"),
        "roe": crudos.get("roe"),
        "margen_neto": crudos.get("margen_neto"),
        "deuda_capital": deuda_ratio,
        "flujo_caja_libre": crudos.get("flujo_caja_libre"),
    }