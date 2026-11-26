# [IA] Gemini – Dashboard interativo em Streamlit com estetica de maquina Pokedex Gen 4 (Sinnoh), sidebar retratil, controles D-Pad e gamificacao (XP, badges, captura e quiz de clusters K-Means)
import os
import time
import random
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score, confusion_matrix

# ==========================================
# 1. Configuracao da Pagina (Sidebar Retratil)
# ==========================================
st.set_page_config(
    page_title="Sinnoh Dex — Pokedex Analytics AVD 2026.2",
    page_icon="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

TYPE_COLORS = {
    "Normal": "#A8A77A", "Fire": "#EE8130", "Water": "#6390F0", "Electric": "#F7D02C",
    "Grass": "#7AC74C", "Ice": "#96D9D6", "Fighting": "#C22E28", "Poison": "#A33EA1",
    "Ground": "#E2BF65", "Flying": "#A98FF3", "Psychic": "#F95587", "Bug": "#A6B91A",
    "Rock": "#B6A136", "Ghost": "#735797", "Dragon": "#6F35FC", "Dark": "#705746",
    "Steel": "#B7B7CE", "Fairy": "#D685AD", "None": "#CBD5E1"
}

CLUSTER_PALETTE = ["#2563EB", "#059669", "#D97706", "#DC0A2D", "#7C3AED", "#0891B2", "#DB2777", "#475569"]

# ==========================================
# 2. Estado de Gamificacao e Navegacao Pokedex
# ==========================================
if "trainer_xp" not in st.session_state:
    st.session_state["trainer_xp"] = 20
if "seen_ids" not in st.session_state:
    st.session_state["seen_ids"] = {6}
if "caught_ids" not in st.session_state:
    st.session_state["caught_ids"] = set()
if "tested_ks" not in st.session_state:
    st.session_state["tested_ks"] = {4}
if "quiz_streak" not in st.session_state:
    st.session_state["quiz_streak"] = 0
if "quiz_hits" not in st.session_state:
    st.session_state["quiz_hits"] = 0
if "quiz_total" not in st.session_state:
    st.session_state["quiz_total"] = 0
if "dex_cursor" not in st.session_state:
    st.session_state["dex_cursor"] = 5  # Charizard (#006)
if "quiz_pkm_id" not in st.session_state:
    st.session_state["quiz_pkm_id"] = None
if "quiz_feedback" not in st.session_state:
    st.session_state["quiz_feedback"] = None


def get_trainer_rank(xp):
    if xp < 100:
        return "Lv.1 Pesquisador Novato", xp, 100
    if xp < 250:
        return "Lv.2 Analista de Sinnoh", xp - 100, 150
    if xp < 500:
        return "Lv.3 Mestre de Clusters", xp - 250, 250
    return "Lv.4 Campeao de Dados", 100, 100


# ==========================================
# 3. CSS Customizado (Hardware Pokedex Gen 4 + Controles Fisicos)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Press+Start+2P&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Chakra Petch', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Fundo LCD Sinnoh com grade tecnica */
    .stApp {
        background-color: #E4EBF2;
        background-image:
            linear-gradient(to right, rgba(30, 41, 59, 0.065) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(30, 41, 59, 0.065) 1px, transparent 1px);
        background-size: 22px 22px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1.8rem;
    }

    /* Botao retratil da sidebar estilizado como alavanca fisica da Pokedex */
    [data-testid="collapsedControl"] {
        background: #CC1E2C !important;
        border: 2.5px solid #1E293B !important;
        border-radius: 0 12px 12px 0 !important;
        box-shadow: 0 3px 0 #1E293B !important;
        color: #FFCB05 !important;
        top: 0.7rem !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #FFCB05 !important;
        stroke: #FFCB05 !important;
    }

    /* Sidebar como Carcaca Vermelha Retratil da Pokedex */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #CC1E2C 0%, #A51320 100%) !important;
        border-right: 4px solid #1E293B !important;
        box-shadow: inset -6px 0 0 rgba(0, 0, 0, 0.16);
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.28) !important;
    }

    /* Animacoes */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pokeballWobble {
        0%, 100% { transform: translateX(0) rotate(0deg); }
        20% { transform: translateX(-9px) rotate(-20deg); }
        40% { transform: translateX(9px) rotate(20deg); }
        60% { transform: translateX(-6px) rotate(-12deg); }
        80% { transform: translateX(4px) rotate(6deg); }
    }
    @keyframes buttonBlink {
        0%, 100% { background: #FFFFFF; box-shadow: 0 0 6px rgba(255,255,255,0.8); }
        50% { background: #FF3B30; box-shadow: 0 0 18px #FF3B30; }
    }
    @keyframes ledPulse {
        0%, 100% { opacity: 1; box-shadow: 0 0 10px #22C55E; }
        50% { opacity: 0.45; box-shadow: 0 0 3px #22C55E; }
    }
    @keyframes scanLine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(260%); }
    }
    @keyframes holoShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Loading Estilo Caixa de Dialogo Nintendo DS */
    .poke-loader-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 38px 24px;
        background: #F8FAFC;
        border-radius: 14px;
        border: 4px solid #1E293B;
        box-shadow: inset 0 0 0 4px #CBD5E1, 0 8px 0 #1E293B;
        margin: 18px 0;
        color: #1E293B;
    }
    .css-pokeball {
        width: 66px; height: 66px;
        border-radius: 50%;
        background: linear-gradient(to bottom, #DC0A2D 47%, #1E293B 47%, #1E293B 54%, #FFFFFF 54%);
        border: 4px solid #1E293B;
        position: relative;
        box-shadow: 0 6px 0 rgba(30, 41, 59, 0.22);
        animation: pokeballWobble 1.05s ease-in-out infinite;
    }
    .css-pokeball::after {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        width: 18px; height: 18px;
        border-radius: 50%;
        border: 4px solid #1E293B;
        transform: translate(-50%, -50%);
        animation: buttonBlink 1.05s ease-in-out infinite;
    }
    .loader-title {
        font-family: 'Press Start 2P', monospace;
        margin-top: 20px;
        font-size: 0.82rem;
        line-height: 1.5;
        color: #CC1E2C;
        text-align: center;
    }
    .loader-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #475569;
        margin-top: 8px;
        text-align: center;
    }

    /* Chassi Superior da Maquina Pokedex */
    .pokedex-shell-top {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, #DC1E2E 0%, #B71422 100%);
        padding: 16px 22px;
        border-radius: 16px 16px 8px 8px;
        border: 3px solid #1E293B;
        box-shadow: 0 6px 0 #1E293B, inset 0 3px 0 rgba(255,255,255,0.22);
        color: #FFFFFF;
        margin-bottom: 14px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        animation: fadeSlideUp 0.35s ease-out;
    }
    .pokedex-shell-top::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 32%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.13), transparent);
        animation: scanLine 5s ease-in-out infinite;
        pointer-events: none;
    }
    .lens-outer {
        width: 56px; height: 56px;
        border-radius: 50%;
        background: #F8FAFC;
        border: 3px solid #1E293B;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.9);
        flex-shrink: 0;
    }
    .lens-inner {
        width: 42px; height: 42px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #E0F2FE, #0EA5E9 58%, #0369A1);
        border: 2px solid #0C4A6E;
    }
    .shell-title {
        font-family: 'Press Start 2P', monospace;
        margin: 0;
        font-size: 1rem;
        line-height: 1.4;
        color: #FFFFFF;
        text-shadow: 2px 2px 0 #1E293B;
    }
    .shell-sub {
        margin: 5px 0 0 0;
        font-size: 0.86rem;
        color: #FEF3C7;
        font-weight: 600;
    }

    /* HUD de Gamificacao do Treinador embutido no Chassi */
    .trainer-hud {
        background: #0F172A;
        border: 2px solid #1E293B;
        border-radius: 12px;
        padding: 10px 14px;
        min-width: 265px;
        z-index: 2;
        box-shadow: inset 0 2px 6px rgba(0,0,0,0.5);
    }
    .hud-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #E2E8F0;
    }
    .xp-track {
        width: 100%;
        height: 8px;
        background: #334155;
        border-radius: 999px;
        overflow: hidden;
        margin: 6px 0;
    }
    .xp-fill {
        height: 100%;
        background: linear-gradient(90deg, #FACC15, #22C55E);
        border-radius: 999px;
        transition: width 0.5s ease;
    }
    .badge-chip {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 5px;
        font-size: 0.66rem;
        font-weight: 700;
        margin-right: 4px;
        border: 1px solid rgba(255,255,255,0.2);
    }

    /* Barra Inferior de Hardware Fisico (D-Pad + Botoes A/B + Alto-falante) */
    .pokedex-hardware-bar {
        background: linear-gradient(180deg, #B71422 0%, #99101C 100%);
        border: 3px solid #1E293B;
        border-radius: 10px 10px 18px 18px;
        padding: 12px 22px;
        margin-top: 22px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: #FFFFFF;
        box-shadow: 0 5px 0 #1E293B;
    }
    .dpad-mini {
        width: 44px; height: 44px;
        position: relative;
    }
    .dpad-h {
        position: absolute; top: 14px; left: 0;
        width: 44px; height: 16px;
        background: #1E293B; border-radius: 4px;
        box-shadow: 0 3px 0 #0F172A;
    }
    .dpad-v {
        position: absolute; top: 0; left: 14px;
        width: 16px; height: 44px;
        background: #1E293B; border-radius: 4px;
        box-shadow: 0 3px 0 #0F172A;
    }
    .ab-buttons {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    .ab-btn {
        width: 32px; height: 32px;
        border-radius: 50%;
        background: #1E293B;
        color: #FFCB05;
        font-family: 'Press Start 2P', monospace;
        font-size: 0.65rem;
        display: flex; align-items: center; justify-content: center;
        border: 2px solid #0F172A;
        box-shadow: 0 3px 0 #0F172A;
    }
    .speaker-grill {
        display: flex;
        gap: 5px;
    }
    .speaker-slot {
        width: 5px; height: 22px;
        background: #1E293B;
        border-radius: 3px;
        transform: rotate(15deg);
    }
    .battery-led {
        width: 10px; height: 10px;
        border-radius: 50%;
        background: #22C55E;
        display: inline-block;
        animation: ledPulse 2s ease-in-out infinite;
        margin-right: 6px;
    }

    /* Abas estilo Botoes Fisicos DS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1E293B;
        padding: 8px;
        border-radius: 14px;
        border: 2px solid #0F172A;
        box-shadow: 0 4px 0 #0F172A;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 15px;
        font-weight: 700;
        font-size: 0.86rem;
        background: #334155;
        color: #E2E8F0;
        border: 2px solid #0F172A;
        transition: all 0.15s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #475569;
        color: #FFFFFF;
    }
    .stTabs [aria-selected="true"] {
        background: #FFCB05 !important;
        color: #1E293B !important;
        border: 2px solid #1E293B !important;
        box-shadow: inset 0 -3px 0 rgba(0,0,0,0.18);
    }

    /* Botoes do Streamlit estilo Cartucho */
    .stButton > button {
        border: 2px solid #1E293B !important;
        border-radius: 10px !important;
        box-shadow: 0 3px 0 #1E293B !important;
        font-weight: 700 !important;
        transition: transform 0.1s ease, box-shadow 0.1s ease !important;
    }
    .stButton > button:active {
        transform: translateY(2px) !important;
        box-shadow: 0 1px 0 #1E293B !important;
    }

    /* KPI Cards & Cluster Cards */
    .kpi-card, .cluster-card {
        background: #FFFFFF;
        border: 2px solid #1E293B;
        border-radius: 12px;
        padding: 12px 14px;
        box-shadow: 0 4px 0 #1E293B;
        transition: transform 0.15s ease;
        animation: fadeSlideUp 0.4s ease-out;
    }
    .kpi-card:hover, .cluster-card:hover {
        transform: translateY(-2px);
    }
    .kpi-label {
        font-family: 'Press Start 2P', monospace;
        font-size: 0.55rem;
        line-height: 1.4;
        color: #64748B;
        text-transform: uppercase;
    }
    .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.4rem;
        font-weight: 700;
        color: #111827;
        margin-top: 6px;
    }

    /* Badges de Tipo */
    .type-badge {
        display: inline-block;
        padding: 3px 11px;
        border-radius: 6px;
        border: 1.5px solid #1E293B;
        box-shadow: 0 2px 0 #1E293B;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: #FFFFFF;
        text-shadow: 1px 1px 0 rgba(0,0,0,0.45);
        margin-right: 6px;
    }

    /* Cartao de Batalha Sinnoh */
    .battle-card {
        border-radius: 14px;
        padding: 18px;
        color: #111827;
        border: 3px solid #1E293B;
        box-shadow: 0 6px 0 #1E293B;
        position: relative;
        overflow: hidden;
        animation: fadeSlideUp 0.35s ease-out;
    }
    .battle-card-holo {
        background: linear-gradient(135deg, #FFFBEB, #FDE68A, #FEF3C7, #FCD34D);
        background-size: 300% 300%;
        animation: holoShimmer 4.5s ease infinite, fadeSlideUp 0.35s ease-out;
        border: 3px solid #B45309;
        box-shadow: 0 6px 0 #78350F;
    }

    /* Barras de Stats estilo Showdown */
    .stat-row {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
    }
    .stat-name { width: 64px; font-weight: 700; color: #475569; text-align: right; }
    .stat-num { width: 34px; font-weight: 700; color: #111827; text-align: right; }
    .stat-track { flex: 1; height: 10px; background: rgba(15, 23, 42, 0.1); border-radius: 999px; overflow: hidden; }
    .stat-fill { height: 100%; border-radius: 999px; transition: width 0.55s ease; }

    .autoral-note {
        background: #FFFFFF;
        border-left: 5px solid #CC1E2C;
        border-top: 2px solid #1E293B;
        border-right: 2px solid #1E293B;
        border-bottom: 2px solid #1E293B;
        padding: 12px 16px;
        border-radius: 10px;
        font-size: 0.88rem;
        color: #1E293B;
        margin: 8px 0 16px 0;
        box-shadow: 0 3px 0 #1E293B;
    }

    /* Arena de Captura Animada Estilo Nintendo DS (Gen 4) */
    @keyframes ballDropArc {
        0% { transform: translate(-110px, -95px) scale(0.55) rotate(-220deg); opacity: 0.2; }
        65% { transform: translate(0px, -18px) scale(1.1) rotate(35deg); opacity: 1; }
        85% { transform: translate(0px, 4px) scale(0.94) rotate(0deg); }
        100% { transform: translate(0px, 0px) scale(1) rotate(0deg); }
    }
    @keyframes pkmAbsorb {
        0% { transform: scale(1); filter: brightness(1); opacity: 1; }
        35% { transform: scale(1.12); filter: brightness(2.5) sepia(1) hue-rotate(-50deg) saturate(6); opacity: 0.95; }
        100% { transform: scale(0.05) translateY(-10px); filter: brightness(4) sepia(1) hue-rotate(-50deg) saturate(8); opacity: 0; }
    }
    @keyframes captureShake3 {
        0%, 100% { transform: rotate(0deg) translateX(0); }
        12% { transform: rotate(-24deg) translateX(-10px); }
        24% { transform: rotate(22deg) translateX(10px); }
        34% { transform: rotate(0deg) translateX(0); }
        52% { transform: rotate(-22deg) translateX(-9px); }
        64% { transform: rotate(20deg) translateX(9px); }
        74% { transform: rotate(0deg) translateX(0); }
        88% { transform: rotate(-16deg) translateX(-6px); }
    }
    @keyframes starPopLeft {
        0% { transform: translate(0, 0) scale(0.2) rotate(0deg); opacity: 0; }
        40% { opacity: 1; }
        100% { transform: translate(-62px, -48px) scale(1.25) rotate(-60deg); opacity: 0; }
    }
    @keyframes starPopCenter {
        0% { transform: translate(0, 0) scale(0.2) rotate(0deg); opacity: 0; }
        40% { opacity: 1; }
        100% { transform: translate(0px, -68px) scale(1.35) rotate(45deg); opacity: 0; }
    }
    @keyframes starPopRight {
        0% { transform: translate(0, 0) scale(0.2) rotate(0deg); opacity: 0; }
        40% { opacity: 1; }
        100% { transform: translate(62px, -48px) scale(1.25) rotate(60deg); opacity: 0; }
    }
    .capture-stage {
        position: relative;
        overflow: hidden;
        height: 230px;
        border-radius: 14px;
        border: 4px solid #1E293B;
        box-shadow: inset 0 0 0 3px #CBD5E1, 0 8px 0 #1E293B;
        background: linear-gradient(180deg, #7DD3FC 0%, #BAE6FD 54%, #4ADE80 54%, #22C55E 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 14px 0;
    }
    .capture-ground-oval {
        position: absolute;
        bottom: 42px;
        width: 170px;
        height: 36px;
        border-radius: 50%;
        background: rgba(21, 128, 61, 0.38);
        border: 3px solid rgba(255, 255, 255, 0.35);
    }
    .capture-dialog {
        position: absolute;
        bottom: 8px;
        left: 12px;
        right: 12px;
        background: #F8FAFC;
        border: 3px solid #1E293B;
        border-radius: 8px;
        padding: 7px 14px;
        font-family: 'Press Start 2P', monospace;
        font-size: 0.68rem;
        color: #1E293B;
        text-align: center;
        box-shadow: inset 0 0 0 2px #CBD5E1;
    }
    .star-fx {
        position: absolute;
        font-size: 1.55rem;
        color: #FACC15;
        text-shadow: 0 2px 0 #92400E, 0 0 12px #FEF08A;
        pointer-events: none;
    }

    /* PC Box Sinnoh (Estilo Armazenamento da Bebe em Diamond/Pearl) */
    .pcbox-header {
        background: linear-gradient(90deg, #0284C7 0%, #0EA5E9 100%);
        border: 3px solid #1E293B;
        border-radius: 12px;
        padding: 12px 18px;
        color: #FFFFFF;
        box-shadow: 0 4px 0 #1E293B;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .pcbox-slot {
        background-color: #F0FDF4;
        background-image:
            linear-gradient(to right, rgba(16, 185, 129, 0.12) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(16, 185, 129, 0.12) 1px, transparent 1px);
        background-size: 16px 16px;
        border: 2.5px solid #1E293B;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 4px 0 #1E293B;
        margin-bottom: 10px;
        transition: transform 0.15s ease;
    }
    .pcbox-slot:hover {
        transform: translateY(-3px);
    }
</style>
""", unsafe_allow_html=True)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def render_type_badge(type_name):
    color = TYPE_COLORS.get(type_name, "#64748B")
    return f'<span class="type-badge" style="background-color:{color};">{type_name}</span>'


def stat_bar_color(val):
    if val < 55:
        return "#EF4444"
    if val < 85:
        return "#F97316"
    if val < 105:
        return "#EAB308"
    if val < 130:
        return "#22C55E"
    return "#06B6D4"


def render_showdown_stats(pkm_row):
    stats_map = [
        ("HP", int(pkm_row["hp"])),
        ("ATK", int(pkm_row["attack"])),
        ("DEF", int(pkm_row["defense"])),
        ("SP.A", int(pkm_row["sp_attack"])),
        ("SP.D", int(pkm_row["sp_defense"])),
        ("SPD", int(pkm_row["speed"])),
    ]
    rows_html = ""
    for label, val in stats_map:
        pct = min(100, round(val / 200 * 100, 1))
        cor = stat_bar_color(val)
        rows_html += (
            f'<div class="stat-row">'
            f'<div class="stat-name">{label}</div>'
            f'<div class="stat-num">{val}</div>'
            f'<div class="stat-track"><div class="stat-fill" style="width:{pct}%;background:{cor};"></div></div>'
            f'</div>'
        )
    return rows_html


def style_plotly(fig, height=420, y_zero=False, show_zeroline=False):
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Chakra Petch, sans-serif", color="#0F172A", size=12),
        title=dict(font=dict(size=15, color="#0F172A"), x=0.02, xanchor="left"),
        margin=dict(l=68, r=28, t=58, b=52),
        height=height,
        hoverlabel=dict(bgcolor="#0F172A", font_color="#FFFFFF", font_size=12)
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E2E8F0",
        gridwidth=1,
        showline=True,
        linecolor="#64748B",
        linewidth=1.5,
        ticks="outside",
        ticklen=5,
        tickcolor="#64748B",
        tickfont=dict(size=11.5, color="#1E293B"),
        title_font=dict(size=13, color="#0F172A"),
        title_standoff=10,
        automargin=True,
        zeroline=show_zeroline,
        zerolinecolor="#94A3B8",
        zerolinewidth=1.2
    )
    y_kwargs = dict(
        showgrid=True,
        gridcolor="#E2E8F0",
        gridwidth=1,
        showline=True,
        linecolor="#64748B",
        linewidth=1.5,
        ticks="outside",
        ticklen=5,
        tickcolor="#64748B",
        tickfont=dict(size=11.5, color="#1E293B"),
        title_font=dict(size=13, color="#0F172A"),
        title_standoff=12,
        automargin=True,
        zeroline=show_zeroline,
        zerolinecolor="#94A3B8",
        zerolinewidth=1.2
    )
    if y_zero:
        y_kwargs["rangemode"] = "tozero"
    fig.update_yaxes(**y_kwargs)
    return fig


def show_pokeball_loader(title_text, subtitle_text, duration=0.8):
    placeholder = st.empty()
    placeholder.markdown(
        f'<div class="poke-loader-wrap">'
        f'<div class="css-pokeball"></div>'
        f'<div class="loader-title">{title_text}</div>'
        f'<div class="loader-sub">{subtitle_text}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    time.sleep(duration)
    placeholder.empty()


def show_capture_animation(pkm_name, dex_id, is_legendary=False):
    ball_label = "Master Ball" if is_legendary else "Pokebola"
    show_pokeball_loader(
        f"CAPTURANDO {pkm_name.upper()}...",
        f"{ball_label} arremessada! Registrando #{dex_id:03d} no seu PC Box...",
        duration=0.85
    )


# ==========================================
# 4. Boot Inicial Estilo Maquina Pokedex
# ==========================================
if "sinnoh_booted" not in st.session_state:
    show_pokeball_loader(
        "SINNOH DEX MODELO DP-04",
        "Ligando scanner... Carregando 801 especies da PokeAPI e K-Means",
        duration=1.0
    )
    st.session_state["sinnoh_booted"] = True


# ==========================================
# 5. Carregamento dos Dados
# ==========================================
# [IA] Gemini – Carregamento cacheado e limpeza basica do dataset Pokemon
@st.cache_data
def load_pokemon_data():
    possible_paths = [
        os.path.join(ROOT_DIR, "data", "parte_especifica", "pokemon.csv"),
        os.path.join("data", "parte_especifica", "pokemon.csv"),
        "pokemon.csv"
    ]
    filepath = next((p for p in possible_paths if os.path.exists(p)), None)
    if filepath is None:
        st.error("Arquivo `pokemon.csv` nao encontrado em `data/parte_especifica/`.")
        st.stop()

    df = pd.read_csv(filepath)
    df["type1"] = df["type1"].fillna("None").str.capitalize()
    df["type2"] = df["type2"].fillna("None").str.capitalize()
    df["is_legendary"] = df["is_legendary"].astype(int)
    df["generation"] = df["generation"].astype(int)
    df["status_lendario"] = df["is_legendary"].map({0: "Comum", 1: "Lendario"})
    # [IA] Claude (Antigravity) – altura/peso NAO sao imputados (ausencia ligada a formas de Alola/alternativas,
    # ver secao 3.1 do notebook). Ficam como NaN; a correlacao usa exclusao par a par e o K-Means nao usa essas colunas.
    df["height_m"] = pd.to_numeric(df["height_m"], errors="coerce")
    df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce")
    return df


# [IA] Gemini – Carregamento cacheado dos dados e CSVs oficiais da Parte Comum (Wine Quality)
@st.cache_data
def load_wine_data():
    wine_path = os.path.join(ROOT_DIR, "data", "parte_comum", "winequality-red.csv")
    if not os.path.exists(wine_path):
        return None, None, None, None

    with open(wine_path, "r", encoding="utf-8") as f:
        sep = ";" if ";" in f.readline() else ","
    df_wine = pd.read_csv(wine_path, sep=sep)

    out_comum = os.path.join(ROOT_DIR, "out", "parte_comum")
    comp_path = os.path.join(out_comum, "comparacao_passadas.csv")
    m5_path = os.path.join(out_comum, "metricas_k5.csv")
    m6_path = os.path.join(out_comum, "metricas_k6.csv")

    df_comp = pd.read_csv(comp_path) if os.path.exists(comp_path) else None
    df_m5 = pd.read_csv(m5_path) if os.path.exists(m5_path) else None
    df_m6 = pd.read_csv(m6_path) if os.path.exists(m6_path) else None
    return df_wine, df_comp, df_m5, df_m6


# ==========================================
# 6. Sidebar Retratil (Painel de Hardware da Pokedex)
# ==========================================
with st.sidebar:
    col_l1, col_l2 = st.columns([1, 3])
    with col_l1:
        st.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/master-ball.png", width=46)
    with col_l2:
        st.markdown("### SINNOH DEX\n**Painel Retratil • AVD**")

    pagina_ativa = st.radio(
        "Cartucho / Modulo:",
        options=[
            "Parte Especifica — Pokemon",
            "Parte Comum — Wine Quality"
        ]
    )
    st.markdown("---")


# ==============================================================================
# MODULO 1: PARTE ESPECIFICA — POKEMON
# ==============================================================================
if pagina_ativa == "Parte Especifica — Pokemon":
    df_raw = load_pokemon_data()

    with st.sidebar:
        st.markdown("#### Filtros da Pokedex")
        todas_geracoes = sorted(df_raw["generation"].unique())
        geracoes_sel = st.multiselect("Geracoes (1 a 7):", options=todas_geracoes, default=todas_geracoes)

        todos_tipos = sorted([t for t in df_raw["type1"].unique() if t != "None"])
        tipos_sel = st.multiselect("Tipos Primarios:", options=todos_tipos, default=todos_tipos)

        filtro_lendario = st.radio("Categoria:", options=["Todos", "Apenas Lendarios", "Apenas Comuns"])

        st.markdown("---")
        st.markdown("#### Motor K-Means")
        atributos_disp = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "base_total"]
        features_sel = st.multiselect(
            "Variaveis de Agrupamento:",
            options=atributos_disp,
            default=["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        )
        k_clusters = st.slider("Numero de Clusters (k):", min_value=2, max_value=8, value=4, step=1)
        random_state = st.number_input("Random State:", min_value=0, max_value=999, value=42)

    # Gamificacao: testar novos valores de k da XP
    if k_clusters not in st.session_state["tested_ks"]:
        st.session_state["tested_ks"].add(k_clusters)
        st.session_state["trainer_xp"] += 25
        show_pokeball_loader(
            f"RECALIBRANDO K-MEANS (k = {k_clusters})",
            "+25 XP de Pesquisa! Atualizando centroides e espaco PCA 2D...",
            duration=0.55
        )
        st.toast(f"Novo valor k = {k_clusters} explorado! +25 XP", icon="⚡")

    df_filt = df_raw[
        (df_raw["generation"].isin(geracoes_sel)) &
        (df_raw["type1"].isin(tipos_sel))
    ].copy()

    if filtro_lendario == "Apenas Lendarios":
        df_filt = df_filt[df_filt["is_legendary"] == 1]
    elif filtro_lendario == "Apenas Comuns":
        df_filt = df_filt[df_filt["is_legendary"] == 0]

    if df_filt.empty or len(features_sel) < 2:
        st.warning("Ajuste os filtros na barra lateral retratil (seta no canto superior esquerdo).")
        st.stop()

    # [IA] Gemini – Padronizacao, K-Means, ordenacao de clusters, metricas e PCA 2D
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_filt[features_sel])

    kmeans = KMeans(n_clusters=k_clusters, random_state=int(random_state), n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    df_clust = df_filt.copy()
    df_clust["Cluster_Num"] = labels
    ordem_clusters = df_clust.groupby("Cluster_Num")["base_total"].mean().sort_values().index.tolist()
    mapa_ordem = {old_c: idx for idx, old_c in enumerate(ordem_clusters)}
    df_clust["Cluster_Num"] = df_clust["Cluster_Num"].map(mapa_ordem)
    df_clust["Cluster"] = df_clust["Cluster_Num"].apply(lambda c: f"Cluster {c}")

    sil_score = silhouette_score(X_scaled, df_clust["Cluster_Num"]) if len(np.unique(labels)) > 1 else 0.0
    db_score = davies_bouldin_score(X_scaled, df_clust["Cluster_Num"]) if len(np.unique(labels)) > 1 else 0.0

    pca_2d = PCA(n_components=2, random_state=int(random_state))
    coords_2d = pca_2d.fit_transform(X_scaled)
    df_clust["PCA1"] = coords_2d[:, 0]
    df_clust["PCA2"] = coords_2d[:, 1]

    # Badges desbloqueaveis de gamificacao
    rank_name, xp_cur, xp_max = get_trainer_rank(st.session_state["trainer_xp"])
    xp_pct = min(100, int((xp_cur / xp_max) * 100))
    badges_html = ""
    if len(st.session_state["seen_ids"]) >= 3:
        badges_html += '<span class="badge-chip" style="background:#2563EB;color:#FFF;">Scanner</span>'
    if len(st.session_state["caught_ids"]) >= 1:
        badges_html += '<span class="badge-chip" style="background:#DC0A2D;color:#FFF;">Capturador</span>'
    if len(st.session_state["tested_ks"]) >= 2:
        badges_html += '<span class="badge-chip" style="background:#059669;color:#FFF;">K-Explorer</span>'
    if st.session_state["quiz_hits"] >= 1:
        badges_html += '<span class="badge-chip" style="background:#D97706;color:#FFF;">Mestre Quiz</span>'
    if not badges_html:
        badges_html = '<span style="font-size:0.68rem;color:#94A3B8;">Explore a Dex e o Desafio para ganhar insignias!</span>'

    # Banner Superior da Maquina Pokedex + HUD de Treinador
    st.markdown(f"""
    <div class="pokedex-shell-top">
        <div style="display:flex;align-items:center;gap:16px;z-index:2;">
            <div class="lens-outer"><div class="lens-inner"></div></div>
            <div>
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
                    <span style="width:11px;height:11px;border-radius:50%;background:#FF3B30;border:2px solid #1E293B;display:inline-block;"></span>
                    <span style="width:11px;height:11px;border-radius:50%;background:#FFCB05;border:2px solid #1E293B;display:inline-block;"></span>
                    <span style="width:11px;height:11px;border-radius:50%;background:#22C55E;border:2px solid #1E293B;display:inline-block;"></span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#FEF3C7;margin-left:6px;">SINNOH DEX DP-04 • Abra a barra retratil (◀) para filtros</span>
                </div>
                <h1 class="shell-title">POKEDEX ANALYTICS</h1>
                <p class="shell-sub">{len(df_clust)} especies ativas • K-Means (k = {k_clusters}) • Silhouette {sil_score:.3f}</p>
            </div>
        </div>
        <div class="trainer-hud">
            <div class="hud-row">
                <span style="color:#FFCB05;font-weight:700;">{rank_name}</span>
                <span>{st.session_state["trainer_xp"]} XP</span>
            </div>
            <div class="xp-track"><div class="xp-fill" style="width:{xp_pct}%;"></div></div>
            <div class="hud-row" style="margin-bottom:5px;">
                <span>Vistos: <b>{len(st.session_state["seen_ids"])}</b></span>
                <span>Capturados: <b>{len(st.session_state["caught_ids"])}</b></span>
                <span>Streak: <b>{st.session_state["quiz_streak"]}</b></span>
            </div>
            <div>{badges_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs LCD
    k1, k2, k3, k4, k5 = st.columns(5)
    for col_k, label_k, val_k, color_k in [
        (k1, "Pokemons Ativos", f"{len(df_clust)}", "#DC0A2D"),
        (k2, "Base Total Media", f"{df_clust['base_total'].mean():.1f}", "#2563EB"),
        (k3, "Lendarios", f"{int(df_clust['is_legendary'].sum())} ({df_clust['is_legendary'].mean()*100:.1f}%)", "#D97706"),
        (k4, "Silhouette Score", f"{sil_score:.3f}", "#059669"),
        (k5, "Davies-Bouldin", f"{db_score:.3f}", "#1B263B"),
    ]:
        col_k.markdown(
            f'<div class="kpi-card" style="border-top:4px solid {color_k};">'
            f'<div class="kpi-label">{label_k}</div>'
            f'<div class="kpi-value">{val_k}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    qtd_cap = len(st.session_state["caught_ids"])
    tab_dex, tab_pcbox, tab_quiz, tab_km, tab_exp, tab_story, tab_tab = st.tabs([
        "Maquina Pokedex",
        f"PC Box ({qtd_cap})",
        "Desafio K-Means",
        "Clusters K-Means",
        "Exploratoria (EDA)",
        "Explanatoria",
        "Dados & CSV"
    ])

    # ---------------------------------------------------------
    # ABA 1: MAQUINA POKEDEX INTERATIVA (CONTROLES D-PAD + CAPTURA)
    # ---------------------------------------------------------
    with tab_dex:
        stats_6 = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
        df_dex = df_clust.sort_values("pokedex_number").reset_index(drop=True)
        total_dex = len(df_dex)

        if st.session_state["dex_cursor"] >= total_dex:
            st.session_state["dex_cursor"] = 0

        # Barra de Controles Fisicos D-Pad da Maquina Pokedex
        b1, b2, b3, b4 = st.columns([1, 1, 1.2, 2.2])
        if b1.button("◀ ANTERIOR", use_container_width=True):
            st.session_state["dex_cursor"] = (st.session_state["dex_cursor"] - 1) % total_dex
            st.rerun()
        if b2.button("PROXIMO ▶", use_container_width=True):
            st.session_state["dex_cursor"] = (st.session_state["dex_cursor"] + 1) % total_dex
            st.rerun()
        if b3.button("🎲 SCAN ALEATORIO", use_container_width=True):
            st.session_state["dex_cursor"] = random.randint(0, total_dex - 1)
            show_pokeball_loader("ESCANEANDO MATO ALTO...", "Buscando especie selvagem no banco de dados...", duration=0.45)
            st.rerun()

        nomes_dex = [f"#{int(r['pokedex_number']):03d} — {r['name']}" for _, r in df_dex.iterrows()]
        sel_idx = b4.selectbox(
            "Busca rapida na Pokedex:",
            options=list(range(total_dex)),
            index=st.session_state["dex_cursor"],
            format_func=lambda i: nomes_dex[i],
            label_visibility="collapsed"
        )
        if sel_idx != st.session_state["dex_cursor"]:
            st.session_state["dex_cursor"] = sel_idx
            st.rerun()

        pkm = df_dex.iloc[st.session_state["dex_cursor"]]
        dex_id = int(pkm["pokedex_number"])

        if dex_id not in st.session_state["seen_ids"]:
            st.session_state["seen_ids"].add(dex_id)
            st.session_state["trainer_xp"] += 10

        col_p1, col_p2 = st.columns([1.08, 1.22])
        with col_p1:
            type_cor = TYPE_COLORS.get(pkm["type1"], "#64748B")
            gif_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/{dex_id}.gif"
            art_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{dex_id}.png"
            cry_url = f"https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{dex_id}.ogg"

            badges = render_type_badge(pkm["type1"])
            if pkm["type2"] != "None":
                badges += render_type_badge(pkm["type2"])

            ja_capturado = dex_id in st.session_state["caught_ids"]
            status_cap_html = (
                '<span style="background:#22C55E;color:#FFF;padding:2px 8px;border-radius:6px;font-size:0.68rem;">CAPTURADO</span>'
                if ja_capturado else
                '<span style="background:#64748B;color:#FFF;padding:2px 8px;border-radius:6px;font-size:0.68rem;">SELVAGEM</span>'
            )

            card_extra_cls = "battle-card-holo" if pkm["is_legendary"] == 1 else ""
            card_bg = "" if pkm["is_legendary"] == 1 else f"background: linear-gradient(155deg, {type_cor}28 0%, #FFFFFF 55%);"

            st.markdown(
                f'<div class="battle-card {card_extra_cls}" style="{card_bg}">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;font-family:\'JetBrains Mono\',monospace;font-size:0.78rem;color:#334155;font-weight:700;">'
                f'<span>#{dex_id:03d} • GEN {int(pkm["generation"])}</span>'
                f'<div>{status_cap_html} <span style="background:#1E293B;color:#FFCB05;padding:2px 8px;border-radius:6px;font-size:0.68rem;">{pkm["Cluster"]}</span></div></div>'
                f'<div style="display:flex;align-items:center;justify-content:center;gap:18px;margin:12px 0;">'
                f'<img src="{art_url}" width="142" style="filter:drop-shadow(0 8px 14px rgba(0,0,0,0.2));" />'
                f'<img src="{gif_url}" onerror="this.style.display=\'none\';" style="max-height:78px;" />'
                f'</div>'
                f'<div style="text-align:center;margin-bottom:14px;">'
                f'<h2 style="margin:0 0 6px 0;color:#111827;font-size:1.55rem;">{pkm["name"]}</h2>'
                f'<div>{badges}</div>'
                f'<div style="margin-top:8px;font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;color:#334155;">'
                f'<b>BST:</b> {int(pkm["base_total"])} &nbsp;|&nbsp; <b>H:</b> {"n/d (forma alternativa)" if pd.isna(pkm["height_m"]) else f"{pkm['height_m']:.1f}m"} &nbsp;|&nbsp; <b>W:</b> {"n/d" if pd.isna(pkm["weight_kg"]) else f"{pkm['weight_kg']:.1f}kg"}</div>'
                f'</div>'
                f'{render_showdown_stats(pkm)}'
                f'</div>',
                unsafe_allow_html=True
            )

            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            c_cap, c_cry = st.columns([1, 1.3])
            with c_cap:
                if not ja_capturado:
                    if st.button(f"🔴 Capturar {pkm['name']}", use_container_width=True):
                        show_capture_animation(pkm["name"], dex_id, is_legendary=(pkm["is_legendary"] == 1))
                        st.session_state["caught_ids"].add(dex_id)
                        ganho = 40 if pkm["is_legendary"] == 1 else 20
                        st.session_state["trainer_xp"] += ganho
                        st.toast(f"{pkm['name']} enviado para o PC Box! +{ganho} XP", icon="🎉")
                        st.rerun()
                else:
                    st.success(f"{pkm['name']} salvo no seu PC Box!")
            with c_cry:
                st.audio(cry_url)

        with col_p2:
            nomes_disp = sorted(df_clust["name"].unique())
            idx_2 = nomes_disp.index("Mewtwo") if "Mewtwo" in nomes_disp else (nomes_disp.index(pkm["name"]) + 1) % len(nomes_disp)
            pkms_comp = st.multiselect(
                "Comparador de Batalha Lado a Lado:",
                options=nomes_disp,
                default=[pkm["name"], nomes_disp[idx_2]] if nomes_disp[idx_2] != pkm["name"] else [pkm["name"]]
            )
            if pkms_comp:
                df_comp_p = df_clust[df_clust["name"].isin(pkms_comp)]
                df_comp_melt = df_comp_p.melt(
                    id_vars=["name", "Cluster"],
                    value_vars=stats_6,
                    var_name="Atributo",
                    value_name="Valor"
                )
                fig_comp_bar = px.bar(
                    df_comp_melt,
                    x="Atributo",
                    y="Valor",
                    color="name",
                    barmode="group",
                    text="Valor",
                    color_discrete_sequence=["#DC0A2D", "#2563EB", "#059669", "#D97706"],
                    title="Duelo de Atributos Base (Comparacao Direta)",
                    labels={"Atributo": "Atributo de Combate", "Valor": "Pontuacao Base (0–255)", "name": "Pokemon"}
                )
                fig_comp_bar.update_traces(textposition="outside", textfont=dict(size=11, color="#0F172A"))
                max_v_comp = max(160, int(df_comp_melt["Valor"].max()) + 25)
                fig_comp_bar = style_plotly(fig_comp_bar, 410, y_zero=True)
                fig_comp_bar.update_yaxes(range=[0, max_v_comp], dtick=25)
                st.plotly_chart(fig_comp_bar, use_container_width=True)
                st.dataframe(
                    df_comp_p[["pokedex_number", "name", "type1", "type2", "base_total", "Cluster"] + stats_6],
                    use_container_width=True
                )

    # ---------------------------------------------------------
    # ABA 2: PC BOX (MEUS POKEMONS CAPTURADOS)
    # ---------------------------------------------------------
    with tab_pcbox:
        caught_set = st.session_state["caught_ids"]
        st.markdown(
            f'<div class="pcbox-header">'
            f'<div><span style="font-family:\'Press Start 2P\',monospace;font-size:0.8rem;">PC BOX 01 — SINNOH STORAGE</span><br>'
            f'<span style="font-size:0.84rem;opacity:0.9;">Todos os Pokemons capturados na sua sessao com seus Clusters K-Means</span></div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.95rem;font-weight:700;background:#0F172A;padding:6px 12px;border-radius:8px;border:2px solid #FFFFFF;">'
            f'{len(caught_set)} / {len(df_raw)} CAPTURADOS</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        if not caught_set:
            st.info("Seu PC Box ainda esta vazio! Va na aba **Maquina Pokedex**, escolha um Pokemon (ou clique em **SCAN ALEATORIO**) e aperte **Capturar** para comecar seu time.")
        else:
            df_caught = df_clust[df_clust["pokedex_number"].isin(caught_set)].sort_values("pokedex_number")
            if df_caught.empty:
                df_caught = df_raw[df_raw["pokedex_number"].isin(caught_set)].sort_values("pokedex_number").copy()
                df_caught["Cluster"] = "Fora do filtro atual"

            # Metricas rapidas do Time Capturado
            tc1, tc2, tc3, tc4 = st.columns(4)
            mais_forte = df_caught.nlargest(1, "base_total").iloc[0]
            for col_t, lbl_t, val_t, cor_t in [
                (tc1, "No PC Box", f"{len(df_caught)}", "#0284C7"),
                (tc2, "Base Total Media", f"{df_caught['base_total'].mean():.1f}", "#2563EB"),
                (tc3, "Mais Forte", f"{mais_forte['name']} ({int(mais_forte['base_total'])})", "#DC0A2D"),
                (tc4, "Lendarios", f"{int(df_caught['is_legendary'].sum())}", "#D97706"),
            ]:
                col_t.markdown(
                    f'<div class="kpi-card" style="border-top:4px solid {cor_t};">'
                    f'<div class="kpi-label">{lbl_t}</div>'
                    f'<div class="kpi-value" style="font-size:1.15rem;">{val_t}</div></div>',
                    unsafe_allow_html=True
                )

            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            # Grade visual de slots do PC Box (4 por linha)
            cols_pc = st.columns(4)
            for idx_pc, (_, r_pc) in enumerate(df_caught.iterrows()):
                pid = int(r_pc["pokedex_number"])
                gif_pc = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/{pid}.gif"
                art_pc = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid}.png"
                b_pc = render_type_badge(r_pc["type1"])
                if r_pc["type2"] != "None":
                    b_pc += render_type_badge(r_pc["type2"])

                col_slot = cols_pc[idx_pc % 4]
                with col_slot:
                    st.markdown(
                        f'<div class="pcbox-slot">'
                        f'<div style="display:flex;justify-content:space-between;font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;color:#475569;font-weight:700;">'
                        f'<span>#{pid:03d}</span>'
                        f'<span style="background:#1E293B;color:#FFCB05;padding:1px 6px;border-radius:4px;">{r_pc["Cluster"]}</span></div>'
                        f'<div style="height:72px;display:flex;align-items:center;justify-content:center;margin:6px 0;">'
                        f'<img src="{gif_pc}" onerror="this.onerror=null;this.src=\'{art_pc}\';" style="max-height:64px;max-width:68px;" />'
                        f'</div>'
                        f'<div style="font-weight:700;font-size:0.95rem;color:#111827;margin-bottom:5px;">{r_pc["name"]}</div>'
                        f'<div style="margin-bottom:6px;">{b_pc}</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.75rem;color:#334155;">BST: <b>{int(r_pc["base_total"])}</b></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button(f"Soltar {r_pc['name']}", key=f"release_{pid}", use_container_width=True):
                        st.session_state["caught_ids"].discard(pid)
                        st.toast(f"{r_pc['name']} foi solto na natureza!", icon="🍃")
                        st.rerun()

            st.markdown("---")
            col_pc_chart, col_pc_exp = st.columns([1.4, 1])
            with col_pc_chart:
                pc_clust = df_caught["Cluster"].value_counts().reset_index()
                pc_clust.columns = ["Cluster", "Quantidade"]
                fig_pc_bar = px.bar(
                    pc_clust,
                    x="Cluster",
                    y="Quantidade",
                    color="Cluster",
                    text="Quantidade",
                    color_discrete_sequence=CLUSTER_PALETTE,
                    title="Distribuicao dos Clusters K-Means no Seu Time Capturado",
                    labels={"Cluster": "Cluster K-Means", "Quantidade": "Qtd. de Pokemons"}
                )
                fig_pc_bar.update_traces(textposition="outside")
                fig_pc_bar.update_layout(showlegend=False)
                fig_pc_bar = style_plotly(fig_pc_bar, 340, y_zero=True)
                fig_pc_bar.update_yaxes(dtick=1, range=[0, int(pc_clust["Quantidade"].max()) + 1])
                st.plotly_chart(fig_pc_bar, use_container_width=True)
            with col_pc_exp:
                st.markdown("#### Exportar Seu Time")
                st.dataframe(
                    df_caught[["pokedex_number", "name", "type1", "Cluster", "base_total"]],
                    use_container_width=True,
                    height=220
                )
                st.download_button(
                    "Baixar Meu Time (CSV)",
                    data=df_caught.to_csv(index=False).encode("utf-8"),
                    file_name="meu_time_pokemon.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    # ---------------------------------------------------------
    # ABA 3: DESAFIO GAMIFICADO — "QUAL E O CLUSTER K-MEANS?" (INSTANTANEO COM FRAGMENT)
    # ---------------------------------------------------------
    def describe_cluster_archetype(sub_df, c_num, total_k):
        bst_m = sub_df["base_total"].mean()
        stat_means = {
            "HP": sub_df["hp"].mean(),
            "ATK": sub_df["attack"].mean(),
            "DEF": sub_df["defense"].mean(),
            "SP.A": sub_df["sp_attack"].mean(),
            "SP.D": sub_df["sp_defense"].mean(),
            "SPD": sub_df["speed"].mean(),
        }
        top_stat = max(stat_means, key=stat_means.get)
        if c_num == 0:
            nome = "Iniciais / Basicos"
        elif c_num == total_k - 1:
            nome = "Titas / Lendarios"
        elif top_stat in ("DEF", "SP.D", "HP"):
            nome = "Tanques / Defensivos"
        elif top_stat == "SPD":
            nome = "Sweepers / Velozes"
        elif top_stat == "SP.A":
            nome = "Atacantes Especiais"
        else:
            nome = "Atacantes Fisicos"
        return nome, bst_m, top_stat, stat_means[top_stat]

    @st.fragment
    def render_cluster_quiz(df_quiz_src, total_k):
        # Construir guia visual rapido dos clusters (apelido + icone + ponto forte)
        cluster_meta = {}
        for c_i in range(total_k):
            sub_i = df_quiz_src[df_quiz_src["Cluster_Num"] == c_i]
            apelido, bst_m, top_s, top_v = describe_cluster_archetype(sub_i, c_i, total_k)
            rep_row = sub_i.iloc[(sub_i["base_total"] - bst_m).abs().argsort()[:1]].iloc[0]
            cluster_meta[c_i] = {
                "apelido": apelido,
                "bst": bst_m,
                "top_stat": top_s,
                "top_val": top_v,
                "rep_name": rep_row["name"],
                "rep_id": int(rep_row["pokedex_number"]),
                "cor": CLUSTER_PALETTE[c_i % len(CLUSTER_PALETTE)]
            }

        valid_ids = df_quiz_src["pokedex_number"].tolist()
        if st.session_state["quiz_pkm_id"] not in valid_ids:
            st.session_state["quiz_pkm_id"] = int(random.choice(valid_ids))
            st.session_state["quiz_feedback"] = None

        q_pkm = df_quiz_src[df_quiz_src["pokedex_number"] == st.session_state["quiz_pkm_id"]].iloc[0]
        q_dex = int(q_pkm["pokedex_number"])
        q_true_cluster = int(q_pkm["Cluster_Num"])
        revelado = st.session_state["quiz_feedback"] is not None

        # Barra superior compacta de placar do mini-game
        st.markdown(
            f'<div class="autoral-note" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            f'<div><b>DESAFIO K-MEANS:</b> Olhe o <b>Base Total</b> e o <b>ponto forte</b> do Pokemon abaixo e adivinhe seu Cluster!</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.82rem;">'
            f'Acertos: <b>{st.session_state["quiz_hits"]}/{st.session_state["quiz_total"]}</b> &nbsp;|&nbsp; '
            f'Streak: <b>{st.session_state["quiz_streak"]}</b> &nbsp;|&nbsp; '
            f'XP: <b>{st.session_state["trainer_xp"]}</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        col_q1, col_q2 = st.columns([0.95, 1.35])
        with col_q1:
            q_art = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{q_dex}.png"
            img_filter = "" if revelado else "filter: brightness(0) drop-shadow(0 6px 10px rgba(0,0,0,0.35));"
            q_titulo = f"#{q_dex:03d} — {q_pkm['name']}" if revelado else "QUEM E ESSE CLUSTER?"

            # Destaque automatico do maior stat do Pokemon misterioso
            p_stats = {
                "HP": int(q_pkm["hp"]), "ATK": int(q_pkm["attack"]), "DEF": int(q_pkm["defense"]),
                "SP.A": int(q_pkm["sp_attack"]), "SP.D": int(q_pkm["sp_defense"]), "SPD": int(q_pkm["speed"])
            }
            p_top_s = max(p_stats, key=p_stats.get)

            st.markdown(
                f'<div class="battle-card" style="background:#FFFFFF;">'
                f'<div style="text-align:center;">'
                f'<span style="font-family:\'Press Start 2P\',monospace;font-size:0.68rem;color:#CC1E2C;">{q_titulo}</span><br>'
                f'<img src="{q_art}" width="150" style="margin:10px 0;{img_filter}transition:filter 0.35s ease;" />'
                f'</div>'
                f'<div style="display:flex;justify-content:center;gap:8px;margin-bottom:10px;font-family:\'JetBrains Mono\',monospace;font-size:0.76rem;">'
                f'<span style="background:#1E293B;color:#FFCB05;padding:3px 9px;border-radius:6px;font-weight:700;">BST: {int(q_pkm["base_total"])}</span>'
                f'<span style="background:#E2E8F0;color:#1E293B;padding:3px 9px;border-radius:6px;font-weight:700;">Forte: {p_top_s} ({p_stats[p_top_s]})</span>'
                f'</div>'
                f'{render_showdown_stats(q_pkm)}'
                f'</div>',
                unsafe_allow_html=True
            )

        with col_q2:
            st.markdown("#### Escolha o Cluster correspondente:")

            # Cards clicaveis / referencia clara lado a lado (2 colunas)
            grid_c = st.columns(2)
            for c_opt in range(total_k):
                meta = cluster_meta[c_opt]
                sprite_sm = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{meta['rep_id']}.png"
                border_extra = ""
                if revelado and c_opt == q_true_cluster:
                    border_extra = "border:3px solid #16A34A;background:#F0FDF4;"

                with grid_c[c_opt % 2]:
                    st.markdown(
                        f'<div class="cluster-card" style="padding:10px 12px;margin-bottom:6px;border-left:5px solid {meta["cor"]};{border_extra}">'
                        f'<div style="display:flex;align-items:center;justify-content:space-between;">'
                        f'<div>'
                        f'<div style="font-weight:700;color:{meta["cor"]};font-size:0.88rem;">Cluster {c_opt} — {meta["apelido"]}</div>'
                        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.72rem;color:#475569;">'
                        f'BST medio: <b>{meta["bst"]:.0f}</b> • Destaque: <b>{meta["top_stat"]} ({meta["top_val"]:.0f})</b></div>'
                        f'<div style="font-size:0.7rem;color:#64748B;">Ex.: {meta["rep_name"]}</div>'
                        f'</div>'
                        f'<img src="{sprite_sm}" width="48" />'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
                    if st.button(
                        f"Escolher Cluster {c_opt}",
                        key=f"quiz_btn_{c_opt}",
                        use_container_width=True,
                        disabled=revelado
                    ):
                        st.session_state["quiz_total"] += 1
                        true_apelido = cluster_meta[q_true_cluster]["apelido"]
                        if c_opt == q_true_cluster:
                            st.session_state["quiz_hits"] += 1
                            st.session_state["quiz_streak"] += 1
                            st.session_state["trainer_xp"] += 50
                            st.session_state["quiz_feedback"] = (
                                "ok",
                                f"ACERTOU! {q_pkm['name']} e do Cluster {q_true_cluster} ({true_apelido}) — BST {int(q_pkm['base_total'])} e foco em {p_top_s}. (+50 XP)"
                            )
                        else:
                            st.session_state["quiz_streak"] = 0
                            st.session_state["quiz_feedback"] = (
                                "err",
                                f"Errou! {q_pkm['name']} pertence ao Cluster {q_true_cluster} ({true_apelido}), que tem BST medio de {cluster_meta[q_true_cluster]['bst']:.0f}."
                            )
                        st.rerun(scope="fragment")

            if revelado:
                fb_type, fb_msg = st.session_state["quiz_feedback"]
                if fb_type == "ok":
                    st.success(fb_msg)
                else:
                    st.error(fb_msg)

                act1, act2 = st.columns(2)
                if act1.button("▶ PROXIMO DESAFIO", use_container_width=True, type="primary"):
                    st.session_state["quiz_pkm_id"] = int(random.choice(valid_ids))
                    st.session_state["quiz_feedback"] = None
                    st.rerun(scope="fragment")
                if q_dex not in st.session_state["caught_ids"]:
                    if act2.button(f"🔴 Guardar {q_pkm['name']} no PC Box", use_container_width=True):
                        st.session_state["caught_ids"].add(q_dex)
                        st.session_state["trainer_xp"] += 20
                        st.toast(f"{q_pkm['name']} guardado no PC Box! +20 XP", icon="🎉")
                        st.rerun()
                else:
                    act2.info("Ja esta no seu PC Box!")

    with tab_quiz:
        render_cluster_quiz(df_clust, k_clusters)

    # ---------------------------------------------------------
    # ABA 3: CLUSTERS K-MEANS
    # ---------------------------------------------------------
    with tab_km:
        st.markdown("#### Arquetipos Descobertos — Sprites Animados dos Representantes")
        cols_showcase = st.columns(min(k_clusters, 4))
        for c_idx in range(k_clusters):
            sub_c = df_clust[df_clust["Cluster_Num"] == c_idx]
            exemplos_c = sub_c.nlargest(3, "base_total")
            cor_c = CLUSTER_PALETTE[c_idx % len(CLUSTER_PALETTE)]

            sprites_html = ""
            for _, row_ex in exemplos_c.iterrows():
                dex_num = int(row_ex["pokedex_number"])
                gif_u = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/{dex_num}.gif"
                art_u = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{dex_num}.png"
                sprites_html += (
                    f'<div style="display:inline-block;text-align:center;margin:0 7px;vertical-align:bottom;">'
                    f'<img src="{gif_u}" onerror="this.onerror=null;this.src=\'{art_u}\';" style="max-height:52px;max-width:56px;" /><br>'
                    f'<span style="font-size:0.72rem;color:#334155;font-weight:700;">{row_ex["name"]}</span></div>'
                )

            target_col = cols_showcase[c_idx % len(cols_showcase)]
            target_col.markdown(
                f'<div class="cluster-card" style="border-top:4px solid {cor_c};">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">'
                f'<span style="font-weight:700;color:{cor_c};font-size:0.95rem;">Cluster {c_idx}</span>'
                f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:0.74rem;color:#64748B;">{len(sub_c)} pkms | Base {sub_c["base_total"].mean():.0f}</span>'
                f'</div>'
                f'<div style="text-align:center;min-height:76px;display:flex;align-items:flex-end;justify-content:center;">{sprites_html}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        col_k1, col_k2 = st.columns([1.3, 0.7])
        with col_k1:
            var_expl = pca_2d.explained_variance_ratio_ * 100
            fig_pca = px.scatter(
                df_clust,
                x="PCA1",
                y="PCA2",
                color="Cluster",
                color_discrete_sequence=CLUSTER_PALETTE,
                hover_name="name",
                hover_data=["type1", "type2", "base_total", "status_lendario"] + features_sel,
                title=f"Projecao 2D dos Clusters via PCA (PC1: {var_expl[0]:.1f}% | PC2: {var_expl[1]:.1f}%)",
                labels={"PCA1": f"PC1 — Variancia explicada: {var_expl[0]:.1f}%", "PCA2": f"PC2 — Variancia explicada: {var_expl[1]:.1f}%"}
            )
            fig_pca.update_traces(marker=dict(size=8, opacity=0.84, line=dict(width=0.6, color="#FFFFFF")))
            st.plotly_chart(style_plotly(fig_pca, 430, show_zeroline=True), use_container_width=True)

        with col_k2:
            dist_c = df_clust["Cluster"].value_counts().reset_index()
            dist_c.columns = ["Cluster", "Contagem"]
            dist_c["Pct"] = (dist_c["Contagem"] / len(df_clust) * 100).round(1)
            dist_c["Rotulo"] = dist_c["Contagem"].astype(str) + " (" + dist_c["Pct"].astype(str) + "%)"
            fig_dist = px.bar(
                dist_c,
                x="Contagem",
                y="Cluster",
                orientation="h",
                color="Cluster",
                color_discrete_sequence=CLUSTER_PALETTE,
                text="Rotulo",
                title="Contagem por Cluster",
                labels={"Contagem": "Qtd. de Pokemons", "Cluster": "Grupo (K-Means)"}
            )
            fig_dist.update_traces(textposition="outside", textfont=dict(size=11, color="#0F172A"))
            fig_dist.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            fig_dist = style_plotly(fig_dist, 430)
            fig_dist.update_xaxes(range=[0, float(dist_c["Contagem"].max()) * 1.28], rangemode="tozero")
            st.plotly_chart(fig_dist, use_container_width=True)

        with st.expander("Curva do Cotovelo e Coeficiente de Silhueta (k = 2 a 8)", expanded=False):
            k_range = list(range(2, 9))
            inertias, silhouettes = [], []
            for test_k in k_range:
                km_t = KMeans(n_clusters=test_k, random_state=int(random_state), n_init=10)
                lbl_t = km_t.fit_predict(X_scaled)
                inertias.append(km_t.inertia_)
                silhouettes.append(silhouette_score(X_scaled, lbl_t))

            fig_eval = go.Figure()
            fig_eval.add_trace(go.Scatter(x=k_range, y=inertias, mode="lines+markers", name="Inercia (WCSS)", yaxis="y1", line=dict(color="#DC0A2D", width=3), marker=dict(size=8)))
            fig_eval.add_trace(go.Scatter(x=k_range, y=silhouettes, mode="lines+markers", name="Silhouette Score", yaxis="y2", line=dict(color="#2563EB", width=3, dash="dot"), marker=dict(size=8)))
            fig_eval = style_plotly(fig_eval, 380)
            fig_eval.update_layout(
                title="Avaliacao de Hiperparametro k (Cotovelo e Silhueta)",
                margin=dict(l=72, r=72, t=60, b=52),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(title=dict(text="Numero de Clusters (k)"), tickmode="linear", dtick=1),
                yaxis=dict(
                    title=dict(text="Inercia (WCSS)", font=dict(color="#DC0A2D", size=13)),
                    tickfont=dict(color="#DC0A2D", size=11.5),
                    tickformat=",.0f",
                    rangemode="tozero",
                    showline=True,
                    linecolor="#DC0A2D"
                ),
                yaxis2=dict(
                    title=dict(text="Silhouette Score (0 a 1)", font=dict(color="#2563EB", size=13)),
                    tickfont=dict(color="#2563EB", size=11.5),
                    tickformat=".2f",
                    range=[0, max(0.5, max(silhouettes) * 1.25)],
                    overlaying="y",
                    side="right",
                    showgrid=False,
                    showline=True,
                    linecolor="#2563EB"
                )
            )
            st.plotly_chart(fig_eval, use_container_width=True)

        resumo = df_clust.groupby("Cluster")[features_sel + ["base_total", "is_legendary"]].mean()
        resumo["Contagem"] = df_clust.groupby("Cluster").size()
        resumo["Pct_Lendarios"] = (resumo["is_legendary"] * 100).round(1)
        resumo = resumo.drop(columns=["is_legendary"])
        st.dataframe(resumo.style.format("{:.1f}").background_gradient(cmap="Reds"), use_container_width=True)

    # ---------------------------------------------------------
    # ABA 4: EXPLORATORIA (4 VISUALIZACOES)
    # ---------------------------------------------------------
    with tab_exp:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            type_counts = df_clust["type1"].value_counts().reset_index()
            type_counts.columns = ["Tipo Primario", "Quantidade"]
            fig_type = px.bar(
                type_counts,
                x="Quantidade",
                y="Tipo Primario",
                orientation="h",
                text="Quantidade",
                color="Tipo Primario",
                color_discrete_map=TYPE_COLORS,
                title="Exploratoria 1: Quantidade de Pokemons por Tipo Primario",
                labels={"Quantidade": "Qtd. de Especies", "Tipo Primario": "Tipo Primario"}
            )
            fig_type.update_traces(textposition="outside", textfont=dict(size=11, color="#0F172A"))
            fig_type.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"})
            fig_type = style_plotly(fig_type, 460)
            fig_type.update_xaxes(range=[0, float(type_counts["Quantidade"].max()) * 1.18], dtick=20, rangemode="tozero")
            st.plotly_chart(fig_type, use_container_width=True)

        with col_e2:
            stat_box = st.selectbox(
                "Atributo para inspecao de distribuicao e outliers:",
                ["base_total", "hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]
            )
            y_label_box = "Base Total (BST — 180 a 780)" if stat_box == "base_total" else f"Pontuacao Base de {stat_box.upper()} (0 a 255)"
            fig_box = px.box(
                df_clust,
                x="type1",
                y=stat_box,
                color="type1",
                color_discrete_map=TYPE_COLORS,
                hover_name="name",
                title=f"Exploratoria 2: Distribuicao e Outliers de {stat_box.upper()} por Tipo",
                labels={"type1": "Tipo Primario", stat_box: y_label_box},
                points="outliers"
            )
            fig_box.update_layout(showlegend=False, xaxis_tickangle=-45)
            fig_box = style_plotly(fig_box, 400, y_zero=True)
            fig_box.update_yaxes(dtick=100 if stat_box == "base_total" else 25)
            st.plotly_chart(fig_box, use_container_width=True)

        col_e3, col_e4 = st.columns(2)
        with col_e3:
            stats_corr = ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed", "base_total", "height_m", "weight_kg"]
            corr_mat = df_clust[stats_corr].corr()
            fig_corr = px.imshow(
                corr_mat,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1,
                title="Exploratoria 3: Matriz de Correlacao Linear (Pearson)",
                labels=dict(x="Variavel", y="Variavel", color="Correlacao (r)")
            )
            fig_corr = style_plotly(fig_corr, 440)
            fig_corr.update_xaxes(tickangle=-35, showgrid=False)
            fig_corr.update_yaxes(showgrid=False)
            st.plotly_chart(fig_corr, use_container_width=True)

        with col_e4:
            sc1, sc2 = st.columns(2)
            eixo_x = sc1.selectbox("Eixo X:", options=stats_corr, index=1)
            eixo_y = sc2.selectbox("Eixo Y:", options=stats_corr, index=2)
            fig_sc = px.scatter(
                df_clust,
                x=eixo_x,
                y=eixo_y,
                color="status_lendario",
                color_discrete_map={"Comum": "#94A3B8", "Lendario": "#DC0A2D"},
                size="base_total",
                hover_name="name",
                hover_data=["pokedex_number", "type1", "type2", "Cluster"],
                title=f"Exploratoria 4: {eixo_x.upper()} vs {eixo_y.upper()} (Lendarios em Destaque)",
                labels={eixo_x: f"{eixo_x.upper()} (Eixo X)", eixo_y: f"{eixo_y.upper()} (Eixo Y)", "status_lendario": "Categoria"}
            )
            fig_sc = style_plotly(fig_sc, 385, y_zero=True)
            fig_sc.update_xaxes(rangemode="tozero")
            st.plotly_chart(fig_sc, use_container_width=True)

    # ---------------------------------------------------------
    # ABA 5: EXPLANATORIA & STORYTELLING
    # ---------------------------------------------------------
    with tab_story:
        # [IA] Claude (Antigravity) – Pergunta de pesquisa, publico-alvo e explanatorias alinhadas ao notebook (secoes 1 e 7)
        st.markdown(
            '<div class="autoral-note">'
            '<b>Pergunta de pesquisa:</b> o aumento do poder de combate (Base Total) ao longo das geracoes '
            '(<i>power creep</i>) atinge os Pokemon comuns ou e explicado pela maior presenca de lendarios nas geracoes recentes?<br>'
            '<b>Publico-alvo:</b> jogadores e entusiastas de Pokemon (publico nao tecnico).<br>'
            '<b>Leitura:</b> vermelho = elemento da mensagem; cinza = contexto. Os graficos tecnicos (cotovelo, PCA) '
            'ficam na aba <i>Clusters K-Means</i> e nao fazem parte da narrativa.'
            '</div>',
            unsafe_allow_html=True
        )

        VERMELHO, CINZA, CINZA_CLARO = "#DC0A2D", "#8D99AE", "#D9DEE5"
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            gen_todos = df_clust.groupby("generation")["base_total"].mean().rename("Todos os Pokemon")
            gen_comuns = df_clust[df_clust["is_legendary"] == 0].groupby("generation")["base_total"].mean().rename("Somente comuns")
            gen_stats = pd.concat([gen_todos, gen_comuns], axis=1).reset_index()
            gen_long = gen_stats.melt(id_vars="generation", var_name="Grupo", value_name="base_total").dropna()
            gen_long["rotulo"] = gen_long["base_total"].round(0).astype(int).astype(str)
            fig_exp1 = px.line(
                gen_long,
                x="generation",
                y="base_total",
                color="Grupo",
                text="rotulo",
                markers=True,
                color_discrete_map={"Todos os Pokemon": VERMELHO, "Somente comuns": CINZA},
                title="Explanatoria 1: o poder medio sobe nas geracoes novas, puxado pelos lendarios",
                labels={"generation": "Geracao (1 a 7)", "base_total": "Media de Base Total (BST)", "Grupo": ""}
            )
            fig_exp1.update_traces(line=dict(width=2.5), marker=dict(size=8), textposition="top center", textfont=dict(size=10.5))
            fig_exp1.update_traces(selector=dict(name="Todos os Pokemon"), line=dict(width=4.5), marker=dict(size=11))
            fig_exp1 = style_plotly(fig_exp1, 430, y_zero=True)
            fig_exp1.update_xaxes(dtick=1)
            max_exp1 = max(500, float(gen_long["base_total"].max()) + 65)
            fig_exp1.update_yaxes(range=[0, max_exp1], dtick=100)
            pct_leg = df_clust.groupby("generation")["is_legendary"].mean() * 100
            for g_val, p_val in pct_leg.items():
                fig_exp1.add_annotation(
                    x=g_val, y=0.04, yref="paper", text=f"{p_val:.0f}% lend.",
                    showarrow=False, font=dict(size=10, color=VERMELHO if p_val == pct_leg.max() else "#64748B")
                )
            st.plotly_chart(fig_exp1, use_container_width=True)

        with col_s2:
            cluster_titas = df_clust["Cluster_Num"].max()  # clusters ordenados por base_total: o ultimo e o de maior poder
            df_t = df_clust.assign(titas=df_clust["Cluster_Num"] == cluster_titas)
            comp = df_t.groupby("generation").apply(lambda g: pd.Series({
                "Lendarios": (g["titas"] & (g["is_legendary"] == 1)).mean() * 100,
                "Comuns": (g["titas"] & (g["is_legendary"] == 0)).mean() * 100,
            }), include_groups=False).reset_index()
            comp_long = comp.melt(id_vars="generation", var_name="Categoria", value_name="Pct")
            fig_exp2 = px.bar(
                comp_long,
                x="generation",
                y="Pct",
                color="Categoria",
                text_auto=".1f",
                category_orders={"Categoria": ["Comuns", "Lendarios"]},
                color_discrete_map={"Comuns": CINZA_CLARO, "Lendarios": VERMELHO},
                title=f"Explanatoria 2: % de cada geracao no grupo de maior poder (Cluster {cluster_titas})",
                labels={"generation": "Geracao (1 a 7)", "Pct": "% da geracao no grupo de maior poder (0–100%)", "Categoria": ""}
            )
            fig_exp2.update_layout(barmode="stack")
            fig_exp2 = style_plotly(fig_exp2, 430, y_zero=True)
            fig_exp2.update_xaxes(dtick=1)
            max_pct_exp2 = min(100, max(35, float(comp[["Lendarios", "Comuns"]].sum(axis=1).max()) + 8))
            fig_exp2.update_yaxes(range=[0, max_pct_exp2], dtick=10, ticksuffix="%")
            st.plotly_chart(fig_exp2, use_container_width=True)

    # ---------------------------------------------------------
    # ABA 6: DADOS & CSV
    # ---------------------------------------------------------
    with tab_tab:
        cols_show = ["pokedex_number", "name", "type1", "type2", "generation", "status_lendario", "Cluster", "base_total"] + features_sel
        st.dataframe(df_clust[cols_show], use_container_width=True)
        csv_bytes = df_clust.to_csv(index=False).encode("utf-8")
        st.download_button("Baixar Base Clusterizada (CSV)", data=csv_bytes, file_name="pokemon_clusters.csv", mime="text/csv")

    # Rodape Hardware Fisico da Maquina Pokedex
    st.markdown("""
    <div class="pokedex-hardware-bar">
        <div class="dpad-mini"><div class="dpad-h"></div><div class="dpad-v"></div></div>
        <div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:0.75rem;">
            <span class="battery-led"></span><b>SINNOH DEX ONLINE</b> &nbsp;|&nbsp; POKEAPI CONNECTED &nbsp;|&nbsp; AVD 2026.2
        </div>
        <div style="display:flex;align-items:center;gap:18px;">
            <div class="ab-buttons">
                <div class="ab-btn">B</div>
                <div class="ab-btn">A</div>
            </div>
            <div class="speaker-grill">
                <div class="speaker-slot"></div>
                <div class="speaker-slot"></div>
                <div class="speaker-slot"></div>
                <div class="speaker-slot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MODULO 2: PARTE COMUM — WINE QUALITY (BONUS VISUAL/UX)
# ==============================================================================
else:
    # [IA] Gemini – Modulo interativo da Parte Comum (Wine Quality) comparando Passada 1 (k=5) e Passada 2 (k=6)
    st.markdown("""
    <div class="pokedex-shell-top" style="background: linear-gradient(120deg, #7F1D1D 0%, #991B1B 58%, #1E293B 100%);">
        <div>
            <h1 class="shell-title">PARTE COMUM — WINE QUALITY</h1>
            <p class="shell-sub">Comparacao interativa entre Passada 1 (k livre = 5 via Cotovelo) e Passada 2 (k fixo = 6 classes reais)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_wine, df_comp, df_m5, df_m6 = load_wine_data()
    if df_wine is None:
        st.error("Dataset `winequality-red.csv` nao encontrado em `data/parte_comum/`.")
        st.stop()

    passada_sel = st.sidebar.radio(
        "Passada do K-Means:",
        options=["Passada 1 — k livre (k = 5)", "Passada 2 — k fixo (k = 6)"]
    )
    k_wine = 5 if "k = 5" in passada_sel else 6

    feature_cols = [c for c in df_wine.columns if c != "quality"]
    X_wine_scaled = StandardScaler().fit_transform(df_wine[feature_cols])
    km_wine = KMeans(n_clusters=k_wine, random_state=42, n_init=10)
    wine_clusters = km_wine.fit_predict(X_wine_scaled)

    df_w_plot = df_wine.copy()
    df_w_plot["Cluster"] = wine_clusters
    mapa_cluster_classe = {
        c_id: int(df_w_plot[df_w_plot["Cluster"] == c_id]["quality"].mode().iloc[0])
        for c_id in range(k_wine)
    }
    df_w_plot["Classe_Mapeada"] = df_w_plot["Cluster"].map(mapa_cluster_classe)
    acc_atual = (df_w_plot["Classe_Mapeada"] == df_w_plot["quality"]).mean() * 100

    pca_w = PCA(n_components=2, random_state=42)
    coords_w = pca_w.fit_transform(X_wine_scaled)
    df_w_plot["PC1"] = coords_w[:, 0]
    df_w_plot["PC2"] = coords_w[:, 1]
    df_w_plot["Cluster_Label"] = df_w_plot["Cluster"].apply(lambda c: f"Cluster {c} (-> nota {mapa_cluster_classe[c]})")

    m1, m2, m3, m4 = st.columns(4)
    for col_m, lbl_m, val_m, cor_m in [
        (m1, "Amostras", f"{len(df_wine)}", "#7F1D1D"),
        (m2, "Passada Ativa", f"k = {k_wine}", "#2563EB"),
        (m3, "Inercia (WCSS)", f"{km_wine.inertia_:.2f}", "#D97706"),
        (m4, "Acuracia Mapeada", f"{acc_atual:.2f}%", "#059669"),
    ]:
        col_m.markdown(
            f'<div class="kpi-card" style="border-top:4px solid {cor_m};">'
            f'<div class="kpi-label">{lbl_m}</div>'
            f'<div class="kpi-value">{val_m}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        var_w = pca_w.explained_variance_ratio_ * 100
        fig_w_pca = px.scatter(
            df_w_plot, x="PC1", y="PC2", color="Cluster_Label",
            color_discrete_sequence=CLUSTER_PALETTE,
            hover_data=["quality", "alcohol", "volatile acidity", "sulphates"],
            title=f"Projecao PCA 2D — {passada_sel}",
            labels={"PC1": f"PC1 ({var_w[0]:.1f}%)", "PC2": f"PC2 ({var_w[1]:.1f}%)", "Cluster_Label": "Cluster"}
        )
        st.plotly_chart(style_plotly(fig_w_pca, 420), use_container_width=True)

    with col_w2:
        classes_reais = sorted(df_w_plot["quality"].unique())
        cm = confusion_matrix(df_w_plot["quality"], df_w_plot["Classe_Mapeada"], labels=classes_reais)
        fig_cm = px.imshow(
            cm, x=[str(c) for c in classes_reais], y=[str(c) for c in classes_reais],
            text_auto=True, color_continuous_scale="Reds",
            title=f"Matriz de Confusao (Real vs Mapeado) — k = {k_wine}",
            labels=dict(x="Classe Mapeada", y="Classe Real (quality)", color="Qtd")
        )
        st.plotly_chart(style_plotly(fig_cm, 420), use_container_width=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if df_comp is not None:
            st.markdown("#### Comparacao Oficial das Passadas")
            st.dataframe(df_comp, use_container_width=True)
    with col_t2:
        df_met_ativo = df_m5 if k_wine == 5 else df_m6
        if df_met_ativo is not None:
            st.markdown(f"#### Metricas por Classe (k = {k_wine})")
            st.dataframe(df_met_ativo, use_container_width=True)
