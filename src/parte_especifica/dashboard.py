import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, davies_bouldin_score

# ==========================================
# 1. Configuração da Página Streamlit
# ==========================================
st.set_page_config(
    page_title="PokéAnalytics - Clustering & EDA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #E63946;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #457B9D;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 5px solid #E63946;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. Carregamento e Cache dos Dados
# ==========================================
@st.cache_data
def load_pokemon_data():
    # Caminhos possíveis para localização do arquivo CSV
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "parte_especifica", "pokemon.csv"),
        os.path.join("data", "parte_especifica", "pokemon.csv"),
        "pokemon.csv"
    ]
    filepath = None
    for p in possible_paths:
        if os.path.exists(p):
            filepath = p
            break

    if filepath is None:
        st.error("Arquivo `pokemon.csv` não encontrado na pasta `data/parte_especifica/`.")
        st.stop()

    df = pd.read_csv(filepath)

    # Padronização e preenchimento de tipos
    df['type1'] = df['type1'].fillna('None').str.capitalize()
    df['type2'] = df['type2'].fillna('None').str.capitalize()
    df['is_legendary'] = df['is_legendary'].astype(int)
    df['generation'] = df['generation'].astype(int)

    # Tratamento de altura e peso
    df['height_m'] = pd.to_numeric(df['height_m'], errors='coerce')
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce')
    df['height_m'] = df['height_m'].fillna(df['height_m'].median())
    df['weight_kg'] = df['weight_kg'].fillna(df['weight_kg'].median())

    return df

df_raw = load_pokemon_data()

# ==========================================
# 3. Barra Lateral (Filtros e Configurações)
# ==========================================
st.sidebar.image("https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png", width=50)
st.sidebar.title("Configurações & Filtros")

# Filtro de Geração
todas_geracoes = sorted(df_raw['generation'].unique())
geracoes_selecionadas = st.sidebar.multiselect(
    "Gerações:",
    options=todas_geracoes,
    default=todas_geracoes
)

# Filtro de Tipos
todos_tipos = sorted([t for t in df_raw['type1'].unique() if t != 'None'])
tipos_selecionados = st.sidebar.multiselect(
    "Tipos Primários:",
    options=todos_tipos,
    default=todos_tipos
)

# Filtro de Lendários
filtro_lendario = st.sidebar.radio(
    "Filtrar por Status Lendário:",
    options=["Todos", "Apenas Lendários", "Apenas Não-Lendários"]
)

# Aplicação dos Filtros
df_filtrado = df_raw[
    (df_raw['generation'].isin(geracoes_selecionadas)) &
    (df_raw['type1'].isin(tipos_selecionados))
]

if filtro_lendario == "Apenas Lendários":
    df_filtrado = df_filtrado[df_filtrado['is_legendary'] == 1]
elif filtro_lendario == "Apenas Não-Lendários":
    df_filtrado = df_filtrado[df_filtrado['is_legendary'] == 0]

if df_filtrado.empty:
    st.warning("Nenhum Pokémon encontrado com os filtros selecionados. Ajuste os filtros na barra lateral.")
    st.stop()

# Parâmetros para Agrupamento (K-Means)
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Parâmetros do K-Means")

atributos_disponiveis = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_total']
features_selecionadas = st.sidebar.multiselect(
    "Variáveis para Clustering:",
    options=atributos_disponiveis,
    default=['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
)

k_clusters = st.sidebar.slider(
    "Número de Clusters (k):",
    min_value=2,
    max_value=8,
    value=4,
    step=1
)

random_state = st.sidebar.number_input("Random State:", min_value=0, max_value=999, value=42)

# ==========================================
# 4. Processamento do Modelo K-Means
# ==========================================
if len(features_selecionadas) < 2:
    st.error("Por favor, selecione pelo menos 2 variáveis numéricas para executar o K-Means.")
    st.stop()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_filtrado[features_selecionadas])

kmeans = KMeans(n_clusters=k_clusters, random_state=random_state, n_init=10)
cluster_labels = kmeans.fit_predict(X_scaled)

df_clusterizado = df_filtrado.copy()
df_clusterizado['Cluster'] = [f"Cluster {c}" for c in cluster_labels]
df_clusterizado['Cluster_Num'] = cluster_labels

