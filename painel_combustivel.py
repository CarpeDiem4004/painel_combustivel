"""
╔══════════════════════════════════════════════════════╗
║     PAINEL EXECUTIVO - GESTÃO DE COMBUSTÍVEL         ║
║     Desenvolvido com Dash + Plotly                   ║
╚══════════════════════════════════════════════════════╝

COMO USAR:
  1. Instale as dependências (rode UMA VEZ no terminal):
       pip install dash plotly pandas openpyxl

  2. Coloque a planilha .xlsx na mesma pasta deste arquivo
     (ou ajuste o caminho em CAMINHO_PLANILHA abaixo)

  3. Execute:
       python painel_combustivel.py

  4. Abra no navegador:
       http://127.0.0.1:8050
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, dash_table
import warnings
warnings.filterwarnings("ignore")

# ──────────────────────────────────────────
#  CONFIGURAÇÃO — ajuste o caminho se precisar
# ──────────────────────────────────────────
CAMINHO_PLANILHA = "Dados.xlsx"
ABA_DADOS        = "Transações"

# ──────────────────────────────────────────
#  CARREGAMENTO E LIMPEZA DOS DADOS
# ──────────────────────────────────────────
df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=ABA_DADOS)
print("[DEBUG] Início do script.")
print("⏳ Carregando planilha...")
df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=ABA_DADOS)
print("[DEBUG] Planilha carregada.")

df["DATA"]           = df["DATA TRANSACAO"].dt.date
df["ANO_MES"]        = df["DATA TRANSACAO"].dt.to_period("M").astype(str)
df["VALOR EMISSAO"] = pd.to_numeric(df["VALOR EMISSAO"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
df["LITROS"] = pd.to_numeric(df["LITROS"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)
df["VL/LITRO"] = pd.to_numeric(df["VL/LITRO"].astype(str).str.replace(',', '.'), errors="coerce").fillna(0)

print("[DEBUG] Dados tratados.")

df["CODIGO ESTABELECIMENTO"] = df["CODIGO ESTABELECIMENTO"].fillna("N/D").astype(str)
df["Base"]   = df["Base"].fillna("N/D").astype(str)
df["PLACA"]  = df["PLACA"].fillna("N/D").astype(str)

print("[DEBUG] Substituições para exibição feitas.")


DATA_MIN = df["DATA TRANSACAO"].min()
DATA_MAX = df["DATA TRANSACAO"].max()
print(f"✅ {len(df):,} transações carregadas | {DATA_MIN.date()} → {DATA_MAX.date()}")
print("[DEBUG] Datas mínimas e máximas calculadas.")

# ──────────────────────────────────────────
#  PALETA DE CORES
# ──────────────────────────────────────────
CORES = {
    "fundo":      "#0D1117",
    "card":       "#161B22",
    "borda":      "#30363D",
    "primaria":   "#58A6FF",
    "secundaria": "#3FB950",
    "alerta":     "#F78166",
    "amarelo":    "#E3B341",
    "roxo":       "#BC8CFF",
    "texto":      "#E6EDF3",
    "subtexto":   "#8B949E",
}

PALETA_GRAFICOS = [
    "#58A6FF","#3FB950","#F78166","#E3B341",
    "#BC8CFF","#79C0FF","#56D364","#FFA657",
]

LAYOUT_BASE = dict(
    paper_bgcolor=CORES["fundo"],
    plot_bgcolor =CORES["card"],
    font=dict(color=CORES["texto"], family="Segoe UI, sans-serif", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=PALETA_GRAFICOS,
)

def estilo_eixos():
    return dict(
        gridcolor=CORES["borda"],
        linecolor=CORES["borda"],
        tickfont=dict(color=CORES["subtexto"]),
    )

# ──────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────
def formata_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def card(titulo, valor_id, cor=CORES["primaria"], icone="💰"):
    return html.Div([
        html.Div(f"{icone} {titulo}", style={
            "fontSize": "11px", "color": CORES["subtexto"],
            "textTransform": "uppercase", "letterSpacing": "1px", "marginBottom": "6px"
        }),
        html.Div(id=valor_id, style={
            "fontSize": "26px", "fontWeight": "700", "color": cor
        }),
    ], style={
        "background": CORES["card"], "border": f"1px solid {CORES['borda']}",
        "borderLeft": f"3px solid {cor}", "borderRadius": "8px",
        "padding": "20px 24px", "flex": "1", "minWidth": "160px"
    })

# ──────────────────────────────────────────
#  LAYOUT DO PAINEL
# ──────────────────────────────────────────
print("[DEBUG] Antes de criar o app Dash.")
app = Dash(__name__, title="Painel Combustível")
print("[DEBUG] App Dash criado.")

print("[DEBUG] Antes de definir o layout do app.")
app.layout = html.Div(style={
    "background": CORES["fundo"], "minHeight": "100vh",
    "fontFamily": "Segoe UI, sans-serif", "color": CORES["texto"],
    "padding": "24px 32px"
}, children=[

    # ── CABEÇALHO ──
    html.Div([
        html.Div([
            html.H1("⛽ Painel de Combustível", style={
                "margin": "0", "fontSize": "28px", "fontWeight": "700",
                "color": CORES["texto"]
            }),
            html.P("Visão Executiva de Gastos com Combustível",
                   style={"margin": "4px 0 0", "color": CORES["subtexto"], "fontSize": "14px"}),
        ]),
        html.Div(id="periodo-header", style={
            "background": CORES["card"], "border": f"1px solid {CORES['borda']}",
            "borderRadius": "8px", "padding": "10px 20px",
            "fontSize": "13px", "color": CORES["subtexto"]
        })
    ], style={"display": "flex", "justifyContent": "space-between",
              "alignItems": "center", "marginBottom": "24px"}),

    # ── FILTROS ──
    html.Div([
        html.Div([
            html.Label("📅 Período", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
            dcc.DatePickerRange(
                id="filtro-datas",
                min_date_allowed=DATA_MIN.date(),
                max_date_allowed=DATA_MAX.date(),
                start_date=DATA_MIN.date(),
                end_date=DATA_MAX.date(),
                display_format="DD/MM/YYYY",
                style={"fontSize": "13px"}
            ),
        ], style={"flex": "2"}),

        html.Div([
            html.Label("⛽ Combustível", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filtro-combustivel",
                options=[{"label": "Todos", "value": "TODOS"}] +
                        [{"label": c, "value": c} for c in sorted(df["TIPO COMBUSTIVEL"].dropna().unique())],
                value="TODOS", clearable=False,
                style={"background": CORES["card"], "color": "#000"}
            ),
        ], style={"flex": "1", "minWidth": "200px"}),

            html.Div([
                html.Label("🏢 Base", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
                dcc.Dropdown(
                    id="filtro-base",
                    options=[{"label": "Todos", "value": "TODOS"}] +
                            [{"label": b, "value": b} for b in sorted(df["Base"].dropna().unique())],
                    value="TODOS", clearable=False,
                    style={"background": CORES["card"], "color": "#000"}
                ),
            ], style={"flex": "1", "minWidth": "160px"}),

        html.Div([
            html.Label("🚗 Modelo Veículo", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filtro-modelo",
                options=[{"label": "Todos", "value": "TODOS"}] +
                        [{"label": m, "value": m} for m in sorted(df["MODELO VEICULO"].dropna().unique())],
                value="TODOS", clearable=False,
                style={"background": CORES["card"], "color": "#000"}
            ),
        ], style={"flex": "1", "minWidth": "200px"}),

        html.Div([
            html.Label("🏛️ UF", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filtro-uf",
                options=[{"label": "Todos", "value": "TODOS"}] +
                        [{"label": u, "value": u} for u in sorted(df["UF"].dropna().unique())],
                value="TODOS", clearable=False,
                style={"background": CORES["card"], "color": "#000"}
            ),
        ], style={"flex": "1", "minWidth": "120px"}),

        html.Div([
            html.Label("🆔 ID", style={"fontSize": "12px", "color": CORES["subtexto"], "marginBottom": "6px", "display": "block"}),
            dcc.Dropdown(
                id="filtro-id",
                options=[{"label": "Todos", "value": "TODOS"}] +
                        [{"label": str(i), "value": str(i)} for i in sorted(df["ID"].dropna().unique())],
                value="TODOS", clearable=False,
                style={"background": CORES["card"], "color": "#000"}
            ),
        ], style={"flex": "1", "minWidth": "120px"}),

    ], style={
        "display": "flex", "gap": "16px", "flexWrap": "wrap",
        "background": CORES["card"], "border": f"1px solid {CORES['borda']}",
        "borderRadius": "8px", "padding": "20px", "marginBottom": "24px"
    }),

    # ── KPI CARDS ──
    html.Div([
        card("Valor Total",    "kpi-total",       CORES["primaria"],   "💰"),
        card("Nº Transações",  "kpi-transacoes",  CORES["secundaria"], "🔢"),
        card("Total Litros",   "kpi-litros",       CORES["amarelo"],    "🪣"),
        card("Preço Médio/L",  "kpi-preco-medio",  CORES["roxo"],       "📊"),
        card("Veículos Únicos","kpi-veiculos",     CORES["alerta"],     "🚛"),
        card("Cidades",        "kpi-cidades",      "#79C0FF",           "📍"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

    # ── GRÁFICOS LINHA 1 ──
    html.Div([
        html.Div([
            dcc.Graph(id="graf-timeline", config={"displayModeBar": False}),
        ], style={"flex": "2", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),

        html.Div([
            dcc.Graph(id="graf-combustivel-pizza", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # ── GRÁFICOS LINHA 2 ──
    html.Div([
        html.Div([
            dcc.Graph(id="graf-top-cidades", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),

        html.Div([
            dcc.Graph(id="graf-top-modelos", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),

        html.Div([
            dcc.Graph(id="graf-uf-mapa", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # ── GRÁFICO PREÇO MÉDIO POR COMBUSTÍVEL ──
    html.Div([
        html.Div([
            dcc.Graph(id="graf-preco-combustivel", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),

        html.Div([
            dcc.Graph(id="graf-gasto-placa", config={"displayModeBar": False}),
        ], style={"flex": "1", "background": CORES["card"],
                  "border": f"1px solid {CORES['borda']}", "borderRadius": "8px", "padding": "16px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "24px"}),

    # ── TABELA DETALHADA ──
    html.Div([
        html.Div([
            html.H3("📋 Transações Detalhadas", style={
                "margin": "0 0 16px", "fontSize": "16px", "color": CORES["texto"]
            }),
            html.Div(id="tabela-container"),
        ], style={
            "background": CORES["card"], "border": f"1px solid {CORES['borda']}",
            "borderRadius": "8px", "padding": "20px"
        }),
    ]),

    # ── RODAPÉ ──
    html.Div(
        "Painel Executivo de Combustível • Dados carregados da planilha",
        style={"textAlign": "center", "color": CORES["subtexto"],
               "fontSize": "12px", "marginTop": "32px", "paddingBottom": "16px"}
    ),

])

# ──────────────────────────────────────────
#  CALLBACK PRINCIPAL
# ──────────────────────────────────────────
@app.callback(
    Output("periodo-header",        "children"),
    Output("kpi-total",             "children"),
    Output("kpi-transacoes",        "children"),
    Output("kpi-litros",            "children"),
    Output("kpi-preco-medio",       "children"),
    Output("kpi-veiculos",          "children"),
    Output("kpi-cidades",           "children"),
    Output("graf-timeline",         "figure"),
    Output("graf-combustivel-pizza","figure"),
    Output("graf-top-cidades",      "figure"),
    Output("graf-top-modelos",      "figure"),
    Output("graf-uf-mapa",          "figure"),
    Output("graf-preco-combustivel","figure"),
    Output("graf-gasto-placa",      "figure"),
    Output("tabela-container",      "children"),
    Input("filtro-datas",       "start_date"),
    Input("filtro-datas",       "end_date"),
    Input("filtro-combustivel", "value"),
    Input("filtro-modelo",      "value"),
    Input("filtro-uf",          "value"),
        Input("filtro-base",        "value"),
        Input("filtro-id",          "value"),
)
def atualiza_painel(start_date, end_date, combustivel, modelo, uf, base, id_value):
    # ── Filtrar ──
    dff = df.copy()
    if start_date:
        dff = dff[dff["DATA TRANSACAO"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["DATA TRANSACAO"] <= pd.to_datetime(end_date) + pd.Timedelta(days=1)]
    if combustivel != "TODOS":
        dff = dff[dff["TIPO COMBUSTIVEL"] == combustivel]
    if modelo != "TODOS":
        dff = dff[dff["MODELO VEICULO"] == modelo]
    if uf != "TODOS":
        dff = dff[dff["UF"] == uf]
    if base != "TODOS":
        dff = dff[dff["Base"] == base]
    if id_value != "TODOS":
        dff = dff[dff["ID"].astype(str) == id_value]

    # ── KPIs ──
    total_valor   = dff["VALOR EMISSAO"].sum()
    total_trans   = len(dff)
    total_litros  = dff["LITROS"].sum()
    preco_medio   = (dff["VL/LITRO"].replace(0, pd.NA).mean()) if len(dff) else 0
    veiculos      = dff["PLACA"].nunique()
    cidades       = dff["CIDADE"].nunique()

    periodo_txt = (
        f"📅 {pd.to_datetime(start_date).strftime('%d/%m/%Y') if start_date else '—'} "
        f"→ {pd.to_datetime(end_date).strftime('%d/%m/%Y') if end_date else '—'} "
        f"| {total_trans:,} registros"
    )

    # ── Gráfico 1: Timeline de gastos por dia ──
    timeline = dff.groupby("DATA")["VALOR EMISSAO"].sum().reset_index()
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=timeline["DATA"], y=timeline["VALOR EMISSAO"],
        mode="lines", fill="tozeroy",
        line=dict(color=CORES["primaria"], width=2),
        fillcolor="rgba(88,166,255,0.15)",
        name="Valor/Dia"
    ))
    fig_timeline.update_layout(
        **LAYOUT_BASE, title="💸 Gastos por Dia",
        xaxis=dict(title="", **estilo_eixos()),
        yaxis=dict(title="R$", **estilo_eixos()),
        showlegend=False,
    )

    # ── Gráfico 2: Pizza combustível ──
    pizza_data = dff.groupby("TIPO COMBUSTIVEL")["VALOR EMISSAO"].sum().reset_index()
    fig_pizza = px.pie(
        pizza_data, names="TIPO COMBUSTIVEL", values="VALOR EMISSAO",
        title="⛽ Valor por Combustível",
        color_discrete_sequence=PALETA_GRAFICOS,
        hole=0.45,
    )
    fig_pizza.update_layout(**LAYOUT_BASE)
    fig_pizza.update_traces(textinfo="percent+label", textfont_size=11)

    # ── Gráfico 3: Top 10 cidades ──
    top_cidades = (
        dff.groupby("CIDADE")["VALOR EMISSAO"].sum()
        .nlargest(10).reset_index().sort_values("VALOR EMISSAO")
    )
    fig_cidades = px.bar(
        top_cidades, x="VALOR EMISSAO", y="CIDADE",
        orientation="h", title="📍 Top 10 Cidades (Gasto)",
        color="VALOR EMISSAO", color_continuous_scale=["#1c3a5f", CORES["primaria"]],
    )
    fig_cidades.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
        xaxis=dict(title="R$", **estilo_eixos()),
        yaxis=dict(title="", **estilo_eixos()),
    )

    # ── Gráfico 4: Top 10 modelos ──
    top_modelos = (
        dff.groupby("MODELO VEICULO")["VALOR EMISSAO"].sum()
        .nlargest(10).reset_index().sort_values("VALOR EMISSAO")
    )
    fig_modelos = px.bar(
        top_modelos, x="VALOR EMISSAO", y="MODELO VEICULO",
        orientation="h", title="🚛 Top 10 Modelos (Gasto)",
        color="VALOR EMISSAO", color_continuous_scale=["#1a3d1a", CORES["secundaria"]],
    )
    fig_modelos.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
        xaxis=dict(title="R$", **estilo_eixos()),
        yaxis=dict(title="", **estilo_eixos()),
    )

    # ── Gráfico 5: Mapa UF (barras horizontais) ──
    uf_data = (
        dff.groupby("UF")["VALOR EMISSAO"].sum()
        .nlargest(15).reset_index().sort_values("VALOR EMISSAO")
    )
    fig_uf = px.bar(
        uf_data, x="VALOR EMISSAO", y="UF",
        orientation="h", title="🗺️ Gasto por Estado (UF)",
        color="VALOR EMISSAO", color_continuous_scale=["#3d1a3d", CORES["roxo"]],
    )
    fig_uf.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
        xaxis=dict(title="R$", **estilo_eixos()),
        yaxis=dict(title="", **estilo_eixos()),
    )

    # ── Gráfico 6: Preço médio/L por combustível ──
    preco_comb = (
        dff[dff["VL/LITRO"] > 0]
        .groupby("TIPO COMBUSTIVEL")["VL/LITRO"].mean()
        .reset_index().sort_values("VL/LITRO", ascending=False)
    )
    fig_preco = px.bar(
        preco_comb, x="TIPO COMBUSTIVEL", y="VL/LITRO",
        title="📊 Preço Médio por Litro (R$/L)",
        color="VL/LITRO", color_continuous_scale=["#3d2a00", CORES["amarelo"]],
        text_auto=".2f",
    )
    fig_preco.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
        xaxis=dict(title="", **estilo_eixos(), tickangle=-30),
        yaxis=dict(title="R$/Litro", **estilo_eixos()),
    )

    # ── Gráfico 7: Top 15 placas por gasto ──
    top_placas = (
        dff.groupby("PLACA")["VALOR EMISSAO"].sum()
        .nlargest(15).reset_index().sort_values("VALOR EMISSAO")
    )
    fig_placas = px.bar(
        top_placas, x="VALOR EMISSAO", y="PLACA",
        orientation="h", title="🚘 Top 15 Veículos por Gasto (Placa)",
        color="VALOR EMISSAO", color_continuous_scale=["#3d1a00", CORES["alerta"]],
    )
    fig_placas.update_layout(**LAYOUT_BASE, coloraxis_showscale=False,
        xaxis=dict(title="R$", **estilo_eixos()),
        yaxis=dict(title="", **estilo_eixos()),
    )

    # ── Tabela ──
    colunas_tabela = [
        "DATA TRANSACAO","PLACA","MODELO VEICULO","TIPO COMBUSTIVEL",
        "LITROS","VL/LITRO","VALOR EMISSAO","NOME ESTABELECIMENTO","CIDADE","UF"
    ]
    dff_tabela = dff[colunas_tabela].copy()
    dff_tabela["DATA TRANSACAO"] = dff_tabela["DATA TRANSACAO"].dt.strftime("%d/%m/%Y %H:%M")
    dff_tabela["LITROS"]         = dff_tabela["LITROS"].map("{:.2f}".format)
    dff_tabela["VL/LITRO"]       = dff_tabela["VL/LITRO"].map("R$ {:.3f}".format)
    dff_tabela["VALOR EMISSAO"]  = dff_tabela["VALOR EMISSAO"].map("R$ {:,.2f}".format)

    tabela = dash_table.DataTable(
        data=dff_tabela.head(500).to_dict("records"),
        columns=[{"name": c, "id": c} for c in colunas_tabela],
        page_size=15,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#21262D",
            "color": CORES["primaria"],
            "fontWeight": "bold",
            "fontSize": "12px",
            "border": f"1px solid {CORES['borda']}",
        },
        style_cell={
            "backgroundColor": CORES["card"],
            "color": CORES["texto"],
            "border": f"1px solid {CORES['borda']}",
            "fontSize": "12px",
            "padding": "8px 12px",
            "textOverflow": "ellipsis",
            "maxWidth": "180px",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#1C2128"},
        ],
    )

    return (
        periodo_txt,
        formata_brl(total_valor),
        f"{total_trans:,}",
        f"{total_litros:,.0f} L",
        f"R$ {preco_medio:.3f}" if preco_medio else "—",
        str(veiculos),
        str(cidades),
        fig_timeline,
        fig_pizza,
        fig_cidades,
        fig_modelos,
        fig_uf,
        fig_preco,
        fig_placas,
        tabela,
    )


# ──────────────────────────────────────────
#  INICIA O SERVIDOR
# ──────────────────────────────────────────
import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8051))
    print("\n" + "═"*55)
    print(f"  🚀 PAINEL COMBUSTÍVEL — iniciando servidor na porta {port}...")
    print(f"  🌐 Acesse: http://127.0.0.1:{port}")
    print("  🛑 Para parar: Ctrl+C")
    print("═"*55 + "\n")
    app.run(debug=False, host="0.0.0.0", port=port)

# ──────────────────────────────────────────
#  INICIA O SERVIDOR COM GUNICORN
# ──────────────────────────────────────────
# gunicorn painel_combustivel:app