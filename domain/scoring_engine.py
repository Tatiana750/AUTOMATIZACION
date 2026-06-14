"""Motor de scoring: NUCLEO DETERMINISTA de la recomendacion.
 
Combina las senales tecnicas y fundamentales aplicando los pesos de
config.PESOS_SCORING y produce un score 0-100, una recomendacion y un desglose
por indicador (para justificar el resultado y para que el chatbot lo explique
sin inventar nada).
 
La recomendacion (Comprar/Neutral/Evitar) SALE DE AQUI, nunca del LLM.
 
Notas de diseno:
  - "P/E vs sector": Yahoo no da una mediana sectorial fiable, asi que se usa un
    umbral fijo (config.PE_ATRACTIVO). Simplificacion transparente.
  - "ROE creciente": sin historico no se mide el crecimiento; se comprueba solo
    que el ROE sea positivo. Mejorable en el futuro.
  - Datos ausentes: los criterios que no se pueden evaluar se excluyen y el
    score se renormaliza sobre los pesos realmente evaluados (no se penaliza por
    datos que faltan).
"""
from __future__ import annotations
 
import math
 
import config
 
_CATEGORIA = {
    "rsi": "Tecnico", "macd": "Tecnico", "precio_sobre_sma200": "Tecnico",
    "bollinger_banda_baja": "Tecnico", "pe_vs_sector": "Fundamental",
    "roe_positivo_creciente": "Fundamental", "deuda_capital": "Fundamental",
    "flujo_caja_libre": "Fundamental",
}
 
 
def _es_numero(x) -> bool:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        return False
    return not (isinstance(x, float) and math.isnan(x))
 
 
def clasificar(score: float) -> str:
    """Traduce un score numerico a etiqueta segun los umbrales de config."""
    if score >= config.UMBRAL_COMPRAR:
        return "Comprar"
    if score >= config.UMBRAL_NEUTRAL:
        return "Neutral"
    return "Evitar"
 
 
def _evaluar(tecnico: dict, fundamental: dict) -> dict:
    """Devuelve, por cada criterio, una tupla (evaluable, cumplido)."""
    t = tecnico or {}
    f = fundamental or {}
 
    rsi, macd, senal = t.get("rsi"), t.get("macd"), t.get("senal")
    precio, sma200, banda_baja = t.get("precio"), t.get("sma200"), t.get("banda_baja")
    pe, roe = f.get("pe"), f.get("roe")
    deuda, fcf = f.get("deuda_capital"), f.get("flujo_caja_libre")
 
    c = {}
    c["rsi"] = (_es_numero(rsi), _es_numero(rsi) and config.RSI_MIN < rsi < config.RSI_MAX)
 
    ev = _es_numero(macd) and _es_numero(senal)
    c["macd"] = (ev, ev and macd > senal)
 
    ev = _es_numero(precio) and _es_numero(sma200)
    c["precio_sobre_sma200"] = (ev, ev and precio > sma200)
 
    ev = _es_numero(precio) and _es_numero(banda_baja)
    c["bollinger_banda_baja"] = (ev, ev and precio <= banda_baja)
 
    c["pe_vs_sector"] = (_es_numero(pe), _es_numero(pe) and 0 < pe < config.PE_ATRACTIVO)
    c["roe_positivo_creciente"] = (_es_numero(roe), _es_numero(roe) and roe > config.ROE_MINIMO)
    c["deuda_capital"] = (_es_numero(deuda), _es_numero(deuda) and deuda < config.DEUDA_CAPITAL_MAX)
    c["flujo_caja_libre"] = (_es_numero(fcf), _es_numero(fcf) and fcf > 0)
    return c
 
 
def calcular_score(tecnico: dict, fundamental: dict, pesos: dict = None) -> dict:
    """Combina senales tecnicas y fundamentales en un score 0-100.
 
    Parametros
    ----------
    tecnico : dict con los ultimos valores tecnicos (rsi, macd, senal, precio,
              sma200, banda_baja).
    fundamental : dict ya normalizado por fundamental_engine (pe, roe,
              deuda_capital, flujo_caja_libre, ...).
 
    Devuelve dict con: score (0-100 o None), recomendacion, desglose,
    peso_evaluado y descargo.
    """
    if pesos is None:
        pesos = config.PESOS_SCORING
 
    criterios = _evaluar(tecnico, fundamental)
 
    peso_evaluado = 0.0
    peso_cumplido = 0.0
    desglose = []
    for nombre, (evaluable, cumplido) in criterios.items():
        peso = pesos.get(nombre, 0)
        if evaluable:
            peso_evaluado += peso
            if cumplido:
                peso_cumplido += peso
        desglose.append({
            "indicador": nombre,
            "categoria": _CATEGORIA.get(nombre, ""),
            "peso": peso,
            "evaluado": evaluable,
            "cumplido": cumplido,
        })
 
    if peso_evaluado == 0:
        return {
            "score": None,
            "recomendacion": "Datos insuficientes",
            "desglose": desglose,
            "peso_evaluado": 0,
            "descargo": config.DESCARGO_RESPONSABILIDAD,
        }
 
    score = round(peso_cumplido / peso_evaluado * 100, 1)
    return {
        "score": score,
        "recomendacion": clasificar(score),
        "desglose": desglose,
        "peso_evaluado": peso_evaluado,
        "descargo": config.DESCARGO_RESPONSABILIDAD,
    }