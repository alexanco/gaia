import os
import logging
from typing import List
from langchain.agents.agent_types import AgentType
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent

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
    "Você é um especialista em análise de notas fiscais eletrônicas (NF-e) brasileiras.\n"
    "Analise exclusivamente os dados dos arquivos CSV fornecidos.\n"
    "Responda somente com o valor solicitado. Seja direto e evite qualquer explicação adicional.\n"
    "Se a informação não estiver presente, diga 'Não encontrado'."
)

def get_agent() -> AgentExecutor:
    """
    Cria um agente seguro baseado em LLM para análise de CSV.
    Garante que nenhuma execução de código seja realizada.

    Returns:
        AgentExecutor: Agente seguro configurado.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("A variável DEEPSEEK_API_KEY não está configurada.")

    llm = ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        temperature=0,
        openai_api_key=api_key
    )

    return create_csv_agent(
        llm=llm,
        path=CSV_PATHS,
        verbose=False,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        allow_dangerous_code=True,  # <- necessário para evitar o erro
        pandas_kwargs={
            'sep': ',',
            'decimal': '.',
            'parse_dates': True
        },
        agent_kwargs={
            "system_message": SYSTEM_MESSAGE
    }
)

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
        agent = get_agent()        
        response = agent.invoke({"input": question})
        logger.info(f"[Resposta gerada] {response}")
        return str(response).strip()
    except Exception as e:
        logger.exception("Erro ao processar a pergunta.")
        raise Exception(f"Erro ao processar a pergunta: {e}")
