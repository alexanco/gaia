# VR Benefits Automation (LangChain + Pandas)

Automatiza o cálculo mensal de Vale Refeição (VR) usando **LangChain** (agente para orquestração/explicação)
e **pandas** (cálculo determinístico). Gera a planilha final **no mesmo layout** do template `VR MENSAL 05.2025.xlsx`.

## Estrutura
```
vr_benefits_full/
├─ src/
│  ├─ agent_vr.py           # Agente LangChain + Tools
│  ├─ tools_beneficios.py   # Funções determinísticas (pandas)
│  ├─ util.py               # Utilidades (datas, interseções, normalização)
│  └─ run.py                # CLI: roda o pipeline (com/sem agente)
├─ data/
│  ├─ input/                # Coloque aqui os .xlsx (.csv opcional)
│  └─ template/             # Template do layout final (VR MENSAL 05.2025.xlsx)
├─ output/                  # Saídas (planilha final + logs)
├─ requirements.txt
└─ .env.example
```

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Execução (modo determinístico – recomendado para produção)
1. Coloque os arquivos em `data/input/` (nomes esperados):
   - `ATIVOS.xlsx`, `ADMISSÃO ABRIL.xlsx`, `DESLIGADOS.xlsx`, `FÉRIAS.xlsx`,
     `AFASTAMENTOS.xlsx`, `EXTERIOR.xlsx`, `APRENDIZ.xlsx`, `ESTÁGIO.xlsx`,
     `Base sindicato x valor.xlsx`, `Base dias uteis.xlsx`
2. Rode:
```bash
python -m src.run --mes 2025-05 --no-llm
```
Saídas em `output/VR_Mensal_202505.xlsx` e abas de LOG no mesmo arquivo.

## Execução (com agente LangChain – opcional)
```bash
export OPENAI_API_KEY=SEU_TOKEN
python -m src.run --mes 2025-05
```

## Regras implementadas
- **Chave:** `matricula`.
- **Base única:** união de ATIVOS + ADMISSÕES; enriquecida por sindicato/UF/município quando disponível.
- **Exclusões:** aprendizes, estagiários, exterior (por matrícula).
- **Dias úteis por colaborador:** por sindicato (a partir de `Base dias uteis.xlsx`), proporcional ao período:
  - Admissão no mês → conta a partir da data.
  - Desligamento no mês → conta até a data.
  - **Regra do dia 15:** se comunicado **OK até o dia 15**, VR = 0; senão, proporcional.
  - **Férias/Afastamentos:** subtrai a interseção de dias com a janela útil do colaborador.
- **Cálculo financeiro:** `VR Total = dias_uteis_calc * valor_diario` (por sindicato),
  `Empresa = 80%`, `Colaborador = 20%`.
- **Layout final:** colunas/ordem do template (primeira aba).

## Ajustes rápidos
- Se os nomes de colunas diferirem, ajuste os `rename` em `tools_beneficios.py` (funções `validate_and_clean`/`derive_workdays`) e o `mapping` em `export_layout`.
- `--mes` aceita `YYYY-MM` para definir a competência.
- Alterar regex da matrícula ou `cutoff_day` na função `set_config`.

## Suporte
Se algo quebrar por causa dos nomes de colunas, rode com `--no-llm` e verifique as abas `LOG_*` do arquivo de saída. Essas abas trazem avisos, exclusões e pendências para correção.
