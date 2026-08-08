"""Configurações centrais do dashboard: ativos, período e parâmetros de cálculo."""

TICKERS = {
    "ITUB4.SA": "Itaú Unibanco (ITUB4)",
    "VALE3.SA": "Vale (VALE3)",
}

# Cor fixa por ativo, usada em todos os gráficos para consistência visual.
TICKER_COLORS = {
    "ITUB4.SA": "#F58220",  # laranja Itaú
    "VALE3.SA": "#0F9D58",  # verde Vale
}

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

MA_WINDOWS_DEFAULT = [20, 50]

CACHE_DIR = "data/cache"

TRADING_DAYS_PER_YEAR = 252
