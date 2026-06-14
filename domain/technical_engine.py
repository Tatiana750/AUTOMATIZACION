"""Motor tecnico: calcula indicadores sobre el historico de precios.
 
Recibe el DataFrame que devuelve data_layer.obtener_historico (con columna
'Close'). No llama a ninguna API: logica de negocio pura, facil de testear.
Devuelve series/tablas completas (utiles para graficar); el motor de scoring
tomara despues el ultimo valor de cada indicador.
"""
from __future__ import annotations
 
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands
 
 
def _cierre(precios: pd.DataFrame):
    """Devuelve la serie de cierres, o None si no hay datos utilizables."""
    if precios is None or precios.empty or "Close" not in precios.columns:
        return None
    return precios["Close"]
 
 
def calcular_rsi(precios: pd.DataFrame, ventana: int = 14) -> pd.Series:
    """Indice de Fuerza Relativa (0-100). Serie vacia si no hay datos."""
    close = _cierre(precios)
    if close is None:
        return pd.Series(dtype="float64")
    return RSIIndicator(close=close, window=ventana).rsi()
 
 
def calcular_macd(precios: pd.DataFrame) -> pd.DataFrame:
    """MACD: columnas 'macd', 'senal' e 'histograma'. Vacio si no hay datos."""
    close = _cierre(precios)
    if close is None:
        return pd.DataFrame(columns=["macd", "senal", "histograma"])
    m = MACD(close=close)
    return pd.DataFrame({
        "macd": m.macd(),
        "senal": m.macd_signal(),
        "histograma": m.macd_diff(),
    })
 
 
def calcular_bollinger(precios: pd.DataFrame, ventana: int = 20) -> pd.DataFrame:
    """Bandas de Bollinger: columnas 'media', 'banda_alta', 'banda_baja'."""
    close = _cierre(precios)
    if close is None:
        return pd.DataFrame(columns=["media", "banda_alta", "banda_baja"])
    bb = BollingerBands(close=close, window=ventana, window_dev=2)
    return pd.DataFrame({
        "media": bb.bollinger_mavg(),
        "banda_alta": bb.bollinger_hband(),
        "banda_baja": bb.bollinger_lband(),
    })
 
 
def calcular_medias_moviles(precios: pd.DataFrame) -> pd.DataFrame:
    """Medias moviles SMA 20/50/200 y EMA 20.
 
    La SMA 200 marca la tendencia de largo plazo (criterio del scoring). Necesita
    al menos 200 dias de historico; con periodos cortos saldra NaN, y eso es
    correcto: no se inventa una tendencia que no se puede calcular.
    """
    close = _cierre(precios)
    if close is None:
        return pd.DataFrame(columns=["sma20", "sma50", "sma200", "ema20"])
    return pd.DataFrame({
        "sma20": SMAIndicator(close=close, window=20).sma_indicator(),
        "sma50": SMAIndicator(close=close, window=50).sma_indicator(),
        "sma200": SMAIndicator(close=close, window=200).sma_indicator(),
        "ema20": EMAIndicator(close=close, window=20).ema_indicator(),
    })