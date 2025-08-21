# Automação de Compra de VR/VA

Sistema automatizado para cálculo mensal de Vale Refeição (VR), garantindo que cada colaborador receba o valor correto considerando ausências, férias, datas de admissão/desligamento e calendário de feriados.

## Objetivo

Automatizar o processo mensal de compra de VR, eliminando cálculos manuais e garantindo precisão nos valores considerando:
- Conferência de datas de início e fim do contrato no mês
- Exclusão de colaboradores em férias (parcial ou integral por regra de sindicato)
- Ajustes para datas quebradas (admissões no meio do mês e desligamentos)
- Cálculo do número exato de dias a serem comprados para cada pessoa
- Geração de layout de compra para envio ao fornecedor
- Aplicação das regras vigentes dos acordos coletivos de cada sindicato

## Estrutura do Projeto

```
vr_benefits/
├── src/
│   ├── agent_vr.py           # Agente LangChain com ReAct pattern
│   ├── tools_beneficios.py   # Lógica de negócio e cálculos
│   ├── util.py               # Funções utilitárias (datas, interseções)
│   └── run.py                # Interface CLI para execução
├── data/
│   ├── input/                # Planilhas de entrada
│   │   ├── ATIVOS.xlsx
│   │   ├── ADMISSÃO ABRIL.xlsx
│   │   ├── DESLIGADOS.xlsx
│   │   ├── FÉRIAS.xlsx
│   │   ├── AFASTAMENTOS.xlsx
│   │   ├── EXTERIOR.xlsx
│   │   ├── APRENDIZ.xlsx
│   │   ├── ESTÁGIO.xlsx
│   │   ├── Base sindicato x valor.xlsx
│   │   └── Base dias uteis.xlsx
│   └── template/
│       └── VR MENSAL 05.2025.xlsx
├── output/                   # Arquivos de saída
├── requirements.txt
├── .env.example
└── README.md
```

## Requisitos

### Sistema
- Python 3.8+
- Pandas 2.3.2+
- OpenPyXL 3.1.5+
- LangChain 0.3.27+
- LangChain-Groq (para modo LLM)

### Dados de Entrada
- 10 arquivos Excel específicos na pasta `data/input/`
- Template de saída em `data/template/`
- Arquivo `.env` com chaves de API (opcional, apenas para modo LLM)

## Instalação

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd vr_benefits

# 2. Criar ambiente virtual
python -m venv .venv

