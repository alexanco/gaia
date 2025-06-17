import os
import logging
from typing import List

import pandas as pd
from langchain.agents import AgentExecutor, initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits.pandas.base import create_pandas_dataframe_agent
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminhos dos arquivos CSV
CSV_PATHS: List[str] = [
    "/app/data/202401_NFs_Cabecalho.csv",
    "/app/data/202401_NFs_Itens.csv"
]

# Mensagem de sistema para a LLM
SYSTEM_MESSAGE = (
    "Você é um agente especialista em Notas Fiscais Eletrônicas (NF-e) com amplo conhecimento técnico, fiscal e normativo. Seu objetivo é analisar e validar dados fiscais contidos em dois datasets fornecidos: o dataset Cabecalhos, que contém informações principais de cada nota fiscal, incluindo a Chave de Acesso (chave primária e identificador único da nota), Número da Nota, Data de Emissão, Valor Total da Nota e demais campos fiscais; e o dataset Itens, que contém os itens individuais de cada nota fiscal, com informações de Chave de Acesso (chave primária, correspondendo à chave no dataset Cabecalhos), Código do Item, Descrição do Produto, Quantidade, Valor Unitário, Valor Total do Item e demais campos de detalhe.\n"
    "Sua principal tarefa é realizar a validação de consistência entre os dois datasets: para cada Chave de Acesso, você deve verificar se a soma do campo Valor Total do Item de todos os itens associados corresponde exatamente ao Valor Total da Nota no dataset Cabecalhos. Sempre que encontrar divergências, apresente um relatório informando a Chave de Acesso, o Valor Total informado na Nota, a soma calculada dos itens e a diferença apurada.\n"
    "Além disso, você deve ser capaz de responder perguntas analíticas e descritivas sobre os dados dos datasets, como: quantidade total de notas fiscais, soma total de valores de notas, número de itens em determinada nota, identificação das maiores notas fiscais emitidas e listagem dos produtos mais comuns. Sempre que possível, apresente as respostas em forma de tabela, lista ou resumo numérico, conforme for mais adequado.\n"
    "Você também deve identificar anomalias fiscais, como notas fiscais com valor total zerado, notas fiscais sem itens associados, e itens com valores unitários nulos ou negativos. Suas respostas devem ser técnicas, claras, objetivas e fundamentadas. Sempre explique o raciocínio seguido ao apresentar suas conclusões. Utilize a Chave de Acesso como chave primária para todas as operações de cruzamento de dados. Em caso de ausência de dados ou limitações nos arquivos fornecidos, informe a limitação de forma transparente e prossiga com a análise possível."
)



def get_agent() -> AgentExecutor:
    """
    Cria um agente seguro baseado em LLM com acesso a múltiplos DataFrames CSV.
    """

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("A variável DEEPSEEK_API_KEY não está configurada.")

    # Instancia o LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        temperature=0,
        openai_api_key=api_key
    )

    # Carrega os arquivos CSV
    dataframes = []
    for path in CSV_PATHS:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        df = pd.read_csv(path, sep=",", decimal=".", parse_dates=True)
        dataframes.append(df)

    # Cria ferramentas de consulta para cada CSV
    tools = []
    for i, df in enumerate(dataframes):
        tool = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            verbose=False,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            allow_dangerous_code=True
        )
        tools.append(
            Tool.from_function(
                func=tool.run,
                name=f"CSV_{i+1}",
                description=f"Consulta ao CSV {i+1}"
            )
        )

    # Cria o prompt com system_message
    system_prompt = SystemMessagePromptTemplate.from_template(SYSTEM_MESSAGE)
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt])

    # Cria e retorna o agente
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )


agent = get_agent()

def process_question(question: str) -> str:
    """
    Usa o agente para responder uma pergunta sobre os dados CSV.

    Args:
        question (str): Pergunta sobre os dados.

    Returns:
        str: Resposta gerada pela LLM com base nos arquivos.

    Raises:
        Exception: Caso ocorra falha no processamento.
    """
    logger.info(f"[Pergunta recebida] {question}")
    try:
        response = agent.invoke({"input": question})
        logger.info(f"[Resposta gerada] {response}")
        return str(response).strip()
    except Exception as e:
        logger.exception("Erro ao processar a pergunta.")
        raise Exception(f"Erro ao processar a pergunta: {e}")
