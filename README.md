# Projeto Final: Agrupamento, EDA e Dashboard Interativo
**Disciplina:** Análise e Visualização de Dados (AVD) — 2026.2  
**Avaliação:** AV2  

Este projeto tem como objetivo aplicar, de ponta a ponta, os conceitos estudados ao longo do semestre na disciplina de Análise e Visualização de Dados (AVD): exploração de dados (EDA), técnicas de agrupamento não supervisionado (K-Means), avaliação por métricas de validação, boas práticas de visualização e comunicação de resultados através de um dashboard interativo.

---

## 📁 Estrutura de Pastas do Repositório

O projeto segue rigorosamente a estrutura oficial exigida pela disciplina:

```text
Projeto_AVD/
├─ README.md                               # Instruções de instalação, execução e matriz de contribuição
├─ requirements.txt                        # Dependências do projeto (Python 3.11+)
├─ docs/
│  ├─ DECLARACAO_IA.pdf                    # Declaração assinada por todos os integrantes
│  └─ DECLARACAO_IA.md                     # Modelo base para assinatura da declaração
├─ data/
│  ├─ parte_comum/
│  │  └─ winequality-red.csv               # Dataset Wine Quality (Vinhos Tintos)
│  └─ parte_especifica/
│     ├─ pokemon.csv                       # The Complete Pokemon Dataset (Kaggle)
│     └─ download_pokemon.py               # Script de download automatizado do dataset
├─ out/
│  ├─ parte_comum/                         # Saídas e figuras exportadas da parte comum
│  └─ parte_especifica/                    # Saídas e figuras exportadas da parte específica
├─ notebooks/
│  └─ parte_comum/
│     └─ eda.ipynb                         # EDA, K-Means e métricas da Parte Comum
├─ src/
│  └─ parte_especifica/
│     ├─ eda.ipynb                         # Análise exploratória e K-Means do dataset Pokémon
│     ├─ dashboard.py                      # Aplicação interativa em Streamlit
│     └─ frontend/                         # EXTRA opcional (HTML/JS) — fora da avaliação
│        ├─ index.html                     # Interface Web TCG com efeito Holo & Showdown
│        ├─ style.css                      # Estilos personalizados e animações de cartas
│        ├─ app.js                         # Lógica interativa, áudio cries e radar charts
│        └─ pokemon_data.js                # Base dos 801 Pokémons com clusters K-Means
└─ relatorio.pdf                           # Relatório técnico completo do projeto (em PDF)
```

---

## 📊 Datasets Utilizados

### 1. Parte Comum: Wine Quality (Red Wine)
- **Fonte:** UCI Machine Learning Repository / Cortez et al.
- **Descrição:** Conjunto de dados com propriedades físico-químicas de amostras de vinho tinto (acidez, açúcar residual, cloretos, dióxido de enxofre, álcool, pH, sulfatos) e a nota sensorial de qualidade atribuída por especialistas.
- **Objetivo:** Exploração estatística e identificação de agrupamentos físico-químicos via K-Means comparados à nota de qualidade.