# Métricas de Validação do Clustering
sil_score = silhouette_score(X_scaled, cluster_labels) if len(np.unique(cluster_labels)) > 1 else 0
db_score = davies_bouldin_score(X_scaled, cluster_labels) if len(np.unique(cluster_labels)) > 1 else 0
inertia_val = kmeans.inertia_

# Redução de Dimensionalidade (PCA 2D e 3D para visualização)
pca_2d = PCA(n_components=2, random_state=random_state)
pca_coords_2d = pca_2d.fit_transform(X_scaled)
df_clusterizado['PCA1'] = pca_coords_2d[:, 0]
df_clusterizado['PCA2'] = pca_coords_2d[:, 1]

pca_3d = PCA(n_components=3, random_state=random_state)
pca_coords_3d = pca_3d.fit_transform(X_scaled)
df_clusterizado['PCA3D_1'] = pca_coords_3d[:, 0]
df_clusterizado['PCA3D_2'] = pca_coords_3d[:, 1]
df_clusterizado['PCA3D_3'] = pca_coords_3d[:, 2]

# ==========================================
# 5. Cabeçalho e Métricas Principais
# ==========================================
st.markdown('<div class="main-title">⚡ PokéAnalytics: Agrupamento & EDA Interativo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Projeto Final de Análise e Visualização de Dados (AVD) — Parte Específica</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Total de Pokémons", f"{len(df_clusterizado)}")
with col2:
    st.metric("Base Total Média", f"{df_clusterizado['base_total'].mean():.1f}")
with col3:
    st.metric("Clusters Ativos (k)", f"{k_clusters}")
with col4:
    st.metric("Silhouette Score", f"{sil_score:.3f}")
with col5:
    st.metric("Davies-Bouldin", f"{db_score:.3f}")

# ==========================================
# 6. Abas da Aplicação
# ==========================================
tab_eda, tab_kmeans, tab_pokedex, tab_tabela = st.tabs([
    "📊 1. Análise Exploratória (EDA)",
    "🎯 2. Agrupamento (K-Means & Métricas)",
    "🔍 3. Pokédex & Comparador",
    "📋 4. Dados & Exportação"
])

# -------------------------------------------------------------
# ABA 1: ANÁLISE EXPLORATÓRIA DE DADOS (EDA)
# -------------------------------------------------------------
with tab_eda:
    st.subheader("Distribuições e Relações entre Estatísticas de Combate")

    col_eda1, col_eda2 = st.columns(2)

    with col_eda1:
        st.markdown("**Distribuição de Tipos Primários**")
        type_counts = df_clusterizado['type1'].value_counts().reset_index()
        type_counts.columns = ['Tipo', 'Quantidade']
        fig_type = px.bar(
            type_counts,
            x='Tipo',
            y='Quantidade',
            color='Tipo',
            text='Quantidade',
            title="Contagem de Pokémons por Tipo Primário",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_type.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_type, use_container_width=True)

    with col_eda2:
        st.markdown("**Boxplot de Estatísticas por Tipo Primário**")
        stat_escolhido = st.selectbox(
            "Selecione o atributo para comparar entre tipos:",
            ['base_total', 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        )
        fig_box = px.box(
            df_clusterizado,
            x='type1',
            y=stat_escolhido,
            color='type1',
            title=f"Distribuição de {stat_escolhido.upper()} por Tipo Primário",
            points="outliers"
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    col_corr, col_scatter = st.columns([1, 1])

    with col_corr:
        st.markdown("**Matriz de Correlação entre Atributos de Combate**")
        stats_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed', 'base_total', 'height_m', 'weight_kg']
        corr_matrix = df_clusterizado[stats_cols].corr()
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Correlação Linear de Pearson"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with col_scatter:
        st.markdown("**Dispersão Customizada entre Atributos**")
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            eixo_x = st.selectbox("Eixo X:", options=stats_cols, index=1)
        with sc_col2:
            eixo_y = st.selectbox("Eixo Y:", options=stats_cols, index=2)

        fig_sc = px.scatter(
            df_clusterizado,
            x=eixo_x,
            y=eixo_y,
            color='type1',
            size='base_total',
            hover_name='name',
            hover_data=['pokedex_number', 'type1', 'type2', 'is_legendary'],
            title=f"Relação: {eixo_x.capitalize()} vs {eixo_y.capitalize()} (Tamanho = Base Total)"
        )
        st.plotly_chart(fig_sc, use_container_width=True)

# -------------------------------------------------------------
# ABA 2: AGRUPAMENTO (K-MEANS & MÉTRICAS)
# -------------------------------------------------------------
with tab_kmeans:
    st.subheader(f"Resultados do Agrupamento K-Means (k = {k_clusters})")

    # Diagnóstico da Curva do Cotovelo e Silhueta
    with st.expander("📈 Visualizar Curva do Cotovelo & Análise de Silhueta (2 a 8 Clusters)", expanded=False):
        k_range = list(range(2, 9))
        inertias = []
        silhouettes = []
        for test_k in k_range:
            km_test = KMeans(n_clusters=test_k, random_state=random_state, n_init=5)
            labels_test = km_test.fit_predict(X_scaled)
            inertias.append(km_test.inertia_)
            silhouettes.append(silhouette_score(X_scaled, labels_test))

        fig_eval = go.Figure()
        fig_eval.add_trace(go.Scatter(x=k_range, y=inertias, mode='lines+markers', name='Inércia (Elbow)', yaxis='y1', line=dict(color='#E63946', width=2)))
        fig_eval.add_trace(go.Scatter(x=k_range, y=silhouettes, mode='lines+markers', name='Silhouette Score', yaxis='y2', line=dict(color='#457B9D', width=2, dash='dot')))

        fig_eval.update_layout(
            title="Curva do Cotovelo e Coeficiente de Silhueta para Avaliação de k",
            xaxis=dict(title="Número de Clusters (k)", tickmode='linear', dtick=1),
            yaxis=dict(title="Inércia", titlefont=dict(color="#E63946"), tickfont=dict(color="#E63946")),
            yaxis2=dict(title="Silhouette Score", titlefont=dict(color="#457B9D"), tickfont=dict(color="#457B9D"), overlaying='y', side='right'),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig_eval, use_container_width=True)

    col_k1, col_k2 = st.columns([1.2, 0.8])

    with col_k1:
        st.markdown("**Projeção 2D dos Clusters (Redução por PCA)**")
        var_expl = pca_2d.explained_variance_ratio_ * 100
        fig_pca = px.scatter(
            df_clusterizado,
            x='PCA1',
            y='PCA2',
            color='Cluster',
            hover_name='name',
            hover_data=['type1', 'type2', 'base_total', 'is_legendary'] + features_selecionadas,
            title=f"Espaço Latente PCA: PC1 ({var_expl[0]:.1f}%) vs PC2 ({var_expl[1]:.1f}%)",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_pca, use_container_width=True)

    with col_k2:
        st.markdown("**Distribuição de Pokémons por Cluster**")
        dist_cluster = df_clusterizado['Cluster'].value_counts().reset_index()
        dist_cluster.columns = ['Cluster', 'Contagem']
        fig_pie = px.pie(
            dist_cluster,
            names='Cluster',
            values='Contagem',
            title="Proporção de Pokémons em Cada Grupo",
            hole=0.4,
            color='Cluster',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Perfil Médio dos Clusters (Radar Chart e Tabela)
    st.markdown("---")
    st.markdown("### 🕸️ Perfil Médio de Atributos por Cluster (Radar Chart)")

    radar_features = [f for f in ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed'] if f in features_selecionadas]
    if len(radar_features) >= 3:
        cluster_means = df_clusterizado.groupby('Cluster')[radar_features].mean().reset_index()

        fig_radar = go.Figure()
        colors = px.colors.qualitative.Bold
        for idx, row in cluster_means.iterrows():
            cluster_name = row['Cluster']
            values = row[radar_features].tolist()
            values += [values[0]] # fechar o polígono
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=radar_features + [radar_features[0]],
                fill='toself',
                name=cluster_name,
                line=dict(color=colors[idx % len(colors)])
            ))

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, max(df_clusterizado[radar_features].max()) + 10])),
            showlegend=True,
            title="Comparação de Perfis Médios dos Clusters"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("#### Médias Resumidas por Cluster")
    resumo_clusters = df_clusterizado.groupby('Cluster')[features_selecionadas + ['base_total', 'is_legendary']].mean()
    resumo_clusters['Contagem'] = df_clusterizado.groupby('Cluster').size()
    resumo_clusters['% Lendários'] = (resumo_clusters['is_legendary'] * 100).round(1)
    resumo_clusters = resumo_clusters.drop(columns=['is_legendary'])
    st.dataframe(resumo_clusters.style.format("{:.1f}").background_gradient(cmap="Blues"), use_container_width=True)

