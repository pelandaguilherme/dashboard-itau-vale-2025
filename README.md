# Itaú x Vale — Dashboard 2025

Dashboard em Streamlit para analisar a cotação e a performance das ações
ITUB4 (Itaú Unibanco PN) e VALE3 (Vale ON) durante o ano de 2025.

## O que o dashboard mostra

- Cards com retorno total, volatilidade anualizada e drawdown máximo
- Preço de fechamento ao longo do ano
- Retorno acumulado normalizado (base 100), para comparar performance relativa
- Preço + médias móveis e volume, um painel por ativo
- Drawdown (queda % em relação ao pico) ao longo do tempo
- Tabela resumo e download dos dados brutos em CSV

Os dados vêm do Yahoo Finance (`yfinance`). Se não houver conexão, o app usa
automaticamente o último cache local salvo em `data/cache/` e avisa na tela.

## Pré-requisitos

- Python 3.12 (use o comando `python`, **não** `py` — nesta máquina o `py`
  aponta para o Python 3.14, que ainda não tem suporte maduro em todas as
  bibliotecas de dados usadas aqui).

## Como rodar

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre automaticamente em `http://localhost:8501`.

### Problema ao ativar o venv?

Se o PowerShell bloquear a ativação com um erro de política de execução,
rode uma vez (na sessão atual):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Yahoo Finance fora do ar ou sem internet?

O app detecta a falha automaticamente e usa o cache local mais recente,
mostrando um aviso amarelo na tela com a data do cache. Se nunca houve uma
busca bem-sucedida, ele mostra uma mensagem de erro em vez de quebrar.

### Atualizar depois que o Yahoo Finance mudar algo

```powershell
pip install -U yfinance
```

## Estrutura do projeto

```
app.py            # UI Streamlit (sidebar, métricas, gráficos)
config.py         # tickers, período, cores, janelas de médias móveis
data_loader.py     # busca yfinance + cache local + fallback
metrics.py          # cálculos: retorno, volatilidade, drawdown, médias móveis
charts.py            # construção dos gráficos Plotly
data/cache/           # CSVs de cache gerados em runtime (fora do git)
```
