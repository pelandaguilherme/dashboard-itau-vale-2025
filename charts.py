"""Construção dos gráficos Plotly do dashboard.

Cada função recebe dados já calculados e devolve uma go.Figure — sem
dependência do Streamlit, para manter a apresentação isolada da lógica de UI.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from metrics import cumulative_return_base100, drawdown, moving_average

LAYOUT_DEFAULTS = dict(
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=20, t=40, b=40),
)


def price_chart(data: dict, names: dict, colors: dict) -> go.Figure:
    fig = go.Figure()
    for ticker, df in data.items():
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name=names.get(ticker, ticker),
                line=dict(color=colors.get(ticker)),
            )
        )
    fig.update_layout(
        title="Preço de fechamento (2025)",
        yaxis_title="Preço (R$)",
        **LAYOUT_DEFAULTS,
    )
    return fig


def normalized_return_chart(data: dict, names: dict, colors: dict) -> go.Figure:
    fig = go.Figure()
    for ticker, df in data.items():
        series = cumulative_return_base100(df["Close"])
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series,
                mode="lines",
                name=names.get(ticker, ticker),
                line=dict(color=colors.get(ticker)),
            )
        )
    fig.add_hline(y=100, line_dash="dot", line_color="gray")
    fig.update_layout(
        title="Retorno acumulado normalizado (base 100 = início de 2025)",
        yaxis_title="Índice (base 100)",
        **LAYOUT_DEFAULTS,
    )
    return fig


def price_volume_panel(ticker: str, df, name: str, color: str, ma_windows) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        subplot_titles=(f"{name} — Preço e médias móveis", "Volume"),
    )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Fechamento", line=dict(color=color)),
        row=1,
        col=1,
    )
    ma_colors = ["#888888", "#444444"]
    for window, ma_color in zip(ma_windows, ma_colors):
        ma_series = moving_average(df["Close"], window)
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=ma_series,
                mode="lines",
                name=f"MM{window}",
                line=dict(color=ma_color, dash="dash", width=1),
            ),
            row=1,
            col=1,
        )

    if "Volume" in df.columns:
        fig.add_trace(
            go.Bar(x=df.index, y=df["Volume"], name="Volume", marker=dict(color=color, opacity=0.5)),
            row=2,
            col=1,
        )

    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_layout(showlegend=True, height=520, **{k: v for k, v in LAYOUT_DEFAULTS.items() if k != "margin"})
    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
    return fig


def drawdown_chart(data: dict, names: dict, colors: dict) -> go.Figure:
    fig = go.Figure()
    for ticker, df in data.items():
        dd = drawdown(df["Close"]) * 100
        fig.add_trace(
            go.Scatter(
                x=dd.index,
                y=dd,
                mode="lines",
                name=names.get(ticker, ticker),
                fill="tozeroy",
                line=dict(color=colors.get(ticker)),
            )
        )
    fig.update_layout(
        title="Drawdown (queda % em relação ao pico acumulado)",
        yaxis_title="Drawdown (%)",
        **LAYOUT_DEFAULTS,
    )
    return fig
