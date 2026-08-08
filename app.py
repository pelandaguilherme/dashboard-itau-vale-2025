"""Dashboard Streamlit: cotação e performance de ITUB4 e VALE3 em 2025."""

import pandas as pd
import streamlit as st

import charts
import metrics
from config import MA_WINDOWS_DEFAULT, START_DATE, END_DATE, TICKER_COLORS, TICKERS
from data_loader import fetch_all

st.set_page_config(page_title="Itaú x Vale — 2025", page_icon="📈", layout="wide")

st.title("📈 Itaú (ITUB4) x Vale (VALE3) — Cotação e performance em 2025")

# ---------------------------------------------------------------- Sidebar --
st.sidebar.header("Filtros")

selected_tickers = st.sidebar.multiselect(
    "Ativos",
    options=list(TICKERS.keys()),
    default=list(TICKERS.keys()),
    format_func=lambda t: TICKERS[t],
)

date_range = st.sidebar.date_input(
    "Período",
    value=(pd.Timestamp(START_DATE).date(), pd.Timestamp(END_DATE).date()),
    min_value=pd.Timestamp(START_DATE).date(),
    max_value=pd.Timestamp(END_DATE).date(),
)

ma_windows = st.sidebar.multiselect(
    "Médias móveis (dias)",
    options=[10, 20, 50, 100],
    default=MA_WINDOWS_DEFAULT,
)

force_refresh = st.sidebar.button("🔄 Atualizar dados")

if not selected_tickers:
    st.warning("Selecione ao menos um ativo na barra lateral.")
    st.stop()

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = pd.Timestamp(START_DATE).date(), pd.Timestamp(END_DATE).date()


# ------------------------------------------------------------- Data load --
@st.cache_data(ttl=3600, show_spinner="Buscando cotações no Yahoo Finance...")
def load_data(tickers, start, end, _cache_bust):
    return fetch_all(tickers, str(start), str(end))


cache_bust = st.session_state.get("cache_bust", 0)
if force_refresh:
    cache_bust += 1
    st.session_state["cache_bust"] = cache_bust
    load_data.clear()

results = load_data(tuple(selected_tickers), start_date, end_date, cache_bust)

data = {}
for ticker in selected_tickers:
    df, status, detail = results[ticker]
    name = TICKERS[ticker]
    if status == "error":
        st.error(
            f"❌ {name}: não foi possível obter os dados do Yahoo Finance. "
            f"Verifique sua conexão com a internet ou tente novamente mais tarde."
            + (f" (detalhe: {detail})" if detail else "")
        )
        continue
    if status == "cache":
        st.warning(
            f"⚠️ {name}: sem conexão com o Yahoo Finance agora — exibindo dados em "
            f"cache local (última atualização: {detail})."
        )
    data[ticker] = df

if not data:
    st.stop()

names = {t: TICKERS[t] for t in data}
colors = TICKER_COLORS
active_ma_windows = ma_windows or MA_WINDOWS_DEFAULT

# ---------------------------------------------------------- Métricas topo --
st.subheader("Resumo")
cols = st.columns(len(data))
for col, (ticker, df) in zip(cols, data.items()):
    close = df["Close"]
    with col:
        st.markdown(f"**{names[ticker]}**")
        st.metric("Retorno total", f"{metrics.total_return_pct(close):.2f}%")
        st.metric("Volatilidade anualizada", f"{metrics.annualized_volatility(close) * 100:.2f}%")
        st.metric("Drawdown máximo", f"{metrics.max_drawdown_pct(close):.2f}%")

# --------------------------------------------------------------- Gráficos --
st.plotly_chart(charts.price_chart(data, names, colors), use_container_width=True)
st.plotly_chart(charts.normalized_return_chart(data, names, colors), use_container_width=True)

st.subheader("Preço, médias móveis e volume por ativo")
for ticker, df in data.items():
    st.plotly_chart(
        charts.price_volume_panel(ticker, df, names[ticker], colors.get(ticker), active_ma_windows),
        use_container_width=True,
    )

st.plotly_chart(charts.drawdown_chart(data, names, colors), use_container_width=True)

# ----------------------------------------------------------------- Tabela --
st.subheader("Tabela resumo")
st.dataframe(metrics.summary_table(data, names), use_container_width=True)

with st.expander("Dados brutos"):
    for ticker, df in data.items():
        st.markdown(f"**{names[ticker]}**")
        st.dataframe(df, use_container_width=True)
        csv_bytes = df.to_csv().encode("utf-8")
        st.download_button(
            f"Baixar CSV — {names[ticker]}",
            data=csv_bytes,
            file_name=f"{ticker}_2025.csv",
            mime="text/csv",
            key=f"download_{ticker}",
        )
