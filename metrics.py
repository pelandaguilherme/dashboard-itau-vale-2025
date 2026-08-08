"""Cálculos de performance: retorno acumulado, volatilidade, drawdown, médias móveis.

Funções puras que recebem DataFrames/Series do pandas — testáveis sem Streamlit.
"""

import pandas as pd

from config import TRADING_DAYS_PER_YEAR


def daily_returns(close: pd.Series) -> pd.Series:
    return close.pct_change().dropna()


def cumulative_return_base100(close: pd.Series) -> pd.Series:
    """Normaliza a série para começar em 100 — permite comparar performance
    relativa entre ativos com preços de magnitudes diferentes no mesmo eixo."""
    return close / close.iloc[0] * 100


def total_return_pct(close: pd.Series) -> float:
    return float((close.iloc[-1] / close.iloc[0] - 1) * 100)


def annualized_volatility(close: pd.Series) -> float:
    returns = daily_returns(close)
    return float(returns.std() * (TRADING_DAYS_PER_YEAR ** 0.5))


def drawdown(close: pd.Series) -> pd.Series:
    running_max = close.cummax()
    return close / running_max - 1


def max_drawdown_pct(close: pd.Series) -> float:
    return float(drawdown(close).min() * 100)


def moving_average(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).mean()


def summary_table(data: dict, ticker_names: dict) -> pd.DataFrame:
    """data: {ticker: DataFrame com colunas Close/Volume}"""
    rows = []
    for ticker, df in data.items():
        close = df["Close"]
        volume = df["Volume"] if "Volume" in df.columns else None
        rows.append(
            {
                "Ativo": ticker_names.get(ticker, ticker),
                "Retorno total (%)": round(total_return_pct(close), 2),
                "Preço mínimo (R$)": round(float(close.min()), 2),
                "Preço máximo (R$)": round(float(close.max()), 2),
                "Volatilidade anualizada (%)": round(annualized_volatility(close) * 100, 2),
                "Drawdown máximo (%)": round(max_drawdown_pct(close), 2),
                "Volume médio diário": int(volume.mean()) if volume is not None else None,
            }
        )
    return pd.DataFrame(rows)