# 3. Ativar ambiente virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente (opcional - apenas para modo LLM)
cp .env.example .env
# Editar .env com sua GROQ_API_KEY
```

## Execução

### Modo Determinístico (Recomendado para Produção)

```bash
cd src
python run.py --mes 2025-05 --no-llm
```

### Modo LLM (com Agente Inteligente)

```bash
cd src
python run.py --mes 2025-06 --model llama3-70b-8192
```

### Parâmetros Disponíveis

- `--mes`: Competência no formato YYYY-MM (obrigatório)
- `--no-llm`: Execução determinística sem agente
- `--model`: Modelo LLM (padrão: llama3-70b-8192)
- `--input`: Diretório de entrada (padrão: ../data/input)
- `--output`: Diretório de saída (padrão: ../output)
- `--template`: Arquivo template (padrão: ../data/template/VR MENSAL 05.2025.xlsx)
- `--use-openai`: Usar OpenAI ao invés de Groq

## Funcionalidades Implementadas

### 1. Base Única Consolidada
- Reunião e consolidação de 5 bases separadas
- Processamento de Ativos, Férias, Desligados, Base cadastral, Base sindicato x valor e Dias úteis
- Normalização e validação de dados

### 2. Tratamento de Exclusões
- **Diretores**: Identificação automática por cargo (CEO, Diretor, Presidente, VP)
- **Estagiários**: Exclusão via arquivo ESTÁGIO.xlsx
- **Aprendizes**: Exclusão via arquivo APRENDIZ.xlsx
- **Afastados**: Processamento de licenças e afastamentos
- **Exterior**: Exclusão de profissionais atuando no exterior

### 3. Validação e Correção
- Tratamento de datas inconsistentes ou "quebradas"
- Validação de campos faltantes
- Correção de férias mal preenchidas
- Aplicação de feriados estaduais e municipais por região

### 4. Cálculo Automatizado do Benefício
- **Dias úteis por colaborador**: Considerando dias úteis de cada sindicato
- **Férias e afastamentos**: Desconto proporcional
- **Data de desligamento**: Cálculo proporcional ao período trabalhado
- **Regra de desligamento**: 
  - Comunicado até dia 15: Não considera para pagamento
  - Comunicado após dia 15: Compra proporcional

### 5. Feriados por Região
- **Feriados nacionais**: Confraternização, Tiradentes, Dia do Trabalhador, etc.
- **Feriados regionais**: 
  - São Paulo: Aniversário de São Paulo, Revolução Constitucionalista
  - Rio de Janeiro: São Jorge, Dia do Servidor Público
  - Paraná: Emancipação do Paraná
  - Rio Grande do Sul: Revolução Farroupilha

### 6. Cálculo Financeiro
- **Valor total de VR**: dias úteis × valor diário por sindicato
- **Custo empresa**: 80% do valor total
- **Desconto profissional**: 20% do valor total

### 7. Validações de Integridade
- Verificação de arquivos carregados
- Consistência de datas (admissões futuras, desligamentos sem comunicado)
- Validação de cálculos financeiros (proporção 80%/20%)
- Identificação de valores atípicos
- Mapeamento de sindicatos e valores diários

## Regras de Negócio

### Chave de Identificação
- Campo: `matricula`
- Formato: 5-12 dígitos numéricos
- Regex: `^\d{5,12}$`

### Exclusões por Status
- Funcionários marcados como "demitido" são excluídos
- Funcionários marcados como "não recebe VR" são excluídos
- Validação aplicada no processamento de admissões

### Regra do Dia 15
- **Comunicado até dia 15**: VR = 0 (exclusão total)
- **Comunicado após dia 15**: VR proporcional ao período

### Cálculo Proporcional
- **Admissões**: A partir da data de admissão
- **Desligamentos**: Até a data de desligamento
- **Férias/Afastamentos**: Desconto dos dias ausentes

## LLM Integrado

O sistema utiliza **Groq API** com o modelo **llama3-70b-8192** para:
- Orquestração inteligente do pipeline
- Explicação das decisões tomadas
- Relatórios detalhados de processamento
- Padrão ReAct (Reasoning and Acting) para tomada de decisões

### Configuração do LLM
```bash
# No arquivo .env
GROQ_API_KEY=sua_chave_api_aqui
```

## Saídas Geradas

### Arquivo Principal
- `VR_Mensal_YYYYMM.xlsx` - Planilha formatada para o fornecedor

### Abas de Log
- `LOG_AVISOS` - Avisos e informações do processamento
- `LOG_EXCLUSOES` - Detalhes de funcionários excluídos
- `LOG_PENDENCIAS` - Itens que requerem atenção

### Colunas de Saída
- Matricula
- Data Admissão
- Sindicato do Colaborador
- Competencia
- Dias
- VALOR DIÁRIO VR
- TOTAL
- Custo empresa
- Desconto profissional
- OBS GERAL

## Validações Automáticas

O sistema executa as seguintes validações:

1. **Integridade dos Arquivos**: Verifica se todos os arquivos esperados foram carregados
2. **Funcionários Elegíveis**: Confirma identificação de funcionários válidos
3. **Consistência de Datas**: Detecta admissões futuras e desligamentos inconsistentes
4. **Cálculos Financeiros**: Valida proporção empresa/funcionário (80%/20%)
5. **Mapeamento de Sindicatos**: Identifica funcionários sem valor diário mapeado
6. **Valores Atípicos**: Detecta VR Total acima de limites esperados

## Troubleshooting

### Problemas Comuns

1. **Arquivo não encontrado**: Verificar nomes exatos dos arquivos em `data/input/`
2. **Colunas não mapeadas**: Ajustar mapeamentos em `tools_beneficios.py`
3. **Datas inválidas**: Verificar formatos de data nos arquivos de entrada
4. **Valores zerados**: Verificar arquivo "Base sindicato x valor.xlsx"

### Logs de Debug
Consultar as abas `LOG_*` no arquivo de saída para informações detalhadas sobre:
- Avisos de processamento
- Exclusões aplicadas
- Pendências identificadas

## Desenvolvimento

### Estrutura do Código

- `load_sources()`: Carregamento dos arquivos Excel
- `validate_and_clean()`: Normalização e validação
- `exclude_non_eligible()`: Aplicação de exclusões
- `derive_workdays()`: Cálculo de dias úteis
- `compute_financials()`: Cálculos financeiros
- `validate_integrity()`: Validações de integridade
- `export_layout()`: Geração do arquivo final

### Personalização

Para adaptar o sistema:

1. **Novos sindicatos**: Atualizar mapeamento em `compute_financials()`
2. **Novos feriados**: Adicionar em `_get_feriados_regionais()`
3. **Novas validações**: Expandir `validate_integrity()`
4. **Novos campos**: Ajustar mapeamentos em `export_layout()`

## Suporte

Para problemas ou dúvidas:

1. Verificar logs de execução
2. Consultar abas LOG no arquivo de saída
3. Validar formato e conteúdo dos arquivos de entrada
4. Confirmar configuração do ambiente Python
