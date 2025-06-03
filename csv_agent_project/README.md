# LangChain CSV Question Answering Agent (com Google Gemini)

Este projeto implementa uma aplicação baseada em LLM usando LangChain para responder a perguntas em linguagem natural sobre arquivos CSV extraídos de dados de notas fiscais públicas brasileiras, utilizando os modelos Deepseek.

## Objetivo

Construir um agente capaz de extrair, ler e consultar dados de dois arquivos CSV relacionados a notas fiscais eletrônicas:
- `202401_NFs_Cabecalho.csv` (Cabeçalhos das Notas Fiscais)
- `202401_NFs_Itens.csv` (Itens das Notas Fiscais)

## Estrutura do Projeto
```
csv_agent_project/
│
├── app.py # Arquivo principal da aplicação
├── requirements.txt # Dependências Python
├── .env # Arquivo para variáveis de ambiente (ex: GOOGLE_API_KEY, DEEPSEEK_API_KEY, etc)
│
├── data/
│   ├── 202401_NFs.zip # Arquivo de entrada (zip) - DEVE SER COLOCADO AQUI
│   └── extracted/ # Pasta para onde os CSVs são extraídos
│       ├── 202401_NFs_Cabecalho.csv # (será extraído aqui)
│       └── 202401_NFs_Itens.csv     # (será extraído aqui)
│
├── agents/
│   └── invoice_agent.py # Lógica do agente CSV baseado em LangChain
│
├── utils/
│   └── file_handler.py # Funções para descompactar e carregar arquivos
│
└── README.md # Documentação do projeto (este arquivo)
```

## Requisitos do Projeto

1.  **Interface**: Aceitar perguntas do usuário via CLI.
2.  **Manuseio de Dados**:
    *   Descompactar `202401_NFs.zip` (se ainda não descompactado e os CSVs estiverem faltando no diretório `data/extracted/`).
    *   Carregar `202401_NFs_Cabecalho.csv` e `202401_NFs_Itens.csv` do diretório `data/extracted/`.
    *   Realizar consultas inteligentes de dados (ex: agregações, filtros, ordenações).
    *   Retornar respostas claras e precisas.
3.  **Formato CSV**:
    *   Separador: vírgula `,`
    *   Ponto decimal: `.` (ponto)
    *   Formato de datas: `YYYY-MM-DD HH:MM:SS` (o agente CSV do LangChain tentará analisar as datas automaticamente; `pandas_kwargs` são usados para auxiliar nisso).
4.  **Linguagem**: Python
5.  **LLM**: Google Gemini

## Configuração e Instalação

1.  **Clone o repositório (se aplicável) ou baixe os arquivos para a estrutura de pastas definida.**

2.  **Crie e Ative um Ambiente Virtual Python (Recomendado):**
    Navegue até o diretório raiz do projeto (`csv_agent_project/`) e execute:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # No Windows use `venv\Scripts\activate`
    ```

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua Chave de API do Google:**
    *   Crie um arquivo chamado `.env` na raiz do projeto (`csv_agent_project/.env`).
    *   Adicione sua chave de API do Google a este arquivo da seguinte forma:
        ```env
        DEEPSEEK_API_KEY="SUA_CHAVE_API_DO_DEEPSEEK_AQUI"
        ```
    *   **Substitua `SUA_CHAVE_API_DO_DEEPSEEK_AQUI` pela sua chave de API real.** A aplicação carregará esta chave automaticamente.

5.  **Prepare os Dados:**
    *   Certifique-se de que o diretório `csv_agent_project/data/` exista.
    *   Coloque o arquivo `202401_NFs.zip` dentro do diretório `csv_agent_project/data/`.
    *   Se o arquivo zip não estiver disponível, o script tentará gerar arquivos CSV fictícios (`202401_NFs_Cabecalho.csv` e `202401_NFs_Itens.csv`) no diretório `csv_agent_project/data/extracted/` para fins de desenvolvimento. Você deve substituí-los pelos dados reais para obter resultados significativos.

## Executando a Aplicação

Com o ambiente virtual ativado e as configurações feitas, execute o script principal a partir do diretório `csv_agent_project/`:

```bash
python app.py
```

O script irá:
1.  Carregar variáveis de ambiente do arquivo `.env`.
2.  Verificar o diretório `data/extracted/` e criá-lo se não existir.
3.  Descompactar `202401_NFs.zip` (do diretório `data/`) para o diretório `data/extracted/` se os arquivos CSV ainda não estiverem presentes.
4.  Carregar os arquivos CSV.
5.  Inicializar o agente CSV LangChain com o modelo Gemini.
6.  Solicitar que você faça perguntas na linha de comando.

Exemplos de perguntas para tentar:
*   "Qual fornecedor recebeu o maior valor total?"
*   "Qual item foi entregue na maior quantidade?"
*   "Qual é o valor total das notas fiscais do 'Fornecedor A'?"
*   "Liste todos os itens da nota fiscal 'NFE123'."

Digite `exit` para sair da aplicação.

## Estrutura do Código

*   `app.py`: Contém a lógica principal da aplicação, incluindo o carregamento de dados (via `file_handler`), criação do agente (via `invoice_agent`) e o loop de interação CLI.
*   `utils/file_handler.py`: Funções para garantir a existência dos diretórios de dados, descompactar o arquivo zip e fornecer os caminhos para os arquivos CSV.
*   `agents/invoice_agent.py`: Função para criar o agente LangChain CSV configurado para usar o Gemini e os `pandas_kwargs` especificados.
*   `requirements.txt`: Lista as dependências Python do projeto.
*   `.env`: Arquivo para armazenar sua `GOOGLE_API_KEY` (não deve ser versionado se o projeto for para um repositório público).
*   `data/`: Este diretório deve conter seu arquivo `202401_NFs.zip`. O script extrairá os CSVs para `data/extracted/`.
*   `README.md`: Este arquivo.

## Notas sobre o Agente CSV e Manuseio de Dados

*   O `create_csv_agent` de `langchain_experimental.agents.agent_toolkits` é usado. Este agente pode trabalhar com múltiplos arquivos CSV.
*   O agente usa um Modelo de Linguagem Grande (LLM) - Gemini - para entender as perguntas e gerar código Python (frequentemente Pandas) para consultar os dados CSV.
*   `allow_dangerous_code=True`: É usado porque o agente gera e executa código Python. Esteja ciente das implicações de segurança se executar este agente com entrada não confiável ou em um ambiente não seguro.
*   **Análise de Datas**: O argumento `pandas_kwargs` em `create_csv_agent` é usado para ajudar o Pandas a analisar corretamente as datas e lidar com o dialeto CSV (separador, decimal).
*   **Escolha do LLM**: O código está configurado para `ChatGoogleGenerativeAI` com `model="gemini-pro"`.

## Melhorias Potenciais (Opcional)

*   **Interface Web**: Usar Streamlit ou Gradio para criar uma interface web amigável.
*   **Integração com Banco de Dados**: Para conjuntos de dados maiores ou necessidades de consulta mais complexas, carregar os dados CSV em um banco de dados (ex: DuckDB, SQLite) e usar o agente SQL do LangChain.
*   **Configuração Avançada do Agente**: Explorar diferentes tipos de agentes e ferramentas dentro do LangChain para interações mais sofisticadas.
*   **Tratamento de Erros e Robustez**: Adicionar tratamento de erros e validação de entrada mais abrangentes.
