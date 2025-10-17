# Guia de Uso do Dataset - Service Weaver Analysis

Este guia fornece exemplos práticos de como utilizar o dataset para diferentes tipos de pesquisa.

---

## Estrutura Completa dos Arquivos

```
service_weaver_analysis/
├── 1_data_collection/              # Coleta de Dados
│   ├── scrapers/                   # Scripts especializados por plataforma
│   │   ├── collect_all.py          # Orquestrador principal
│   │   ├── github_scraper.py       # GitHub API (issues, PRs, discussões)
│   │   ├── reddit_scraper.py       # Reddit PRAW API
│   │   ├── stackoverflow_scraper.py # Stack Exchange API
│   │   ├── hackernews_scraper.py   # Firebase API
│   │   └── google_groups_scraper.py # Web scraping
│   ├── raw_datasets/               # CSVs brutos timestamped
│   ├── collection_report.md        # Relatório de coleta
│   └── collection_stats.json       # Estatísticas JSON
│
├── 2_coding_methodology/           # Codificação e Tagging
│   ├── coding_scheme.json          # Esquema hierárquico de categorias
│   ├── codebook.md                 # Manual de codificação (guidelines)
│   ├── double_code_tool.py         # Ferramenta de inter-rater reliability
│   └── tag_layering.py             # Sistema automático de tags
│
├── 3_processed_data/               # Dados Processados (DATASET FINAL)
│   ├── combined_raw_data.csv       # Dados brutos combinados
│   └── tagged_dataset.csv          # DATASET PRINCIPAL (1035+ registros)
│
├── 4_analysis/                     # Análises e Visualizações
│   ├── statistical_analysis.py     # Análises estatísticas
│   ├── generate_visualizations.py  # Gerador de gráficos
│   ├── analysis_results.json       # Resultados em JSON
│   └── visualizations/             # Gráficos PNG (5+ visualizações)
│       ├── 01_distribution_by_source.png
│       ├── 02_temporal_distribution.png
│       ├── 03_resolution_status.png
│       ├── 04_heatmap_source_temporal.png
│       └── 05_resolution_by_period.png
│
├── tests/                          # Testes Unitários
├── config.yaml                     # Configuração central
├── requirements.txt                # Dependências Python
├── README.md                       # Documentação principal
└── USAGE_GUIDE.md                  # Este guia
```

---

## Exemplos de Análise

### Análise Temporal da Atividade

```python
import pandas as pd
import matplotlib.pyplot as plt

# Carregar dataset
df = pd.read_csv('3_processed_data/tagged_dataset.csv')

# Distribuição temporal
temporal_dist = df['temporal_period'].value_counts()
print("Distribuição por Período:")
print(temporal_dist)

# Atividade por fonte ao longo do tempo
activity = df.groupby(['temporal_period', 'source']).size().unstack(fill_value=0)
activity.plot(kind='bar', stacked=True, figsize=(12,6))
plt.title('Atividade da Comunidade por Fase do Ciclo de Vida')
plt.xlabel('Período Temporal')
plt.ylabel('Número de Registros')
plt.legend(title='Fonte', bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig('custom_temporal_analysis.png')
plt.show()
```

**Output Esperado:**
```
Distribuição por Período:
early_adoption          420
plateau                 336
pre_launch              235
decline                  30
post_discontinuation     14
```

### Análise de Resolução de Issues

```python
# Issues resolvidas vs não resolvidas por período
resolution = pd.crosstab(
    df['temporal_period'], 
    df['resolution_status'], 
    normalize='index'
) * 100

print("Taxa de Resolução por Período (%):")
print(resolution.round(2))

# Visualizar tendência
resolution.plot(kind='line', marker='o', figsize=(10,6))
plt.title('Tendência de Resolução ao Longo do Tempo')
plt.ylabel('Percentual (%)')
plt.xlabel('Período')
plt.legend(title='Status')
plt.grid(True, alpha=0.3)
plt.show()
```

**Insight**: Mostra declínio na taxa de resolução conforme o projeto se aproxima da descontinuação.

### Mineração de Texto e Análise de Frequência

```python
from collections import Counter
import re

# Extrair palavras mais frequentes
all_text = ' '.join(df['raw_text'].dropna())
words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
common_words = Counter(words).most_common(30)

print("Termos técnicos mais discutidos:")
for word, count in common_words:
    print(f"{word:20s}: {count:5d}")

# Criar word cloud
from wordcloud import WordCloud

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Termos Mais Discutidos no Service Weaver')
plt.savefig('wordcloud_analysis.png', dpi=300, bbox_inches='tight')
plt.show()
```

### Análise de Sentimento por Período

```python
from textblob import TextBlob

# Calcular sentimento para cada registro
df['sentiment'] = df['raw_text'].apply(
    lambda x: TextBlob(str(x)[:5000]).sentiment.polarity if pd.notna(x) else 0
)

# Sentimento médio por período
sentiment_by_period = df.groupby('temporal_period')['sentiment'].agg(['mean', 'std', 'count'])
print("Sentimento por Período:")
print(sentiment_by_period)

# Visualizar
sentiment_by_period['mean'].plot(kind='line', marker='o', figsize=(10,6))
plt.title('Evolução do Sentimento da Comunidade')
plt.ylabel('Polaridade (-1 negativo, +1 positivo)')
plt.xlabel('Período')
plt.axhline(y=0, color='r', linestyle='--', alpha=0.3)
plt.grid(True, alpha=0.3)
plt.show()
```

---

