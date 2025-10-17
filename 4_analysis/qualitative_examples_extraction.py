"""
Qualitative Examples Extraction
================================
Extrai exemplos anônimos representativos de cada categoria para enriquecer a análise qualitativa.
"""

import pandas as pd
import json
import hashlib
from pathlib import Path
from collections import defaultdict
import re

class QualitativeExamplesExtractor:
    def __init__(self, tagged_data_path):
        """Inicializa o extrator com o caminho dos dados taggeados."""
        self.df = pd.read_csv(tagged_data_path)
        self.examples = defaultdict(list)
        
    def anonymize_author(self, author_id):
        """Anonimiza o ID do autor usando hash."""
        if pd.isna(author_id):
            return "Anonymous"
        hash_obj = hashlib.md5(str(author_id).encode())
        return f"User_{hash_obj.hexdigest()[:8]}"
    
    def clean_text(self, text, max_length=500):
        """Limpa e trunca o texto para exibição."""
        if pd.isna(text):
            return ""
        
        # Remove múltiplos espaços e quebras de linha
        text = re.sub(r'\s+', ' ', str(text))
        
        # Trunca se muito longo
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
    
    def extract_quote(self, text, max_words=100):
        """Extrai uma citação representativa do texto."""
        if pd.isna(text):
            return ""
        
        # Pega primeiras sentenças até atingir max_words
        sentences = re.split(r'[.!?]\s+', str(text))
        quote = ""
        word_count = 0
        
        for sentence in sentences:
            words = sentence.split()
            if word_count + len(words) > max_words:
                break
            quote += sentence + ". "
            word_count += len(words)
        
        return quote.strip()
    
    def extract_examples_by_root_cause(self, n_per_category=5):
        """Extrai exemplos representativos por categoria de causa raiz."""
        print("Extraindo exemplos por causa raiz...")
        
        for category in self.df['root_cause_category'].unique():
            if pd.isna(category) or category == 'unclear':
                continue
                
            category_df = self.df[self.df['root_cause_category'] == category]
            
            # Pega exemplos variados (diferentes fontes e períodos)
            examples = []
            for source in category_df['source'].unique():
                source_examples = category_df[category_df['source'] == source].sample(
                    min(2, len(category_df[category_df['source'] == source]))
                )
                examples.append(source_examples)
            
            combined = pd.concat(examples).head(n_per_category)
            
            for _, row in combined.iterrows():
                example = {
                    'category': category,
                    'source': row['source'],
                    'timestamp': row['timestamp'],
                    'author': self.anonymize_author(row.get('author_id')),
                    'quote': self.extract_quote(row['raw_text']),
                    'full_text': self.clean_text(row['raw_text'], max_length=1000),
                    'resolution': row.get('resolution_status', 'unknown'),
                    'url': row.get('url', '')
                }
                self.examples[f'root_cause_{category}'].append(example)
    
    def extract_examples_by_resolution(self, n_per_status=5):
        """Extrai exemplos por status de resolução."""
        print("Extraindo exemplos por status de resolução...")
        
        for status in self.df['resolution_status'].unique():
            if pd.isna(status):
                continue
                
            status_df = self.df[self.df['resolution_status'] == status]
            sample = status_df.sample(min(n_per_status, len(status_df)))
            
            for _, row in sample.iterrows():
                example = {
                    'resolution_status': status,
                    'source': row['source'],
                    'timestamp': row['timestamp'],
                    'author': self.anonymize_author(row.get('author_id')),
                    'quote': self.extract_quote(row['raw_text']),
                    'root_cause': row.get('root_cause_category', 'unclear'),
                    'url': row.get('url', '')
                }
                self.examples[f'resolution_{status}'].append(example)
    
    def extract_examples_by_temporal_period(self, n_per_period=3):
        """Extrai exemplos por período temporal."""
        print("Extraindo exemplos por período temporal...")
        
        for period in self.df['temporal_period'].unique():
            if pd.isna(period):
                continue
                
            period_df = self.df[self.df['temporal_period'] == period]
            sample = period_df.sample(min(n_per_period, len(period_df)))
            
            for _, row in sample.iterrows():
                example = {
                    'period': period,
                    'source': row['source'],
                    'timestamp': row['timestamp'],
                    'author': self.anonymize_author(row.get('author_id')),
                    'quote': self.extract_quote(row['raw_text']),
                    'root_cause': row.get('root_cause_category', 'unclear'),
                    'resolution': row.get('resolution_status', 'unknown'),
                    'url': row.get('url', '')
                }
                self.examples[f'temporal_{period}'].append(example)
    
    def extract_interesting_cases(self):
        """Extrai casos particularmente interessantes ou ilustrativos."""
        print("Extraindo casos interessantes...")
        
        # Casos resolvidos com workarounds
        resolved_df = self.df[
            (self.df['resolution_status'] == 'resolved') & 
            (self.df['root_cause_category'] != 'unclear')
        ]
        
        if len(resolved_df) > 0:
            for _, row in resolved_df.head(3).iterrows():
                example = {
                    'type': 'successful_resolution',
                    'source': row['source'],
                    'timestamp': row['timestamp'],
                    'author': self.anonymize_author(row.get('author_id')),
                    'quote': self.extract_quote(row['raw_text']),
                    'full_text': self.clean_text(row['raw_text'], max_length=1500),
                    'root_cause': row.get('root_cause_category'),
                    'url': row.get('url', '')
                }
                self.examples['interesting_cases'].append(example)
        
        # Casos não resolvidos persistentes
        unresolved_df = self.df[
            (self.df['resolution_status'] == 'unresolved') & 
            (self.df['root_cause_category'] != 'unclear')
        ]
        
        if len(unresolved_df) > 0:
            for _, row in unresolved_df.head(3).iterrows():
                example = {
                    'type': 'persistent_issue',
                    'source': row['source'],
                    'timestamp': row['timestamp'],
                    'author': self.anonymize_author(row.get('author_id')),
                    'quote': self.extract_quote(row['raw_text']),
                    'full_text': self.clean_text(row['raw_text'], max_length=1500),
                    'root_cause': row.get('root_cause_category'),
                    'url': row.get('url', '')
                }
                self.examples['interesting_cases'].append(example)
    
    def generate_markdown_report(self, output_path):
        """Gera relatório em Markdown com os exemplos."""
        print("Gerando relatório Markdown...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Análise Qualitativa Enriquecida: Exemplos Anônimos de Discussões\n\n")
            f.write("Este documento apresenta exemplos anônimos representativos extraídos das discussões da comunidade Service Weaver, ")
            f.write("organizados por categoria de problema, status de resolução e período temporal.\n\n")
            f.write("---\n\n")
            
            # Exemplos por Causa Raiz
            f.write("## 1. Exemplos por Categoria de Causa Raiz\n\n")
            f.write("Cada categoria apresenta exemplos reais (anonimizados) que ilustram os tipos de problemas enfrentados.\n\n")
            
            root_cause_categories = sorted([k for k in self.examples.keys() if k.startswith('root_cause_')])
            for cat_key in root_cause_categories:
                category = cat_key.replace('root_cause_', '')
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                
                for i, example in enumerate(self.examples[cat_key], 1):
                    f.write(f"**Exemplo {i}** ({example['source']} - {example['timestamp'][:10]})\n\n")
                    f.write(f"> *{example['author']}:*\n")
                    f.write(f"> \n")
                    f.write(f"> {example['quote']}\n\n")
                    f.write(f"**Status de Resolução:** {example['resolution']}\n\n")
                    f.write("---\n\n")
            
            # Exemplos por Status de Resolução
            f.write("## 2. Exemplos por Status de Resolução\n\n")
            
            resolution_statuses = sorted([k for k in self.examples.keys() if k.startswith('resolution_')])
            for res_key in resolution_statuses:
                status = res_key.replace('resolution_', '')
                f.write(f"### {status.replace('_', ' ').title()}\n\n")
                
                for i, example in enumerate(self.examples[res_key][:3], 1):
                    f.write(f"**Exemplo {i}** ({example['source']})\n\n")
                    f.write(f"> {example['quote']}\n\n")
                    f.write(f"**Causa Raiz:** {example['root_cause']}\n\n")
                    f.write("---\n\n")
            
            # Exemplos por Período Temporal
            f.write("## 3. Evolução Temporal das Discussões\n\n")
            
            temporal_periods = sorted([k for k in self.examples.keys() if k.startswith('temporal_')])
            for temp_key in temporal_periods:
                period = temp_key.replace('temporal_', '')
                f.write(f"### {period.replace('_', ' ').title()}\n\n")
                
                for i, example in enumerate(self.examples[temp_key], 1):
                    f.write(f"**Exemplo {i}**\n\n")
                    f.write(f"> {example['quote']}\n\n")
                    f.write("---\n\n")
            
            # Casos Interessantes
            if 'interesting_cases' in self.examples:
                f.write("## 4. Casos Particularmente Ilustrativos\n\n")
                f.write("Exemplos que demonstram padrões importantes na comunidade.\n\n")
                
                for example in self.examples['interesting_cases']:
                    f.write(f"### {example['type'].replace('_', ' ').title()}\n\n")
                    f.write(f"**Fonte:** {example['source']} | **Data:** {example['timestamp'][:10]}\n\n")
                    f.write(f"**Causa Raiz:** {example['root_cause']}\n\n")
                    f.write(f"> *{example['author']}:*\n")
                    f.write(f"> \n")
                    f.write(f"> {example['full_text']}\n\n")
                    f.write("---\n\n")
            
            f.write("\n## Nota sobre Anonimização\n\n")
            f.write("Todos os IDs de autores foram anonimizados usando hashing MD5. ")
            f.write("Os textos foram mantidos integralmente (ou truncados quando muito longos) ")
            f.write("para preservar o contexto e a autenticidade das discussões.\n")
    
    def save_examples_json(self, output_path):
        """Salva os exemplos em formato JSON."""
        print(f"Salvando exemplos em JSON: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.examples, f, indent=2, ensure_ascii=False)
    
    def run_extraction(self, output_dir='4_analysis'):
        """Executa toda a extração de exemplos."""
        print("Iniciando extração de exemplos qualitativos...")
        
        self.extract_examples_by_root_cause()
        self.extract_examples_by_resolution()
        self.extract_examples_by_temporal_period()
        self.extract_interesting_cases()
        
        # Salva os resultados
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        markdown_file = output_path / 'qualitative_examples.md'
        json_file = output_path / 'qualitative_examples.json'
        
        self.generate_markdown_report(markdown_file)
        self.save_examples_json(json_file)
        
        print(f"\n✓ Relatório Markdown salvo: {markdown_file}")
        print(f"✓ Exemplos JSON salvos: {json_file}")
        print(f"\nTotal de categorias com exemplos: {len(self.examples)}")
        
        # Resumo
        total_examples = sum(len(examples) for examples in self.examples.values())
        print(f"Total de exemplos extraídos: {total_examples}")
        
        return self.examples


if __name__ == "__main__":
    # Configura os caminhos
    tagged_data_path = "3_processed_data/tagged_dataset.csv"
    output_dir = "4_analysis"
    
    # Executa a extração
    extractor = QualitativeExamplesExtractor(tagged_data_path)
    examples = extractor.run_extraction(output_dir)
    
    print("\n" + "="*60)
    print("Extração de exemplos qualitativos concluída!")
    print("="*60)
