import os
from typing import Any, Dict
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

import tools_beneficios as tb

@tool("load_sources")
def t_load_sources(input_dir: str) -> Dict[str, Any]:
    """Carrega os arquivos de entrada do diretório especificado."""
    return tb.load_sources(input_dir)

@tool("set_config")
def t_set_config(competencia: str) -> Dict[str, Any]:
    """Configura parâmetros do processamento como competência e critérios."""
    # Extrai a competência se vier como string de dicionário
    if "competencia" in competencia and "2025-" in competencia:
        import re
        match = re.search(r"(\d{4}-\d{2})", competencia)
        if match:
            competencia = match.group(1)
    return tb.set_config(competencia)

@tool("validate_and_clean")
def t_validate_and_clean() -> Dict[str, Any]:
    """Valida e limpa os dados carregados."""
    return tb.validate_and_clean()

@tool("exclude_non_eligible")
def t_exclude_non_eligible() -> Dict[str, Any]:
    """Exclui funcionários não elegíveis (aprendizes, estagiários, exterior)."""
    return tb.exclude_non_eligible()

@tool("derive_workdays")
def t_derive_workdays() -> Dict[str, Any]:
    """Calcula os dias úteis para cada funcionário."""
    return tb.derive_workdays()

@tool("compute_financials")
def t_compute_financials() -> Dict[str, Any]:
    """Calcula os valores financeiros do VR."""
    return tb.compute_financials()

@tool("validate_integrity")
def t_validate_integrity() -> Dict[str, Any]:
    """Executa validações automáticas de integridade dos dados processados."""
    return tb.validate_integrity()

@tool("export_layout")
def t_export_layout(output_dir: str, template_path: str = None) -> Dict[str, Any]:
    """Exporta os dados no layout do template especificado."""
    # Se template_path não foi fornecido, tenta extrair do output_dir
    if template_path is None and "," in output_dir:
        parts = output_dir.strip("()").split(", ")
        if len(parts) >= 2:
            output_dir = parts[0].strip("'\"")
            template_path = parts[1].strip("'\"")
    
    if template_path is None:
        template_path = "/home/alexandre/Documents/I2A2/gaia/vr_benefits/src/../data/template/VR MENSAL 05.2025.xlsx"
    
    return tb.export_layout(output_dir, template_path)

TOOLS = [t_load_sources, t_set_config, t_validate_and_clean, t_exclude_non_eligible, t_derive_workdays, t_compute_financials, t_validate_integrity, t_export_layout]

REACT_TEMPLATE = """Você orquestra tools determinísticas para calcular VR e exportar no layout do template.
Siga o fluxo EXATO:
1) load_sources(input_dir)
2) set_config(competencia) - use apenas a competência no formato YYYY-MM
3) validate_and_clean()
4) exclude_non_eligible()
5) derive_workdays()
6) compute_financials()
7) validate_integrity() - executa validações automáticas
8) export_layout(output_dir, template_path)
Ao final, explique decisões, avisos, exclusões, validações e o caminho do arquivo gerado.

IMPORTANTE: Para set_config use apenas a competência, exemplo: "2025-05"

TOOLS:
------
Você tem acesso às seguintes tools:

{tools}

Use o seguinte formato:

Question: a pergunta de entrada que você deve responder
Thought: você deve sempre pensar sobre o que fazer
Action: a ação a ser tomada, deve ser uma de [{tool_names}]
Action Input: a entrada para a ação (para set_config use apenas a string da competência)
Observation: o resultado da ação
... (este padrão Thought/Action/Action Input/Observation pode ser repetido N vezes)
Thought: Eu agora sei a resposta final
Final Answer: a resposta final para a pergunta original

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

USER_TEMPLATE = """Competência: {competencia}
Entrada: {input_dir}
Template: {template_path}
Saída: {output_dir}
Execute o fluxo completo."""

def build_agent(model_name: str = "llama3-70b-8192", use_groq: bool = True):
    """
    Constrói o agente LangChain.
    Args:
        model_name: Nome do modelo a ser usado
        use_groq: Se True, usa Groq API; se False, usa OpenAI
    """
    if use_groq:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada no arquivo .env")
        llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name=model_name)
    else:
        llm = ChatOpenAI(model=model_name, temperature=0)
    
    prompt = PromptTemplate.from_template(REACT_TEMPLATE)
    agent = create_react_agent(llm, TOOLS, prompt)
    user_prompt = PromptTemplate.from_template(USER_TEMPLATE)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True), user_prompt
