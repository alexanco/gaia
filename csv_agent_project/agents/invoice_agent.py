import os
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI 

def create_invoice_agent(csv_file_paths):
    """
    Creates and returns a LangChain CSV agent using DeepSeek for querying invoice data.

    Args:
        csv_file_paths (list): A list of paths to the CSV files.
                                 Example: ['path/to/headers.csv', 'path/to/items.csv']

    Returns:
        A LangChain agent executor.
    """
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\nWARNING: DEEPSEEK_API_KEY environment variable not set.")
        print("Please set it to your DeepSeek API key.")
        return None

    # Configuração do modelo DeepSeek (mesmo estilo da OpenAI)
    llm = ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        temperature=0,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY")
    )

    pandas_kwargs = {
        'sep': ',',
        'decimal': '.',
        'parse_dates': True
    }

    agent_kwargs = {
    "system_message": (
        "Você é um especialista em análise de notas fiscais eletrônicas (NF-e) brasileiras.\n"
        "Responda exclusivamente com base nos dados dos arquivos CSV fornecidos.\n"
        "Sua resposta deve conter **somente o dado solicitado**, de forma direta.\n"
        "Não explique, não adicione comentários, não justifique e não repita a pergunta.\n"
        "Se não encontrar uma resposta exata, diga apenas 'Não encontrado'."
    )
}

    try:
        agent_executor = create_csv_agent(
            llm,
            csv_file_paths,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            pandas_kwargs=pandas_kwargs,
            allow_dangerous_code=True,
            agent_kwargs=agent_kwargs

        )
        print("Invoice agent created successfully with DeepSeek.")
        return agent_executor
    except Exception as e:
        print(f"Error creating LangChain agent: {e}")
        return None
