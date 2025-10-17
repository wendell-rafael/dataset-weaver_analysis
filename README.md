# Service Weaver Analysis Dataset

**Dataset de Arqueologia Digital: Análise da Descontinuação do Service Weaver**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Sobre o Dataset

Este dataset documenta a trajetória completa do **Service Weaver**, um framework Go para desenvolvimento de aplicações modulares criado pelo Google, desde seu lançamento em março de 2023 até sua descontinuação em dezembro de 2024.

### Objetivo

Fornecer um **dataset estruturado e reproduzível** para pesquisas em:
- **Arqueologia de Software**: Análise post-mortem de projetos descontinuados
- **Engenharia de Software Empírica**: Estudos sobre adoção, manutenção e declínio de frameworks
- **Mineração de Repositórios**: Análise de discussões técnicas em múltiplas plataformas
- **Análise de Sentimento**: Percepção da comunidade sobre decisões técnicas

---

## Composição do Dataset

### Fontes de Dados Coletadas

O dataset agrega **1.035+ registros** de 5 fontes diferentes:

| Fonte | Tipos de Dados | Volume | Período Coberto |
|-------|---------------|--------|-----------------|
| **GitHub** | Issues, Pull Requests, Comentários | ~750+ registros | Mar/2023 - Mai/2025 |
| **Hacker News** | Stories, Comentários | ~250+ registros | 2023 - 2025 |
| **Reddit** | Posts, Comentários | ~20+ registros | 2009 - 2024 |
| **Stack Overflow** | Perguntas, Respostas | 0* (API limitada) | - |
| **Google Groups** | Threads, Mensagens | 0* (robots.txt) | - |

*\*Fontes bloqueadas ou com restrições de acesso*

### Estrutura dos Dados

Cada registro contém:
- **`source`**: Origem do dado (github_issue, github_pr, reddit, hackernews_story, etc.)
- **`data_id`**: Identificador único (ex: gh_issue_816, reddit_11hkh43)
- **`timestamp`**: Data/hora de criação no formato ISO 8601
- **`raw_text`**: Conteúdo textual completo (título + corpo + comentários)
- **`author_id`**: Hash anonimizado do autor (SHA-256)
- **`url`**: Link direto para o recurso original
- **`metadata`**: JSON com informações específicas da plataforma

### Tags Aplicadas (Camadas de Codificação)

#### **Temporal Period** (Periodização Histórica)
Classifica registros em 5 fases do ciclo de vida:

- **`pre_launch`** (< Mar/2023): Discussões anteriores ao lançamento
- **`early_adoption`** (Mar-Jun/2023): Fase inicial de adoção
- **`plateau`** (Jun/2023-Jun/2024): Maturidade e estabilização
- **`decline`** (Jun-Dez/2024): Sinais de declínio
- **`post_discontinuation`** (> Dez/2024): Após anúncio oficial

#### **Resolution Status** (Status de Resolução)
Indica o desfecho de issues/discussões:

- **`unknown`**: Status não determinado (85% dos casos)
- **`acknowledged_not_fixed`**: Problema reconhecido mas não resolvido
- **`fixed`**: Resolvido
- **`abandoned`**: Abandonado sem resolução
- **`wontfix`**: Marcado como "não será corrigido"

#### **Root Cause Category** (Categoria de Causa Raiz)
Classifica problemas/discussões por origem:

- **`unclear`**: Causa não identificada
- **`architectural_limitation`**: Limitações arquiteturais
- **`community_mismatch`**: Desalinhamento com necessidades da comunidade
- **`technical_debt`**: Dívida técnica acumulada
- **`resource_constraint`**: Falta de recursos (tempo, pessoas, orçamento)

---

## Metodologia de Coleta

### Pipeline Automatizado

```
1. COLETA → 2. DEDUPLICAÇÃO → 3. ANONIMIZAÇÃO → 4. TAGGING → 5. ANÁLISE
```

1. **Coleta Multi-Fonte**: Scrapers Python com rate limiting e retry automático
2. **Deduplicação**: Remoção de duplicatas por hash de URL
3. **Anonimização**: Hash SHA-256 de identificadores de autores
4. **Tagging**: Sistema de tags em 3 camadas (temporal, resolução, causa raiz)
5. **Análise**: Estatísticas descritivas + visualizações

### Configuração Técnica

- **Rate Limiting**: 1 segundo entre requisições (GitHub), variável por API
- **Retry Policy**: 3 tentativas com backoff exponencial
- **Período**: Mar/2023 - Dez/2024 (com alguns registros fora do período)
- **Credenciais**: GitHub Token, Reddit API (configuráveis via `.env`)

---

## Como Usar Este Dataset

### Instalação Rápida

```powershell
# 1. Clone o repositório
git clone <seu-repo-url>
cd service_weaver_analysis

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure credenciais (opcional para re-coletar)
copy .env.example .env
notepad .env  # Adicione suas API keys
```

### Uso Básico: Carregar Dataset Processado

```python
import pandas as pd

# Carregar dataset taggeado (pronto para análise)
df = pd.read_csv('3_processed_data/tagged_dataset.csv')

# Explorar estrutura
print(df.columns)
print(df['temporal_period'].value_counts())
print(df.groupby(['source', 'temporal_period']).size())
```