### 2. Parte Específica: The Complete Pokémon Dataset
- **Fonte:** [Kaggle - The Complete Pokemon Dataset (Rounak Banik)](https://www.kaggle.com/datasets/rounakbanik/pokemon)
- **Descrição:** Conjunto de dados detalhado contendo 801 Pokémons das Gerações 1 a 7, cobrindo:
  - Atributos base de combate: `hp`, `attack`, `defense`, `sp_attack`, `sp_defense`, `speed` e `base_total`.
  - Classificação, tipos primários e secundários (`type1`, `type2`), peso, altura e status lendário (`is_legendary`).
- **Objetivo:** Descobrir arquétipos naturais de combate (Tanques, Sweepers/Atacantes Ágeis, Estágios Iniciais e Lendários/Titãs) através de K-Means, avaliando hiperparâmetros (Elbow, Silhueta, Davies-Bouldin) e disponibilizando uma interface interativa em Streamlit.
- **Aprovação:** dataset aprovado pelo professor no checkpoint de **27/10/2026**.
- **Pergunta de pesquisa:** *O aumento do poder de combate (`base_total`) ao longo das 7 gerações — o chamado power creep — atinge os Pokémon comuns ou é explicado pela maior presença de lendários nas gerações mais recentes?* (detalhes, público-alvo e storytelling na seção 1 do notebook `src/parte_especifica/eda.ipynb`).

### Visualizações da Parte Específica (`out/parte_especifica/`)
| Tipo | Arquivo | Conteúdo |
| :--- | :--- | :--- |
| Exploratória 1 | `1_distribuicao_stats.png` | Histogramas dos 6 atributos de combate |
| Exploratória 2 | `2_frequencia_tipos.png` | Frequência por tipo primário |
| Exploratória 3 | `3_matriz_correlacao.png` | Matriz de correlação de Pearson |
| Exploratória 4 | `4_ataque_vs_defesa.png` | Ataque × Defesa com lendários em destaque |
| Técnico (método) | `5_metricas_cotovelo_silhueta.png`, `6_clusters_pca.png` | Escolha/validação do k — **não** são explanatórios |
| Apoio (outliers) | `7_boxplots_outliers.png` | Boxplots + regra IQR |
| **Explanatória 1** | `8_explanatoria_power_creep.png` | Poder médio por geração (todos vs comuns) e % de lendários — responde à pergunta de pesquisa |
| **Explanatória 2** | `9_explanatoria_titas_por_geracao.png` | Participação de cada geração no cluster de maior poder (lendários vs comuns) |

---

## ⚙️ Pré-requisitos e Instalação

Recomenda-se a utilização do **Python 3.11** ou superior e a criação de um ambiente virtual isolado.

### 1. Clonar o repositório
```bash
git clone https://github.com/gabimontcruz/Projeto_AVD.git
cd Projeto_AVD
```

### 2. Criar e ativar o ambiente virtual
**No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências
```bash
pip install -r requirements.txt
```

---

## 🚀 Como Executar

### 1. Executar o Dashboard Interativo (Streamlit)
O aplicativo interativo da Parte Específica está localizado em `src/parte_especifica/dashboard.py`:

```bash
streamlit run src/parte_especifica/dashboard.py
```
O dashboard será aberto automaticamente no seu navegador padrão (em `http://localhost:8501`). Nele é possível:
- Filtrar Pokémons por Geração (1 a 7), Tipos e Status de Lendário.
- Ajustar dinamicamente o número de clusters $k$ e escolher as variáveis de combate.
- Visualizar em tempo real as métricas do modelo (Curva do Cotovelo, Silhouette Score e Davies-Bouldin).
- Analisar a projeção 2D (PCA) e a contagem de Pokémon por cluster (gráfico de barras).
- Ver as 4 visualizações exploratórias e as 2 explanatórias que respondem à pergunta de pesquisa.
- Explorar a Pokédex individual com sprites oficiais e comparar dois ou mais Pokémons lado a lado.
- Exportar a base com os clusters atribuídos em CSV.

### 2. (Extra, fora da avaliação) Front-end Web Interativo (PokéAPI + Holo TCG)
> [!NOTE]
> A pasta `src/parte_especifica/frontend/` (HTML/CSS/JS) é um **extra opcional** feito pelo grupo e **não faz parte da entrega avaliada**, pois usa tecnologias fora das bibliotecas permitidas pela disciplina. Toda a análise e o dashboard oficial estão em Python (notebook + Streamlit).

Para uma experiência visual rica com efeitos holográficos, sprites animados Showdown e sons reais (Cries) da PokéAPI:

```bash
# Executar a partir da raiz do repositório:
python -m http.server 3000 --directory src/parte_especifica/frontend
```
Acesse no navegador: 👉 `http://localhost:3000`

### 3. Executar os Notebooks Jupyter
Para visualizar e reproduzir as análises exploratórias e experimentos de agrupamento:

```bash
jupyter lab
# ou
jupyter notebook
```

Abra os notebooks nas pastas correspondentes:
- **Parte Comum:**
  - `notebooks/parte_comum/eda.ipynb`
- **Parte Específica:**
  - `src/parte_especifica/eda.ipynb`

### 3. (Opcional) Rebaixar o Dataset de Pokémon
Caso queira atualizar ou rebaixar o dataset Pokémon automaticamente:
```bash
python data/parte_especifica/download_pokemon.py
```

---

## 👥 Matriz de Contribuição dos Integrantes

| Integrante | Matrícula | Responsabilidades / Contribuições Principais | Commits Registrados |
| :--- | :---: | :--- | :---: |
| **Integrante 1** | Matrícula | EDA e K-Means da Parte Comum (`eda.ipynb` e `kmeans_metricas.ipynb`) | Sim |
| **Integrante 2** | Matrícula | EDA, pré-processamento e K-Means do dataset Pokémon (`src/parte_especifica/eda.ipynb`) | Sim |
| **Integrante 3** | Matrícula | Desenvolvimento do Dashboard Interativo em Streamlit (`src/parte_especifica/dashboard.py`) | Sim |
| **Integrante 4** | Matrícula | Redação do Relatório Técnico em PDF (`relatorio.pdf`), métricas visuais e revisão geral | Sim |

---

## 📝 Declaração de Uso de IA
Conforme exigido nas diretrizes do projeto, a declaração de uso de IA encontra-se em `docs/DECLARACAO_IA.pdf`, devidamente assinada por todos os 4 integrantes do grupo.