# -------------------------------------------------------------
# ABA 3: POKÉDEX & COMPARADOR INDIVIDUAL
# -------------------------------------------------------------
with tab_pokedex:
    st.subheader("Explorador Individual de Pokémon & Comparação")

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.markdown("#### Ficha do Pokémon Selecionado")
        nomes_disponiveis = sorted(df_clusterizado['name'].unique())
        nome_selecionado = st.selectbox("Selecione um Pokémon:", options=nomes_disponiveis)
        pkm = df_clusterizado[df_clusterizado['name'] == nome_selecionado].iloc[0]

        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{int(pkm['pokedex_number'])}.png"

        st.image(sprite_url, width=140)
        st.markdown(f"**Nº Dex:** #{int(pkm['pokedex_number']):03d} | **Nome:** {pkm['name']}")
        st.markdown(f"**Tipagem:** `{pkm['type1']}`" + (f" / `{pkm['type2']}`" if pkm['type2'] != 'None' else ""))
        st.markdown(f"**Grupo Identificado:** **{pkm['Cluster']}**")
        st.markdown(f"**Status Lendário:** {'🌟 Sim' if pkm['is_legendary'] == 1 else 'Não'}")

        # Mini radar do Pokémon
        stats_rad = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        pkm_vals = [pkm[s] for s in stats_rad]
        pkm_vals += [pkm_vals[0]]

        fig_pkm_rad = go.Figure(data=go.Scatterpolar(
            r=pkm_vals,
            theta=stats_rad + [stats_rad[0]],
            fill='toself',
            name=pkm['name'],
            line_color='#E63946'
        ))
        fig_pkm_rad.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 200])),
            showlegend=False,
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_pkm_rad, use_container_width=True)

    with col_p2:
        st.markdown("#### Comparador Lado a Lado")
        pkms_comparar = st.multiselect(
            "Selecione 2 ou mais Pokémons para comparar:",
            options=nomes_disponiveis,
            default=[nome_selecionado, nomes_disponiveis[(nomes_disponiveis.index(nome_selecionado) + 1) % len(nomes_disponiveis)]]
        )

        if len(pkms_comparar) > 0:
            df_comp = df_clusterizado[df_clusterizado['name'].isin(pkms_comparar)]
            fig_comp = go.Figure()
            for _, row_c in df_comp.iterrows():
                vals = [row_c[s] for s in stats_rad]
                vals += [vals[0]]
                fig_comp.add_trace(go.Scatterpolar(
                    r=vals,
                    theta=stats_rad + [stats_rad[0]],
                    fill='toself',
                    name=f"{row_c['name']} ({row_c['Cluster']})"
                ))
            fig_comp.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 255])),
                title="Comparativo de Stats",
                height=380
            )
            st.plotly_chart(fig_comp, use_container_width=True)

            st.dataframe(df_comp[['pokedex_number', 'name', 'type1', 'type2', 'base_total', 'Cluster'] + stats_rad], use_container_width=True)

# -------------------------------------------------------------
# ABA 4: DADOS & EXPORTAÇÃO
# -------------------------------------------------------------
with tab_tabela:
    st.subheader("Base de Dados Completa com Atribuição de Clusters")
    colunas_exibir = ['pokedex_number', 'name', 'type1', 'type2', 'generation', 'is_legendary', 'Cluster', 'base_total'] + features_selecionadas
    st.dataframe(df_clusterizado[colunas_exibir], use_container_width=True)

    csv_data = df_clusterizado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Clusterizados em CSV",
        data=csv_data,
        file_name="pokemon_clusters.csv",
        mime="text/csv"
    )
