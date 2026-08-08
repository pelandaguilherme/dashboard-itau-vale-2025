"""Busca de cotações via yfinance, com cache local em CSV e fallback automático.

Este módulo não depende do Streamlit — pode ser testado isoladamente.
"""

import os
from datetime import datetime

import pandas as pd
import yfinance as yf

from config import CACHE_DIR


def _cache_path(ticker: str) -> str:
    safe_name = ticker.replace(".", "_")
    return os.path.join(CACHE_DIR, f"{safe_name}.csv")


def _save_cache(ticker: str, df: pd.DataFrame) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    df.to_csv(_cache_path(ticker))


def _load_cache(ticker: str):
    path = _cache_path(ticker)
    if not os.path.exists(path):
        return None, None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    cache_date = datetime.fromtimestamp(os.path.getmtime(path))
    return df, cache_date


def _end_exclusive(end_date_str: str) -> str:
    """yfinance trata 'end' como exclusivo; soma 1 dia para incluir o último dia do período."""
    end = pd.Timestamp(end_date_str) + pd.Timedelta(days=1)
    return end.strftime("%Y-%m-%d")


def fetch_ticker(ticker: str, start: str, end: str):
    """Busca dados ao vivo; se falhar, cai para o cache local.

    Retorna (df, status, detail):
      status "live"  -> dados frescos do Yahoo Finance (cache atualizado)
      status "cache" -> dados vindos do cache local; detail = data/hora do cache formatada
      status "error" -> nenhum dado disponível; detail = mensagem de erro
    """
    live_error = None
    try:
        raw = yf.download(
            ticker,
            start=start,
            end=_end_exclusive(end),
            auto_adjust=True,
            progress=False,
        )
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        if raw is not None and not raw.empty:
            _save_cache(ticker, raw)
            return raw, "live", None
        live_error = "O Yahoo Finance não retornou dados para este período."
    except Exception as exc:  # rede indisponível, ticker inválido, mudança de API, etc.
        live_error = str(exc)

    cached, cache_date = _load_cache(ticker)
    if cached is not None and not cached.empty:
        cache_label = cache_date.strftime("%d/%m/%Y %H:%M") if cache_date else "desconhecida"
        return cached, "cache", cache_label

    return None, "error", live_error


def fetch_all(tickers, start: str, end: str) -> dict:
    """Busca uma lista de tickers; falha em um ticker não impede os demais."""
    results = {}
    for ticker in tickers:
        results[ticker] = fetch_ticker(ticker, start, end)
    return results