## Casos de Uso para Pesquisa Acadêmica

### Caso 1: Estudo de Ciclo de Vida de Frameworks

**Pergunta de Pesquisa**: Como a atividade da comunidade evolui desde o lançamento até a descontinuação de um framework?

**Metodologia**:
```python
# Agregar métricas por período
lifecycle = df.groupby('temporal_period').agg({
    'data_id': 'count',  # Total de interações
    'source': lambda x: x.value_counts().to_dict(),  # Diversidade de fontes
    'resolution_status': lambda x: (x != 'unknown').sum()  # Issues com resolução
})

# Calcular taxa de engajamento
lifecycle['engagement_rate'] = lifecycle['resolution_status'] / lifecycle['data_id'] * 100
```

**Conferências Alvo**: MSR (Mining Software Repositories), ICSE, FSE

### Caso 2: Padrões de Contribuição Open Source

**Pergunta de Pesquisa**: Quais tipos de discussões dominam em diferentes fases do projeto?

**Metodologia**:
```python
# Distribuição de fontes por período
source_evolution = pd.crosstab(
    df['temporal_period'], 
    df['source'], 
    normalize='index'
) * 100

# Identificar mudanças significativas
print("Mudança na composição de fontes:")
print(source_evolution)

# Testar significância estatística
from scipy.stats import chi2_contingency
chi2, p_value, dof, expected = chi2_contingency(
    pd.crosstab(df['temporal_period'], df['source'])
)
print(f"Chi-square test: χ²={chi2:.2f}, p={p_value:.4f}")
```

**Conferências Alvo**: CSCW (Cooperative Work), OSS Conferences, CHI

### Caso 3: Sinais Precoces de Declínio

**Pergunta de Pesquisa**: É possível identificar sinais precoces de abandono de projetos?

**Metodologia**:
```python
# Issues não resolvidas acumuladas
decline_indicators = df[
    df['resolution_status'].isin(['acknowledged_not_fixed', 'abandoned'])
].groupby('temporal_period').agg({
    'data_id': 'count',
    'resolution_status': lambda x: x.value_counts().to_dict()
})

# Taxa de abandono crescente
abandon_rate = decline_indicators['data_id'] / df.groupby('temporal_period').size() * 100
abandon_rate.plot(kind='line', marker='o')
plt.title('Taxa de Issues Não Resolvidas ao Longo do Tempo')
plt.ylabel('% de Issues Não Resolvidas')
```

**Conferências Alvo**: ICSE-SEIP (Software Engineering in Practice), ESEM (Empirical Software Engineering)

### Caso 4: Análise de Tópicos (Topic Modeling)

**Pergunta de Pesquisa**: Quais são os temas técnicos dominantes em cada fase?

**Metodologia**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Preparar textos
texts = df['raw_text'].fillna('')

# TF-IDF
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
tfidf_matrix = vectorizer.fit_transform(texts)

# LDA Topic Modeling
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(tfidf_matrix)

# Exibir tópicos
feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    top_words = [feature_names[i] for i in topic.argsort()[-10:]]
    print(f"Tópico {topic_idx+1}: {', '.join(top_words)}")
```

**Conferências Alvo**: MSR, ASE (Automated Software Engineering), ICSE

---

## Adaptando para Outros Projetos

### Template: Analisar Projeto X

```python
# 1. Atualizar config.yaml
"""
project_name: projeto_x
sources:
  github:
    repository: org/projeto-x
date_range:
  start: '2020-01-01'
  end: '2024-12-31'
"""

# 2. Coletar dados
!python -m 1_data_collection.scrapers.collect_all

# 3. Combinar e processar
import pandas as pd, glob

dfs = [pd.read_csv(f) for f in glob.glob('1_data_collection/raw_datasets/*_raw_*.csv')]
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('3_processed_data/combined_raw_data.csv', index=False)

# 4. Aplicar tags
!python 2_coding_methodology/tag_layering.py 3_processed_data/combined_raw_data.csv

# 5. Analisar!
df = pd.read_csv('3_processed_data/tagged_dataset.csv')
print(df.describe())
```

---

## Troubleshooting Comum

### Problema 1: Erro de encoding ao ler CSVs

```python
# Solução: Force UTF-8
df = pd.read_csv('file.csv', encoding='utf-8-sig')
```

### Problema 2: Rate limit excedido (GitHub)

```yaml
# Em config.yaml, aumente o sleep
sources:
  github:
    rate_limit_sleep: 3  # de 1 para 3 segundos
```

### Problema 3: Memória insuficiente para grandes datasets

```python
# Ler em chunks
chunks = pd.read_csv('large_file.csv', chunksize=1000)
for chunk in chunks:
    process(chunk)  # Processar em partes
```

---

## Recursos Adicionais

### Bibliotecas Recomendadas

```python
# Análise de Texto
pip install textblob nltk spacy wordcloud

# Topic Modeling
pip install gensim scikit-learn

# Network Analysis
pip install networkx python-louvain

# Visualizações Avançadas
pip install plotly streamlit dash
```

### Tutoriais e Exemplos

- [Jupyter Notebook com exemplos](./notebooks/analysis_examples.ipynb)
- [Dashboard interativo](./notebooks/dashboard.py)
- [Scripts de análise prontos](./scripts/)

---

## Suporte

**Dúvidas técnicas**: Abra uma issue no repositório  
**Colaborações de pesquisa**: Entre em contato via email  
**Sugestões de melhorias**: Pull requests são bem-vindos

---

**Última Atualização**: 17 de Outubro de 2025