### Re-executar Coleta (Atualizar Dataset)

```powershell
# Coletar novos dados
python -m 1_data_collection.scrapers.collect_all

# Combinar e taggear
python -c "
import pandas as pd, glob
dfs = [pd.read_csv(f) for f in glob.glob('1_data_collection/raw_datasets/*_raw_*.csv')]
pd.concat(dfs).to_csv('3_processed_data/combined_raw_data.csv', index=False)
"

python 2_coding_methodology/tag_layering.py 3_processed_data/combined_raw_data.csv
```

### Análise e Visualização

```powershell
# Gerar análise estatística
python -c "exec(open('scripts/analyze.py').read())"

# Gerar visualizações
python -c "exec(open('scripts/visualize.py').read())"
```

---

## Adaptando para Outros Projetos

### Passo 1: Configurar Novo Alvo

Edite `config.yaml`:

```yaml
project_name: seu_projeto_aqui

sources:
  github:
    repository: Organization/repository-name  # Mude aqui
    
  reddit:
    subreddits: [subreddit1, subreddit2]
    keywords: [keyword1, keyword2]
    
  hackernews:
    keywords: [projeto_nome]
```

### Passo 2: Ajustar Períodos Temporais

```yaml
date_range:
  start: '2020-01-01'  # Data de lançamento do projeto
  end: '2024-12-31'    # Data de análise/descontinuação

tagging:
  temporal_periods:
    pre_launch: '2020-01-01'
    early_adoption: '2020-06-30'
    plateau: '2023-01-01'
    decline: '2024-06-30'
```

### Passo 3: Re-coletar e Processar

```powershell
python -m 1_data_collection.scrapers.collect_all
python 2_coding_methodology/tag_layering.py 3_processed_data/combined_raw_data.csv
```

### Passo 4: Codificação Manual (Opcional)

Para análise aprofundada, codifique manualmente uma amostra:

```powershell
# Ferramenta auxiliar de double-coding
python 2_coding_methodology/double_code_tool.py --help
```

---

## 📂 Estrutura de Arquivos

---

## 📂 Estrutura do Projeto

```
service_weaver_analysis/
├── 1_data_collection/          # Coleta de dados
│   ├── scrapers/               # Scripts de scraping
│   │   ├── collect_all.py      # Orquestrador principal
│   │   ├── github_scraper.py
│   │   ├── reddit_scraper.py
│   │   ├── stackoverflow_scraper.py
│   │   ├── hackernews_scraper.py
│   │   └── google_groups_scraper.py
│   └── raw_datasets/           # Dados brutos (CSV)
│
├── 2_coding_methodology/       # Codificação temática
│   ├── coding_scheme.json      # Esquema de categorias
│   ├── codebook.md             # Manual de codificação
│   ├── double_code_tool.py     # Ferramenta auxiliar
│   └── tag_layering.py         # Sistema de tags
│
├── 3_processed_data/           # Dados processados
│   └── tagged_data.csv         # Dataset final taggeado
│
├── 4_analysis/                 # Análises e visualizações
│   ├── statistical_analysis.py
│   ├── generate_visualizations.py
│   └── visualizations/         # Gráficos gerados
│
├── tests/                      # Testes unitários
├── config.yaml                 # Configuração
└── requirements.txt            # Dependências
```

---

## 🔬 Metodologia

### 1. Coleta de Dados
- **Fontes**: GitHub, Stack Overflow, Reddit, Hacker News, Google Groups
- **Período**: Mar/2023 (lançamento) - Dez/2024 (descontinuação)
- **Output**: CSVs em `raw_datasets/`

### 2. Codificação Temática
- Esquema hierárquico de categorias (6 principais, 24 sub-códigos)
- Ferramenta de double-coding para validação
- Output: Dados codificados em `3_processed_data/`

### 3. Tag Layering
- **Temporal**: pre_launch, early_adoption, plateau, decline, post_discontinuation
- **Resolução**: fixed, abandoned, wontfix, acknowledged_not_fixed
- **Root Cause**: architectural_limitation, community_mismatch, technical_debt, etc.

### 4. Análise & Visualização
- Análises estatísticas (χ², correlações)
- Visualizações interativas (timelines, heatmaps)
- Output: Gráficos em `4_analysis/visualizations/`

---

## ⚙️ Configuração

Edite `config.yaml` para personalizar:

```yaml
sources:
  github:
    enabled: true
    max_items: 5000
  
  reddit:
    enabled: true
    subreddits: ["golang", "microservices"]
```

---

## 🧪 Testes

```powershell
pytest tests/ -v
```

---

## � Dados

- **Dataset bruto**: `1_data_collection/raw_datasets/*.csv`
- **Dataset processado**: `3_processed_data/tagged_data.csv`
- **Visualizações**: `4_analysis/visualizations/`

---

## 📧 Contato

Para questões, abra uma issue no GitHub.

---

**Status**: 🚧 Em Desenvolvimento

**Atualizado**: Outubro 2025
