"""Script de validacion de la capa de datos (uso puntual, no es parte de la app).

Comprueba que devuelve yfinance para un ticker de cada mercado. Ejecutar desde
la RAIZ del repositorio, con el entorno virtual activado y las dependencias
instaladas (pip install -r requirements.txt):

    python validar_datos.py

Copia toda la salida y pasala para decidir el alcance de los mercados.
"""
from data_layer.yahoo_client import obtener_historico, obtener_fundamentales

# Incluimos EC y ECOPETROL.CL a proposito para ver cual resuelve Ecopetrol.
TICKERS = ["AAPL", "ECOPETROL.CL", "EC", "WALMEX.MX", "PETR4.SA"]


def revisar(ticker: str) -> None:
    print("=" * 60)
    print(f"TICKER: {ticker}")
    print("-" * 60)

    hist = obtener_historico(ticker, periodo="3mo")
    if hist.empty:
        print("  PRECIOS: vacio (ticker no encontrado o sin datos)")
    else:
        primera = hist.index.min().date()
        ultima = hist.index.max().date()
        cierre = hist["Close"].iloc[-1]
        print(f"  PRECIOS: {len(hist)} filas | {primera} a {ultima} | ultimo cierre: {cierre:.2f}")

    fund = obtener_fundamentales(ticker)
    print(f"  NOMBRE : {fund.get('nombre')}")
    print(f"  MONEDA : {fund.get('moneda')} | SECTOR: {fund.get('sector')}")
    print("  FUNDAMENTALES:")
    for clave in ["pe", "eps", "roe", "deuda_capital", "margen_neto", "flujo_caja_libre"]:
        valor = fund.get(clave)
        estado = "(falta)" if valor is None else valor
        print(f"     {clave:<18}: {estado}")
    print()


if __name__ == "__main__":
    for t in TICKERS:
        revisar(t)
    print("Validacion terminada.")
