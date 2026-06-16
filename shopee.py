import streamlit as st
import pandas as pd
import altair as alt
import json
import os

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Boutique Ferrer – Shopee", page_icon="🛍️", layout="wide")

# =========================
# ESTILOS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main{background:#F5F7FB;}
.block-container{padding-top:0!important;padding-bottom:2rem;max-width:1380px!important;margin:0 auto;}
header[data-testid="stHeader"]{display:none!important;}
#MainMenu,footer{display:none!important;}
.navbar{background:linear-gradient(90deg,#CC0001 0%,#EE4D2D 50%,#CC0001 100%);
        padding:0 32px;height:52px;display:flex;align-items:center;
        box-shadow:0 3px 16px rgba(238,77,45,.35);margin-bottom:20px;border-radius:0 0 12px 12px;}
.navbar-name{color:white;font-size:15px;font-weight:900;letter-spacing:1px;margin-left:10px;}
.card{background:white;border-radius:24px;padding:28px;
      box-shadow:0 8px 28px rgba(15,23,42,.08);border:1px solid #E7ECF5;margin-bottom:18px;}
.hero{background:linear-gradient(135deg,#CC0001 0%,#EE4D2D 55%,#FF6633 100%);
      border-radius:24px;padding:34px 38px;color:white;
      box-shadow:0 18px 45px rgba(238,77,45,.28);margin-bottom:18px;}
.hero-title{font-size:48px;font-weight:900;line-height:1;margin:0 0 22px 0;letter-spacing:-1.6px;}
.hero-small{font-size:14px;font-weight:700;opacity:.95;margin-bottom:0;}
.hero-value-label{font-size:18px;font-weight:800;opacity:.98;text-align:right;}
.hero-value{font-size:60px;font-weight:900;line-height:1.05;text-align:right;letter-spacing:-2px;}
.metric-card{background:#FFFFFF;border:1px dashed #D9E2F0;border-radius:16px;
             padding:24px 22px 20px 22px;min-height:155px;position:relative;overflow:hidden;}
.metric-card:after{content:"";position:absolute;height:8px;left:0;bottom:0;right:0;background:var(--accent);}
.metric-title{font-size:22px;font-weight:800;color:var(--accent);margin-bottom:12px;text-align:center;}
.metric-value{font-size:30px;font-weight:900;color:#020617;text-align:center;letter-spacing:-1px;}
.metric-pill{margin:12px auto 0 auto;width:fit-content;border-radius:999px;padding:5px 16px;
             border:1px solid #E2E8F0;color:#94A3B8;font-weight:800;font-size:14px;background:#FAFBFF;}
.kpi-card{background:#F4F1EA;border-radius:14px;padding:18px 14px;text-align:center;
          min-height:112px;display:flex;flex-direction:column;justify-content:center;overflow:hidden;}
.kpi-title{font-size:13px;font-weight:800;color:#44403C;text-transform:uppercase;
           letter-spacing:.25px;margin-bottom:10px;white-space:nowrap;}
.kpi-value{font-size:clamp(20px,2.05vw,28px);font-weight:900;color:#1F2937;
           letter-spacing:-.8px;white-space:nowrap;line-height:1.05;}
.green-box{background:linear-gradient(135deg,#22C55E 0%,#16A34A 100%);color:white;
           border-radius:16px;padding:26px;box-shadow:0 18px 35px rgba(34,197,94,.22);
           min-height:138px;text-align:center;}
.red-box{background:linear-gradient(135deg,#EF4444 0%,#B91C1C 100%);color:white;
         border-radius:16px;padding:26px;box-shadow:0 18px 35px rgba(239,68,68,.18);
         min-height:138px;text-align:center;}
.green-title{font-size:24px;font-weight:900;margin-bottom:8px;}
.green-value{font-size:36px;font-weight:900;line-height:1;}
.green-sub{font-size:17px;font-weight:900;margin-top:6px;}
.small-title{font-size:26px;font-weight:900;color:#020617;margin-bottom:2px;letter-spacing:-.7px;}
.muted{color:#64748B;font-size:16px;}
</style>
""", unsafe_allow_html=True)

# =========================
# NAVBAR
# =========================
st.markdown(
    '<div class="navbar"><span style="font-size:20px;">🛍️</span>'
    '<span class="navbar-name">BOUTIQUE FERRER — SHOPEE</span></div>',
    unsafe_allow_html=True,
)


# =========================
# CONSTANTES
# =========================
COLUNAS_NECESSARIAS = [
    "ID do pedido",
    "Status do pedido",
    "Nome do Produto",
    "Nome da variação",
    "Quantidade",
    "Subtotal do produto",
    "Taxa de comissão líquida",
    "Taxa de serviço líquida",
    "Desconto do vendedor",
    "Data de criação do pedido",
]

# Unidades base de estoque disponíveis
UNIDADES_LISA    = ["Polo Lisa Preta", "Polo Lisa Branca", "Polo Lisa Marrom"]
UNIDADES_BICOLOR = ["Polo Bicolor Preto/Branco", "Polo Bicolor Marrom/Branco",
                    "Polo Bicolor Branco/Marrom", "Polo Bicolor Branco/Preto"]
TODAS_UNIDADES   = UNIDADES_LISA + UNIDADES_BICOLOR

# Termos que IDENTIFICAM bicolor (abreviados/compostos)
BICOLOR_MAP = {
    "Pret":              "Polo Bicolor Preto/Branco",
    "Marro":             "Polo Bicolor Marrom/Branco",
    "Bco Marro":         "Polo Bicolor Branco/Marrom",
    "Bco Marrom":        "Polo Bicolor Branco/Marrom",
    "Bco Pret":          "Polo Bicolor Branco/Preto",
    "Bco Preto":         "Polo Bicolor Branco/Preto",
    "Branco (com Marrom)": "Polo Bicolor Branco/Marrom",
    "Branco (com Preto)":  "Polo Bicolor Branco/Preto",
}

# Quando contexto já é bicolor, Preto/Marrom/Branco extenso = variante principal
BICOLOR_CONTEXTO_MAP = {
    "Preto":  "Polo Bicolor Preto/Branco",
    "Marrom": "Polo Bicolor Marrom/Branco",
    "Branco": "Polo Bicolor Branco/Marrom",
}

# Mapa lisa: só usado quando NENHUM termo bicolor encontrado
LISA_MAP = {
    "Preto":  "Polo Lisa Preta",
    "Branco": "Polo Lisa Branca",
    "Marrom": "Polo Lisa Marrom",
}

# =========================
# PERSISTÊNCIA JSON LOCAL
# =========================
DIR_BASE      = os.path.dirname(os.path.abspath(__file__))
CUSTOS_FILE   = os.path.join(DIR_BASE, "shopee_custos.json")
ESTOQUE_FILE  = os.path.join(DIR_BASE, "shopee_estoque.json")
REGIME_FILE   = os.path.join(DIR_BASE, "shopee_regime.json")

def load_json(path: str, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Erro ao salvar {os.path.basename(path)}: {e}")

def parse_variacao(variacao: str) -> list[str]:
    """
    Dado o campo 'Nome da variação', retorna lista de unidades de estoque a baixar.
    Ex: 'Pret+Marro+Bco Marro+Bco Pret,Único' → 4 unidades bicolor
    Ex: 'Preto + Branco,Único' → 1 Lisa Preta + 1 Lisa Branca
    Ex: 'Preto,Único' → 1 Lisa Preta
    """
    if not variacao or pd.isna(variacao):
        return []

    # Remove sufixo ',Único' ou similar
    variacao = str(variacao).split(",")[0].strip()

    # Separa pelos '+'
    termos = [t.strip() for t in variacao.split("+")]

    # Decide se é bicolor: se qualquer termo bate no BICOLOR_MAP
    is_bicolor = any(t in BICOLOR_MAP for t in termos)

    resultado = []
    if is_bicolor:
        for t in termos:
            # Primeiro tenta mapa bicolor, depois contexto bicolor (Preto/Marrom extenso)
            unidade = BICOLOR_MAP.get(t) or BICOLOR_CONTEXTO_MAP.get(t)
            if unidade:
                resultado.append(unidade)
    else:
        for t in termos:
            unidade = LISA_MAP.get(t)
            if unidade:
                resultado.append(unidade)

    return resultado

def calcular_consumo(df: pd.DataFrame) -> dict:
    """
    Processa todas as vendas aprovadas e retorna dict {unidade: qtd_consumida}.
    """
    consumo = {u: 0 for u in TODAS_UNIDADES}
    aprovados = df[~df["Cancelado"]] if "Cancelado" in df.columns else df
    for _, row in aprovados.iterrows():
        unidades = parse_variacao(row.get("Nome da variação", ""))
        for u in unidades:
            if u in consumo:
                consumo[u] += 1
    return consumo


def produto_key(nome: str) -> str:
    palavras = str(nome).strip().split()
    return " ".join(palavras[:5])

def parse_planilha(arquivo):
    try:
        df = pd.read_excel(arquivo)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None
    faltando = [c for c in COLUNAS_NECESSARIAS if c not in df.columns]
    if faltando:
        st.error(f"Colunas não encontradas: {faltando}")
        return None
    if df.empty:
        st.warning("Nenhum pedido encontrado.")
        return None
    STATUS_EXCLUIR = ["Cancelado", "Não pago"]
    df["Cancelado"]   = df["Status do pedido"].isin(STATUS_EXCLUIR)
    df["Data"]        = pd.to_datetime(df["Data de criação do pedido"], errors="coerce")
    df["produto_key"] = df["Nome do Produto"].apply(produto_key)
    for col in ["Subtotal do produto","Preço acordado","Quantidade",
                "Taxa de comissão líquida","Taxa de serviço líquida","Desconto do vendedor"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["Receita Bruta"]  = df["Subtotal do produto"]
    # Dividir taxas proporcionalmente pelo nº de linhas do pedido
    linhas_por_pedido    = df.groupby("ID do pedido")["ID do pedido"].transform("count")
    df["Comissao"]       = df["Taxa de comissão líquida"] / linhas_por_pedido
    df["Taxa Servico"]   = df["Taxa de serviço líquida"]  / linhas_por_pedido
    df["Taxas Shopee"]   = df["Comissao"] + df["Taxa Servico"]
    df["Frete Vendedor"] = 0.0
    # Manter Nome da variação no df
    if "Nome da variação" not in df.columns:
        df["Nome da variação"] = ""
    return df[["ID do pedido","Data","Nome do Produto","produto_key","Nome da variação","Quantidade",
               "Receita Bruta","Comissao","Taxa Servico","Taxas Shopee","Frete Vendedor","Cancelado"]]

def custo_da_variacao(variacao: str) -> float:
    """Calcula custo total da venda somando custo/peça × qtd de cada unidade identificada."""
    unidades = parse_variacao(variacao)
    custos = st.session_state.get("custos", {})
    return sum(custos.get(u, 0.0) for u in unidades)

def apply_costs(df):
    df = df.copy()
    aliquota = st.session_state["aliquota"] / 100
    df["Custo Total"]    = df.apply(
        lambda r: 0.0 if r["Cancelado"] else custo_da_variacao(r.get("Nome da variação", "")), axis=1)
    df["Imposto"]        = df.apply(
        lambda r: 0.0 if r["Cancelado"] else r["Receita Bruta"] * aliquota, axis=1)
    df["Lucro"]          = df.apply(
        lambda r: 0.0 if r["Cancelado"] else (
            r["Receita Bruta"] - r["Taxas Shopee"] - r["Custo Total"] - r["Imposto"]), axis=1)
    df["Margem %"]       = df.apply(
        lambda r: 0.0 if r["Cancelado"] else (
            r["Lucro"] / r["Receita Bruta"] * 100 if r["Receita Bruta"] > 0 else 0.0), axis=1)
    return df

def metric_card(col, title, value, sub, color):
    col.markdown(
        f'<div class="metric-card" style="--accent:{color};">'
        f'<div class="metric-title">{title}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-pill">{sub}</div></div>',
        unsafe_allow_html=True)

def kpi_card(col, title, value, color="#1F2937"):
    col.markdown(
        f'<div class="kpi-card"><div class="kpi-title">{title}</div>'
        f'<div class="kpi-value" style="color:{color};">{value}</div></div>',
        unsafe_allow_html=True)

def pct(valor, total):
    return f"{valor/total*100:.1f}%" if total else "0%"

def badge(valor, total, bg, txt):
    p = abs(valor / total * 100) if total else 0
    return (f'<span style="font-weight:700;">R$ {valor:,.2f}</span> '
            f'<span style="background:{bg};color:{txt};border-radius:999px;'
            f'padding:2px 7px;font-size:11px;font-weight:800;">{p:.0f}%</span>')

def margem_badge(pct_val, lucro=None):
    bg  = "#DCFCE7" if pct_val >= 15 else "#FEF9C3" if pct_val >= 8 else "#FEE2E2"
    txt = "#15803D" if pct_val >= 15 else "#854D0E" if pct_val >= 8 else "#DC2626"
    l   = f'<span style="font-weight:700;color:{txt};">R$ {lucro:,.2f}</span> ' if lucro is not None else ""
    return (f'{l}<span style="background:{bg};color:{txt};border-radius:999px;'
            f'padding:2px 9px;font-size:12px;font-weight:800;">{pct_val:.1f}%</span>')

# =========================
# ESTADO DE SESSÃO
# =========================
if "aba" not in st.session_state:
    st.session_state["aba"] = "financeiro"
if "df" not in st.session_state:
    st.session_state["df"] = None
if "custos_detalhado" not in st.session_state:
    st.session_state["custos_detalhado"] = load_json(CUSTOS_FILE, {})
if "custos" not in st.session_state:
    st.session_state["custos"] = {
        u: v["custo_unitario"] + v.get("embalagem", 0) + v.get("outros", 0)
        for u, v in st.session_state["custos_detalhado"].items()
    }
_regime_raw = load_json(REGIME_FILE, {"aliquota": 0.0, "regime": "Simples Nacional"})
if "aliquota" not in st.session_state:
    st.session_state["aliquota"] = float(_regime_raw.get("aliquota", 0.0))
if "regime_nome" not in st.session_state:
    st.session_state["regime_nome"] = _regime_raw.get("regime", "Simples Nacional")
if "estoque" not in st.session_state:
    _estoque_raw = load_json(ESTOQUE_FILE, {})
    st.session_state["estoque"] = {u: int(_estoque_raw.get(u, 0)) for u in TODAS_UNIDADES}

# =========================
# NAVEGAÇÃO
# =========================
nav = st.columns([2, 2, 2, 2, 2])
for col, (aba_id, label) in zip(nav, [
    ("financeiro", "📊 Financeiro"),
    ("estoque",    "📦 Estoque"),
    ("custos",     "💰 Custos"),
    ("regime",     "🏛️ Regime"),
    ("debug",      "🔍 Debug Variação"),
]):
    with col:
        if st.button(label, use_container_width=True,
                     type="primary" if st.session_state["aba"] == aba_id else "secondary"):
            st.session_state["aba"] = aba_id
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# ABA: FINANCEIRO
# ══════════════════════════════════════════
if st.session_state["aba"] == "financeiro":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**📂 Upload da Planilha de Vendas (Shopee)**")
    st.caption("Exporte em Seller Center → Meus Pedidos → Exportar.")
    col_up, col_btn = st.columns([4, 1])
    with col_up:
        arquivo = st.file_uploader("Planilha .xlsx", type=["xlsx"], label_visibility="collapsed")
    with col_btn:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state["df"] = None
            st.rerun()
    if arquivo:
        with st.spinner("Processando…"):
            df_raw = parse_planilha(arquivo)
        if df_raw is not None:
            st.session_state["df"] = df_raw
            st.success(f"✅ {len(df_raw)} pedidos carregados ({len(df_raw[~df_raw['Cancelado']])} aprovados).")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["df"] is None:
        st.markdown(
            '<div style="background:#FFF5F0;border:2px dashed #EE4D2D;border-radius:16px;'
            'padding:48px;text-align:center;color:#CC0001;font-weight:700;font-size:18px;">'
            '🛍️ Faça o upload da planilha para visualizar o dashboard</div>',
            unsafe_allow_html=True)
        st.stop()

    df = apply_costs(st.session_state["df"])

    # ── Filtro de período ──
    from datetime import date as _date
    _dmin = df["Data"].min().date() if pd.notna(df["Data"].min()) else _date.today()
    _dmax = df["Data"].max().date() if pd.notna(df["Data"].max()) else _date.today()

    st.markdown('<div class="card" style="padding:16px 24px;margin-bottom:12px;">', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns([2, 2, 1])
    with fc1:
        data_ini = st.date_input("📅 Data inicial", value=_dmin, min_value=_dmin, max_value=_dmax, key="fi_ini")
    with fc2:
        data_fim = st.date_input("📅 Data final",   value=_dmax, min_value=_dmin, max_value=_dmax, key="fi_fim")
    with fc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺ Resetar período", use_container_width=True):
            st.session_state["fi_ini"] = _dmin
            st.session_state["fi_fim"] = _dmax
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # Aplica filtro
    mask = (df["Data"].dt.date >= data_ini) & (df["Data"].dt.date <= data_fim)
    df   = df[mask]

    aprovados  = df[~df["Cancelado"]]
    cancelados = df[df["Cancelado"]]

    faturamento  = aprovados["Receita Bruta"].sum()
    comissao     = aprovados["Comissao"].sum()
    taxa_serv    = aprovados["Taxa Servico"].sum()
    taxas_total  = aprovados["Taxas Shopee"].sum()
    custos_prod  = aprovados["Custo Total"].sum()
    impostos     = aprovados["Imposto"].sum()
    lucro_total  = aprovados["Lucro"].sum()
    margem_real  = lucro_total / faturamento * 100 if faturamento else 0
    ticket       = faturamento / len(aprovados) if len(aprovados) else 0
    lucro_venda  = lucro_total / len(aprovados) if len(aprovados) else 0
    qtd_vendas   = int(aprovados["Quantidade"].sum())
    n_cancelados    = len(cancelados)
    fat_cancelados  = cancelados["Receita Bruta"].sum()

    data_min = aprovados["Data"].min()
    data_max = aprovados["Data"].max()
    label_per = (f"{data_min.strftime('%d/%m/%Y')} – {data_max.strftime('%d/%m/%Y')}"
                 if pd.notna(data_min) else "–")

    # HERO
    st.markdown(f"""
    <div class="hero">
      <div style="display:flex;justify-content:space-between;gap:30px;align-items:flex-start;flex-wrap:wrap;">
        <div>
          <p class="hero-small">🛍️ Shopee BR</p>
          <h1 class="hero-title">Financeiro</h1>
          <div style="background:rgba(255,255,255,.18);color:white;border:1px solid rgba(255,255,255,.35);
                      border-radius:999px;padding:10px 16px;font-weight:900;width:fit-content;">
            {label_per} &nbsp;•&nbsp; {len(aprovados)} pedidos &nbsp;•&nbsp; {qtd_vendas} unidades
          </div>
        </div>
        <div style="min-width:260px;">
          <div class="hero-value-label">Faturamento</div>
          <div class="hero-value">R$ {faturamento:,.2f}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    metric_card(c1, "Comissão",     f"R$ {comissao:,.2f}",       pct(comissao,  faturamento),    "#FBBF24")
    metric_card(c2, "Taxa Serviço", f"R$ {taxa_serv:,.2f}",      pct(taxa_serv, faturamento),    "#F97316")
    metric_card(c3, "Frete",        "R$ 0,00",                   "incluso nas taxas",             "#94A3B8")
    metric_card(c4, "Custos",       f"R$ {custos_prod:,.2f}",    pct(custos_prod, faturamento),  "#8B5CF6")
    metric_card(c5, "Cancelados",   f"R$ {fat_cancelados:,.2f}", f"{n_cancelados} pedidos",      "#EF4444")

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(f"""<div class="metric-card" style="--accent:#E5E7EB;min-height:138px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-size:22px;font-weight:900;color:#020617;margin-bottom:12px;">Ticket Médio</div>
                    <div class="muted">Por pedido</div>
                    <div style="font-size:24px;font-weight:900;color:#020617;">R$ {ticket:,.2f}</div>
                </div>
                <div>
                    <div class="muted">Lucro por pedido</div>
                    <div style="font-size:24px;font-weight:900;color:#020617;">R$ {lucro_venda:,.2f}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with right:
        box = "green-box" if lucro_total >= 0 else "red-box"
        st.markdown(f"""<div class="{box}">
            <div class="green-title">Lucro Líquido Real</div>
            <div class="green-value">R$ {lucro_total:,.2f}</div>
            <div class="green-sub">Margem real: {margem_real:.2f}%</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    kpi_card(k1, "Receita Bruta",  f"R$ {faturamento:,.2f}")
    kpi_card(k2, "Taxas Shopee",   f"R$ {taxas_total:,.2f}",  "#EF4444")
    kpi_card(k3, "Frete Vendedor", "R$ 0,00",                  "#94A3B8")
    k4, k5, k6 = st.columns(3)
    kpi_card(k4, "Custo Produto",  f"R$ {custos_prod:,.2f}",  "#EF4444")
    kpi_card(k5, "Lucro Real",     f"R$ {lucro_total:,.2f}",  "#059669" if lucro_total >= 0 else "#DC2626")
    kpi_card(k6, "Margem",         f"{margem_real:.2f}%",      "#B45309")

    if custos_prod == 0:
        st.info("💡 Cadastre os custos na aba **💰 Custos** para ver lucro e margem reais.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos diários
    daily = aprovados.copy()
    daily["Dia"] = pd.to_datetime(daily["Data"]).dt.date
    daily_agg = daily.groupby("Dia").agg(
        Lucro=("Lucro","sum"), Receita=("Receita Bruta","sum"), Quantidade=("Quantidade","sum")
    ).reset_index()
    daily_agg["Dia"]    = pd.to_datetime(daily_agg["Dia"])
    media_lucro         = daily_agg["Lucro"].mean()
    daily_agg["Cor"]    = daily_agg["Lucro"].apply(lambda x: "Acima" if x >= media_lucro else "Abaixo")
    daily_agg["Margem"] = (daily_agg["Lucro"] / daily_agg["Receita"].replace(0,1) * 100).round(1)

    prod_daily = aprovados.copy()
    prod_daily["Dia"] = pd.to_datetime(prod_daily["Data"]).dt.date
    prod_agg = prod_daily.groupby(["Dia","produto_key"]).agg(
        Quantidade=("Quantidade","sum"), Receita=("Receita Bruta","sum"), Lucro=("Lucro","sum")
    ).reset_index()
    prod_agg["Dia"]    = pd.to_datetime(prod_agg["Dia"])
    prod_agg["Margem"] = (prod_agg["Lucro"] / prod_agg["Receita"].replace(0,1) * 100).round(1)
    prods   = prod_agg["produto_key"].unique().tolist()
    cores   = ["#EE4D2D","#0EA5E9","#F59E0B","#16A34A","#8B5CF6","#EC4899"]
    cor_map = {p: cores[i % len(cores)] for i, p in enumerate(prods)}
    media_prod = prod_agg.groupby("produto_key")["Quantidade"].mean().reset_index().rename(columns={"Quantidade":"Media"})

    gc1, gc2 = st.columns(2)
    with gc1:
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown("**Resumo de Vendas**")
        st.markdown(f'<div style="color:#64748B;font-size:13px;margin-bottom:16px;">{label_per}</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            taxas_pct = taxas_total / faturamento * 100 if faturamento else 0
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:12px;font-weight:700;color:#EE4D2D;">Pedidos</div>
                <div style="font-size:36px;font-weight:900;color:#0F172A;line-height:1.1;">{len(aprovados)}</div>
                <div style="font-size:12px;color:#64748B;">{qtd_vendas} unidades</div>
            </div>
            <div>
                <div style="font-size:12px;font-weight:700;color:#EE4D2D;">Ticket médio</div>
                <div style="font-size:28px;font-weight:900;color:#0F172A;line-height:1.1;">R$ {ticket:,.2f}</div>
                <div style="font-size:12px;color:#64748B;">lucro/pedido R$ {lucro_venda:,.2f}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <div style="font-size:12px;font-weight:700;color:#F97316;">Taxas Shopee</div>
                <div style="font-size:36px;font-weight:900;color:#0F172A;line-height:1.1;">R$ {taxas_total:,.2f}</div>
                <div style="font-size:12px;color:#64748B;">{taxas_pct:.1f}% da receita</div>
            </div>
            <div>
                <div style="font-size:12px;font-weight:700;color:#16A34A;">Receita</div>
                <div style="font-size:28px;font-weight:900;color:#0F172A;line-height:1.1;">R$ {faturamento:,.2f}</div>
                <div style="font-size:12px;color:#EE4D2D;font-weight:700;">margem {margem_real:.2f}%</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if len(daily_agg) > 1:
            mini = alt.Chart(daily_agg).mark_area(
                interpolate="monotone",
                color=alt.Gradient(gradient="linear",
                    stops=[alt.GradientStop(color="#EE4D2D55", offset=0),
                           alt.GradientStop(color="#EE4D2D00", offset=1)],
                    x1=1, x2=1, y1=1, y2=0),
                line={"color":"#EE4D2D","strokeWidth":3}
            ).encode(
                x=alt.X("Dia:T", title=None, axis=alt.Axis(format="%d/%m", labelFontSize=10)),
                y=alt.Y("Receita:Q", title=None),
                tooltip=[alt.Tooltip("Dia:T", format="%d/%m/%Y", title="Data"),
                         alt.Tooltip("Receita:Q", format=",.2f", title="Receita")]
            ).properties(height=230)
            st.altair_chart(mini, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with gc2:
        import plotly.graph_objects as go
        st.markdown('<div class="card" style="height:100%;">', unsafe_allow_html=True)
        st.markdown("**Quantidade vendida por produto**")
        st.markdown(f'<div style="color:#64748B;font-size:13px;margin-bottom:16px;">Por produto/dia — {label_per} — clique na legenda para mostrar/ocultar</div>', unsafe_allow_html=True)
        if len(prod_agg) > 1:
            fig_q = go.Figure()
            for prod in prods:
                d = prod_agg[prod_agg["produto_key"] == prod].sort_values("Dia")
                media_v = media_prod[media_prod["produto_key"] == prod]["Media"].values
                media_v = float(media_v[0]) if len(media_v) > 0 else 0
                cor = cor_map.get(prod, "#666")
                nome_leg = prod[:35] + f" (média {media_v:.1f}/dia)"
                # Área
                fig_q.add_trace(go.Scatter(
                    x=d["Dia"], y=d["Quantidade"],
                    mode="lines+markers",
                    name=nome_leg,
                    line=dict(color=cor, width=2),
                    marker=dict(color=cor, size=7),
                    fill="tozeroy",
                    fillcolor=cor,
                    opacity=0.85,
                    customdata=list(zip(d["Receita"].round(2), d["Lucro"].round(2), d["Margem"].round(1))),
                    hovertemplate=(
                        "<b>%{x|%d/%m/%Y}</b><br>"
                        f"Produto: {prod[:40]}<br>"
                        "Qtd: %{y}<br>"
                        "Receita: R$ %{customdata[0]:,.2f}<br>"
                        "Lucro: R$ %{customdata[1]:,.2f}<br>"
                        "Margem: %{customdata[2]:.1f}%<extra></extra>"
                    ),
                    legendgroup=prod,
                ))
                # Linha de média
                if len(d) > 0:
                    fig_q.add_trace(go.Scatter(
                        x=[d["Dia"].min(), d["Dia"].max()],
                        y=[media_v, media_v],
                        mode="lines",
                        name=f"Média {prod[:20]}",
                        line=dict(color=cor, width=1.5, dash="dot"),
                        opacity=0.5,
                        showlegend=False,
                        legendgroup=prod,
                        hoverinfo="skip",
                    ))
            fig_q.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.25,
                    xanchor="left",
                    x=0,
                    font=dict(size=11),
                    itemclick="toggle",
                    itemdoubleclick="toggleothers",
                ),
                xaxis=dict(showgrid=False, tickformat="%d/%m"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Qtd"),
                hovermode="closest",
            )
            st.plotly_chart(fig_q, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Gráfico disponível com 2+ dias de dados.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Lucro por dia
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Lucro real por dia (R$)</div><br>', unsafe_allow_html=True)
    if len(daily_agg) > 1:
        area_l  = alt.Chart(daily_agg).mark_area(interpolate="monotone",
            color=alt.Gradient(gradient="linear",
                stops=[alt.GradientStop(color="#16A34A44", offset=0),
                       alt.GradientStop(color="#16A34A00", offset=1)],
                x1=1, x2=1, y1=1, y2=0)
        ).encode(x=alt.X("Dia:T", title=None), y=alt.Y("Lucro:Q", title=None))
        linha_l = alt.Chart(daily_agg).mark_line(interpolate="monotone", color="#16A34A", strokeWidth=3
        ).encode(x="Dia:T", y="Lucro:Q")
        pontos_l = alt.Chart(daily_agg).mark_point(filled=True, size=80).encode(
            x=alt.X("Dia:T", title=None), y=alt.Y("Lucro:Q", title=None),
            color=alt.Color("Cor:N", scale=alt.Scale(domain=["Acima","Abaixo"],
                range=["#16A34A","#EF4444"]), legend=alt.Legend(title="vs Média", orient="top-right")),
            tooltip=[alt.Tooltip("Dia:T", title="Data", format="%d/%m/%Y"),
                     alt.Tooltip("Lucro:Q", title="Lucro R$", format=",.2f"),
                     alt.Tooltip("Receita:Q", title="Receita R$", format=",.2f"),
                     alt.Tooltip("Quantidade:Q", title="Qtd"),
                     alt.Tooltip("Margem:Q", title="Margem %", format=".1f")])
        media_rule = alt.Chart(pd.DataFrame({"media":[media_lucro]})).mark_rule(
            color="#94A3B8", strokeDash=[6,4], strokeWidth=1.5
        ).encode(y="media:Q", tooltip=[alt.Tooltip("media:Q", title="Média R$", format=",.2f")])
        media_text = alt.Chart(pd.DataFrame({"media":[media_lucro],"Dia":[daily_agg["Dia"].max()]}
        )).mark_text(align="right", dy=-8, fontSize=11, fontWeight=700, color="#64748B"
        ).encode(x="Dia:T", y="media:Q", text=alt.value(f"Média: R$ {media_lucro:,.0f}"))
        st.altair_chart((area_l + linha_l + pontos_l + media_rule + media_text).properties(height=300),
                        use_container_width=True)
    else:
        st.info("Gráfico disponível com 2+ dias de dados.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Margem por produto
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Margem ponderada por produto</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="muted">Faturamento, participação e margem — {label_per}</div><br>', unsafe_allow_html=True)
    sku_pond = aprovados.groupby("produto_key").agg(
        Vendas=("Data","count"), Unidades=("Quantidade","sum"),
        Receita=("Receita Bruta","sum"), Lucro=("Lucro","sum")
    ).reset_index()
    sku_pond["Margem %"]       = (sku_pond["Lucro"] / sku_pond["Receita"].replace(0,1) * 100).round(2)
    sku_pond["Participação %"] = (sku_pond["Receita"] / sku_pond["Receita"].sum() * 100).round(1)
    sku_pond = sku_pond.sort_values("Receita", ascending=False).reset_index(drop=True)
    for _, sr in sku_pond.iterrows():
        cor_m = "#16A34A" if sr["Margem %"] >= 15 else "#B45309" if sr["Margem %"] >= 8 else "#DC2626"
        bar_w = min(int(sr["Participação %"] * 3), 100)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:12px 0;border-bottom:1px solid #F1F5F9;">
            <div style="min-width:200px;font-weight:700;color:#EE4D2D;font-size:13px;">{sr['produto_key'][:40]}</div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-weight:700;color:#0F172A;">R$ {sr['Receita']:,.2f}</span>
                    <span style="color:#64748B;font-size:13px;">{sr['Participação %']:.1f}%</span>
                </div>
                <div style="background:#F1F5F9;border-radius:999px;height:6px;">
                    <div style="background:#EE4D2D;width:{bar_w}%;height:6px;border-radius:999px;"></div>
                </div>
            </div>
            <div style="min-width:80px;text-align:center;">
                <div style="font-size:12px;color:#64748B;font-weight:600;">Ped / Un</div>
                <div style="font-weight:800;color:#0F172A;">{int(sr['Vendas'])} / {int(sr['Unidades'])}</div>
            </div>
            <div style="min-width:90px;text-align:right;">
                <div style="font-size:12px;color:#64748B;font-weight:600;">Lucro</div>
                <div style="font-weight:800;color:{cor_m};">R$ {sr['Lucro']:,.2f}</div>
            </div>
            <div style="min-width:70px;text-align:right;">
                <span style="background:{'#DCFCE7' if sr['Margem %']>=15 else '#FEF9C3' if sr['Margem %']>=8 else '#FEE2E2'};
                             color:{cor_m};border-radius:999px;padding:4px 12px;font-size:14px;font-weight:900;">
                    {sr['Margem %']:.2f}%</span>
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Tabela detalhada
    st.markdown('<div class="card">', unsafe_allow_html=True)
    fat_total = faturamento or 1
    linhas = ""
    for _, row in df.sort_values(["Cancelado","Data"], ascending=[True,False]).iterrows():
        rec       = row["Receita Bruta"]
        cancelado = row["Cancelado"]
        bg_row    = "background:#FFF5F5;" if cancelado else ""
        pedido_id = str(row.get('ID do pedido', ''))
        linhas += f"""<tr style="border-bottom:1px solid #F1F5F9;{bg_row}">
            <td style="padding:10px 8px;color:#94A3B8;font-size:10px;white-space:nowrap;font-family:monospace;">{pedido_id}</td>
            <td style="padding:10px 8px;font-weight:700;color:#EE4D2D;font-size:12px;">{row['produto_key'][:30]}</td>
            <td style="padding:10px 8px;color:#94A3B8;font-size:11px;">{str(row.get('Nome da variação',''))[:25]}</td>
            <td style="padding:10px 8px;color:#64748B;font-size:12px;white-space:nowrap;">
                {pd.to_datetime(row['Data']).strftime('%d/%m/%Y') if pd.notna(row['Data']) else '–'}</td>
            <td style="padding:10px 8px;text-align:center;font-weight:700;">{int(row['Quantidade'])}</td>
            <td style="padding:10px 8px;">{'–' if cancelado else badge(rec, fat_total,'#DCFCE7','#15803D')}</td>
            <td style="padding:10px 8px;">{'–' if cancelado else badge(row['Comissao'], rec,'#FEF3C7','#B45309')}</td>
            <td style="padding:10px 8px;">{'–' if cancelado else badge(row['Taxa Servico'], rec,'#FFEDD5','#C2410C')}</td>
            <td style="padding:10px 8px;color:#94A3B8;font-weight:600;">R$ 0,00</td>
            <td style="padding:10px 8px;">{'–' if cancelado else badge(row['Custo Total'], rec,'#EDE9FE','#6D28D9')}</td>
            <td style="padding:10px 8px;">{'–' if cancelado else badge(row['Imposto'], rec,'#F1F5F9','#475569')}</td>
            <td style="padding:10px 8px;text-align:center;">{'<span style="color:#DC2626;font-weight:800;">Cancelado</span>' if cancelado else margem_badge(row.get('Margem %',0), row.get('Lucro',0))}</td>
        </tr>"""
    tabela = f"""<div style="overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;font-family:'Inter',sans-serif;font-size:13px;">
        <thead><tr style="background:#FFF5F0;border-bottom:2px solid #FDDCCC;">
            <th style="padding:10px 8px;text-align:left;color:#64748B;font-size:11px;font-weight:800;text-transform:uppercase;">ID Pedido</th>
            <th style="padding:10px 8px;text-align:left;color:#CC0001;font-size:11px;font-weight:800;text-transform:uppercase;">Produto</th>
            <th style="padding:10px 8px;text-align:left;color:#64748B;font-size:11px;font-weight:800;text-transform:uppercase;">Variação</th>
            <th style="padding:10px 8px;text-align:left;color:#64748B;font-size:11px;font-weight:800;text-transform:uppercase;">Data</th>
            <th style="padding:10px 8px;text-align:center;color:#64748B;font-size:11px;font-weight:800;text-transform:uppercase;">Qtd</th>
            <th style="padding:10px 8px;text-align:left;color:#16A34A;font-size:11px;font-weight:800;text-transform:uppercase;">Receita</th>
            <th style="padding:10px 8px;text-align:left;color:#B45309;font-size:11px;font-weight:800;text-transform:uppercase;">Comissão (−)</th>
            <th style="padding:10px 8px;text-align:left;color:#C2410C;font-size:11px;font-weight:800;text-transform:uppercase;">Taxa Serv. (−)</th>
            <th style="padding:10px 8px;text-align:left;color:#94A3B8;font-size:11px;font-weight:800;text-transform:uppercase;">Frete (−)</th>
            <th style="padding:10px 8px;text-align:left;color:#6D28D9;font-size:11px;font-weight:800;text-transform:uppercase;">Custo (−)</th>
            <th style="padding:10px 8px;text-align:left;color:#475569;font-size:11px;font-weight:800;text-transform:uppercase;">Imposto (−)</th>
            <th style="padding:10px 8px;text-align:center;color:#64748B;font-size:11px;font-weight:800;text-transform:uppercase;">Margem (=)</th>
        </tr></thead>
        <tbody>{linhas}</tbody>
    </table></div>"""
    with st.expander(f"🧾 Ver pedidos detalhados ({len(aprovados)} aprovados + {n_cancelados} cancelados)", expanded=False):
        st.markdown(tabela, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ABA: ESTOQUE
# ══════════════════════════════════════════
elif st.session_state["aba"] == "estoque":

    df_raw = st.session_state.get("df")
    consumo = calcular_consumo(df_raw) if df_raw is not None else {u: 0 for u in TODAS_UNIDADES}

    st.markdown("""<div class="hero" style="min-height:auto;padding:28px 38px;">
        <h1 class="hero-title">Gestão de Estoque</h1>
        <div style="opacity:.85;font-size:15px;margin-top:8px;">
            Cadastre a quantidade inicial de cada unidade — o consumo é calculado automaticamente pelas vendas da planilha
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Cadastro de estoque inicial ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**⚙️ Quantidade inicial em estoque**")
    st.caption("Informe quantas unidades você tinha no início do período da planilha carregada.")

    col_lisa, col_bicolor = st.columns(2)

    with col_lisa:
        st.markdown("**👕 Polo Lisa**")
        for u in UNIDADES_LISA:
            cor_label = u.replace("Polo Lisa ", "")
            val = st.number_input(
                cor_label, min_value=0, step=1,
                value=st.session_state["estoque"].get(u, 0),
                key=f"est_{u}"
            )
            st.session_state["estoque"][u] = val

    with col_bicolor:
        st.markdown("**🎨 Polo Bicolor**")
        for u in UNIDADES_BICOLOR:
            cor_label = u.replace("Polo Bicolor ", "")
            val = st.number_input(
                cor_label, min_value=0, step=1,
                value=st.session_state["estoque"].get(u, 0),
                key=f"est_{u}"
            )
            st.session_state["estoque"][u] = val

    if st.button("💾 Salvar estoque", type="primary", use_container_width=True):
        save_json(ESTOQUE_FILE, dict(st.session_state["estoque"]))
        st.success("✅ Estoque salvo em shopee_estoque.json")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabela de saldo ──
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Posição do Estoque</div>', unsafe_allow_html=True)
    if df_raw is None:
        st.info("Carregue a planilha na aba 📊 Financeiro para ver o consumo calculado.")
    else:
        st.caption(f"Consumo calculado sobre {len(df_raw[~df_raw['Cancelado']])} pedidos aprovados.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Seção Lisa
    st.markdown("**👕 Polo Lisa**")
    for u in UNIDADES_LISA:
        inicial  = st.session_state["estoque"].get(u, 0)
        vendidas = consumo.get(u, 0)
        saldo    = inicial - vendidas
        pct_cons = (vendidas / inicial * 100) if inicial > 0 else 0
        cor_saldo = "#16A34A" if saldo > 50 else "#B45309" if saldo > 20 else "#DC2626"
        bar_cons  = min(int(pct_cons), 100)
        nome_cur  = u.replace("Polo Lisa ", "")

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:20px;padding:14px 0;border-bottom:1px solid #F1F5F9;">
            <div style="min-width:140px;font-weight:800;color:#0F172A;">{nome_cur}</div>
            <div style="min-width:90px;text-align:center;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Cadastrado</div>
                <div style="font-size:22px;font-weight:900;color:#0F172A;">{inicial}</div>
            </div>
            <div style="min-width:90px;text-align:center;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Vendidas</div>
                <div style="font-size:22px;font-weight:900;color:#EE4D2D;">{vendidas}</div>
            </div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:12px;color:#64748B;">consumo</span>
                    <span style="font-size:12px;font-weight:700;color:#EE4D2D;">{pct_cons:.0f}%</span>
                </div>
                <div style="background:#F1F5F9;border-radius:999px;height:8px;">
                    <div style="background:#EE4D2D;width:{bar_cons}%;height:8px;border-radius:999px;
                                transition:width .3s;"></div>
                </div>
            </div>
            <div style="min-width:100px;text-align:right;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Saldo</div>
                <div style="font-size:28px;font-weight:900;color:{cor_saldo};">{saldo}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🎨 Polo Bicolor**")
    for u in UNIDADES_BICOLOR:
        inicial  = st.session_state["estoque"].get(u, 0)
        vendidas = consumo.get(u, 0)
        saldo    = inicial - vendidas
        pct_cons = (vendidas / inicial * 100) if inicial > 0 else 0
        cor_saldo = "#16A34A" if saldo > 50 else "#B45309" if saldo > 20 else "#DC2626"
        bar_cons  = min(int(pct_cons), 100)
        nome_cur  = u.replace("Polo Bicolor ", "")

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:20px;padding:14px 0;border-bottom:1px solid #F1F5F9;">
            <div style="min-width:140px;font-weight:800;color:#0F172A;">{nome_cur}</div>
            <div style="min-width:90px;text-align:center;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Cadastrado</div>
                <div style="font-size:22px;font-weight:900;color:#0F172A;">{inicial}</div>
            </div>
            <div style="min-width:90px;text-align:center;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Vendidas</div>
                <div style="font-size:22px;font-weight:900;color:#EE4D2D;">{vendidas}</div>
            </div>
            <div style="flex:1;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:12px;color:#64748B;">consumo</span>
                    <span style="font-size:12px;font-weight:700;color:#EE4D2D;">{pct_cons:.0f}%</span>
                </div>
                <div style="background:#F1F5F9;border-radius:999px;height:8px;">
                    <div style="background:#8B5CF6;width:{bar_cons}%;height:8px;border-radius:999px;"></div>
                </div>
            </div>
            <div style="min-width:100px;text-align:right;">
                <div style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase;">Saldo</div>
                <div style="font-size:28px;font-weight:900;color:{cor_saldo};">{saldo}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ABA: DEBUG VARIAÇÃO
# ══════════════════════════════════════════
elif st.session_state["aba"] == "debug":
    st.markdown("""<div class="hero" style="min-height:auto;padding:28px 38px;">
        <h1 class="hero-title">Debug de Variações</h1>
        <div style="opacity:.85;font-size:15px;margin-top:8px;">
            Verifique como cada variação está sendo interpretada pelo algoritmo
        </div>
    </div>""", unsafe_allow_html=True)

    df_raw = st.session_state.get("df")
    if df_raw is None:
        st.info("Carregue a planilha primeiro na aba 📊 Financeiro.")
    else:
        aprovados = df_raw[~df_raw["Cancelado"]]
        rows = []
        for _, row in aprovados.iterrows():
            var = str(row.get("Nome da variação", ""))
            unidades = parse_variacao(var)
            tipo = "Bicolor" if any(u in UNIDADES_BICOLOR for u in unidades) else "Lisa" if unidades else "❓ Não identificado"
            rows.append({
                "Produto": row["produto_key"][:35],
                "Variação original": var[:40],
                "Tipo": tipo,
                "Unidades baixadas": " + ".join([u.replace("Polo ","") for u in unidades]) if unidades else "— nenhuma —",
            })
        debug_df = pd.DataFrame(rows)

        # Mostrar não identificados primeiro
        nao_id = debug_df[debug_df["Tipo"] == "❓ Não identificado"]
        if not nao_id.empty:
            st.warning(f"⚠️ {len(nao_id)} vendas com variação não identificada — revise o BICOLOR_MAP ou LISA_MAP.")
            st.dataframe(nao_id, use_container_width=True, hide_index=True)
            st.markdown("---")

        st.markdown(f"**{len(debug_df)} vendas aprovadas**")
        st.dataframe(debug_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════
# ABA: CUSTOS
# ══════════════════════════════════════════
elif st.session_state["aba"] == "custos":
    st.markdown("""<div class="hero" style="min-height:auto;padding:28px 38px;">
        <h1 class="hero-title">Cadastro de Custos</h1>
        <div style="opacity:.85;font-size:15px;margin-top:8px;">
            Custo por peça unitária — o sistema calcula automaticamente nas vendas (kit 2 = 2×, kit 3 = 3×)
        </div>
    </div>""", unsafe_allow_html=True)

    # Custos armazenados por unidade base: {unidade: {custo_unitario, embalagem, outros, margem_alvo}}
    if "custos_detalhado" not in st.session_state:
        st.session_state["custos_detalhado"] = {}

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**➕ Cadastrar / atualizar custo de unidade base**")
    with st.form("form_custo", clear_on_submit=True):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            unidade_sel = st.selectbox("Unidade base", TODAS_UNIDADES)
        with fc2:
            custo_unit  = st.number_input("Custo unitário (R$)", min_value=0.0, step=0.01, format="%.4f")
            embalagem   = st.number_input("Embalagem (R$)",       min_value=0.0, step=0.01, format="%.2f")
        with fc3:
            outros      = st.number_input("Outros custos (R$)",   min_value=0.0, step=0.01, format="%.2f")
            margem_alvo = st.number_input("Margem alvo (%)",      min_value=0.0, step=0.1,  format="%.1f")
        obs = st.text_input("Observação", placeholder="opcional")
        if st.form_submit_button("💾 Salvar", type="primary", use_container_width=True):
            st.session_state["custos_detalhado"][unidade_sel] = {
                "custo_unitario": custo_unit,
                "embalagem":      embalagem,
                "outros":         outros,
                "margem_alvo":    margem_alvo,
                "observacao":     obs,
            }
            # Atualiza o dict simples usado no apply_costs (custo total por peça)
            st.session_state["custos"][unidade_sel] = custo_unit + embalagem + outros
            # Persiste no JSON
            save_json(CUSTOS_FILE, st.session_state["custos_detalhado"])
            st.success(f"✅ {unidade_sel} → custo total R$ {custo_unit+embalagem+outros:.4f}/peça")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state["custos_detalhado"]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**📋 Custos cadastrados por unidade base**")
        st.caption("O custo total por peça (unitário + embalagem + outros) é multiplicado pela quantidade de peças identificada na variação de cada venda.")

        for unidade, vals in st.session_state["custos_detalhado"].items():
            custo_total = vals["custo_unitario"] + vals["embalagem"] + vals["outros"]
            tipo_tag = "👕 Lisa" if "Lisa" in unidade else "🎨 Bicolor"
            c1, c2, c3, c4, c5, c6 = st.columns([3, 1.5, 1.2, 1.2, 1.2, 0.6])
            with c1:
                st.markdown(
                    f'<div style="padding:8px 0;font-weight:700;color:#EE4D2D;">{unidade}</div>'
                    f'<div style="font-size:11px;color:#94A3B8;">{tipo_tag}</div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div style="padding:8px 0;font-size:13px;color:#64748B;font-weight:600;">Custo total/peça</div>'
                    f'<div style="font-weight:900;color:#0F172A;">R$ {custo_total:.4f}</div>',
                    unsafe_allow_html=True)
            with c3:
                st.markdown(
                    f'<div style="padding:8px 0;font-size:12px;color:#64748B;">Unitário</div>'
                    f'<div style="font-weight:700;">R$ {vals["custo_unitario"]:.4f}</div>',
                    unsafe_allow_html=True)
            with c4:
                st.markdown(
                    f'<div style="padding:8px 0;font-size:12px;color:#64748B;">Embalagem</div>'
                    f'<div style="font-weight:700;">R$ {vals["embalagem"]:.2f}</div>',
                    unsafe_allow_html=True)
            with c5:
                st.markdown(
                    f'<div style="padding:8px 0;font-size:12px;color:#64748B;">Margem alvo</div>'
                    f'<div style="font-weight:700;">{vals["margem_alvo"]:.1f}%</div>',
                    unsafe_allow_html=True)
            with c6:
                if st.button("🗑️", key=f"del_{unidade}"):
                    del st.session_state["custos_detalhado"][unidade]
                    st.session_state["custos"].pop(unidade, None)
                    save_json(CUSTOS_FILE, st.session_state["custos_detalhado"])
                    st.rerun()
            st.markdown("<hr style='border:none;border-top:1px solid #F1F5F9;margin:0;'>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Info: como o custo é aplicado nas vendas
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**ℹ️ Como o custo é calculado nas vendas**")
        st.markdown("""
O sistema lê o campo **Variação** de cada pedido aprovado e identifica quantas peças de cada unidade foram vendidas:

- `Preto, Único` → 1 × Polo Lisa Preta
- `Preto + Branco, Único` → 1 × Polo Lisa Preta + 1 × Polo Lisa Branca
- `Preto + Marrom + Branco, Único` → 3 peças (1 de cada)
- `Pret+Marro+Bco Marro+Bco Pret, Único` → 4 peças bicolor

O **Custo Total** da venda = soma de (custo/peça × quantidade) para cada unidade identificada.
        """)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum custo cadastrado ainda. Use o formulário acima para cadastrar o custo de cada peça.")


# ══════════════════════════════════════════
# ABA: REGIME
# ══════════════════════════════════════════
elif st.session_state["aba"] == "regime":
    st.markdown("""<div class="hero" style="min-height:auto;padding:28px 38px;">
        <h1 class="hero-title">Regime Tributário</h1>
        <div style="opacity:.85;font-size:15px;margin-top:8px;">
            Alíquota aplicada sobre a receita bruta de cada pedido
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("**⚙️ Configurar alíquota**")
    regime = st.selectbox("Regime", ["Simples Nacional","Lucro Presumido","Lucro Real","MEI","Isento"])
    nova = st.number_input("Alíquota (%)", min_value=0.0, max_value=100.0,
                           value=st.session_state["aliquota"], step=0.01, format="%.2f")
    if st.button("💾 Aplicar", type="primary"):
        st.session_state["aliquota"]    = nova
        st.session_state["regime_nome"] = regime
        save_json(REGIME_FILE, {"aliquota": nova, "regime": regime})
        st.success(f"✅ {regime} — {nova:.2f}% aplicado.")
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    al = st.session_state["aliquota"]
    cor_al = "#16A34A" if al == 0 else "#B45309" if al <= 6 else "#EF4444"
    st.markdown(f"""<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:16px;
                    padding:24px;text-align:center;">
        <div style="font-size:13px;font-weight:700;color:#64748B;text-transform:uppercase;margin-bottom:8px;">
            Alíquota atual</div>
        <div style="font-size:48px;font-weight:900;color:{cor_al};">{al:.2f}%</div>
        <div style="font-size:13px;color:#64748B;margin-top:4px;">{regime}</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
