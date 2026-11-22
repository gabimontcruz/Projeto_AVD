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
│     ├─ eda.ipynb                         # Análise exploratória da Parte Comum
│     └─ kmeans_metricas.ipynb             # K-Means e avaliação de métricas da Parte Comum
├─ src/
│  ├─ parte_comum/                         # Scripts complementares da Parte Comum
│  └─ parte_especifica/
│     ├─ eda.ipynb                         # Análise exploratória e K-Means do dataset Pokémon
│     └─ dashboard.py                      # Aplicação interativa em Streamlit
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

---

## ⚙️ Pré-requisitos e Instalação

Recomenda-se a utilização do **Python 3.11** ou superior e a criação de um ambiente virtual isolado.

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/Projeto_AVD.git
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
- Analisar a projeção 2D (PCA) e a distribuição 3D dos clusters.
- Inspecionar o gráfico de radar (Spider Chart) com o perfil médio de cada arquétipo.
- Explorar a Pokédex individual com sprites oficiais e comparar dois ou mais Pokémons lado a lado.
- Exportar a base com os clusters atribuídos em CSV.

### 2. Executar os Notebooks Jupyter
Para visualizar e reproduzir as análises exploratórias e experimentos de agrupamento:

```bash
jupyter lab
# ou
jupyter notebook
```

Abra os notebooks nas pastas correspondentes:
- **Parte Comum:**
  - `notebooks/parte_comum/eda.ipynb`
  - `notebooks/parte_comum/kmeans_metricas.ipynb`
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
