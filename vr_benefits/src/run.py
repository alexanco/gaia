import os
import argparse
from dotenv import load_dotenv
import tools_beneficios as tb

def run_deterministic(input_dir: str, competencia: str, output_dir: str, template_path: str):
    print(">> Carregando fontes...")
    tb.load_sources(input_dir)
    print(">> Configurando...")
    tb.set_config(competencia)
    print(">> Validando/Limpando...")
    tb.validate_and_clean()
    print(">> Exclusões...")
    tb.exclude_non_eligible()
    print(">> Dias úteis...")
    tb.derive_workdays()
    print(">> Cálculo financeiro...")
    tb.compute_financials()
    print(">> Validações de integridade...")
    validation_result = tb.validate_integrity()
    if not validation_result["ok"]:
        print(f"⚠️ ATENÇÃO: {validation_result['errors']} erros encontrados!")
        for erro in validation_result["detalhes"]["errors"]:
            print(f"   {erro}")
    if validation_result["warnings"] > 0:
        print(f"⚠️ {validation_result['warnings']} avisos encontrados")
    print(f"✓ {validation_result['validacoes_ok']} validações OK")
    print(">> Exportando...")
    res = tb.export_layout(output_dir, template_path)
    print(res)

def run_with_agent(input_dir: str, competencia: str, output_dir: str, template_path: str, model_name: str, use_groq: bool = True):
    from agent_vr import build_agent
    agent, prompt = build_agent(model_name=model_name, use_groq=use_groq)
    user = prompt.format(competencia=competencia, input_dir=input_dir, template_path=template_path, output_dir=output_dir)
    result = agent.invoke({"input": user})
    print(result.get("output", ""))

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--mes", required=True, help="YYYY-MM (ex.: 2025-05)")
    parser.add_argument("--input", default=os.path.join(os.path.dirname(__file__), "..", "data", "input"))
    parser.add_argument("--output", default=os.path.join(os.path.dirname(__file__), "..", "output"))
    parser.add_argument("--template", default=os.path.join(os.path.dirname(__file__), "..", "data", "template", "VR MENSAL 05.2025.xlsx"))
    parser.add_argument("--no-llm", action="store_true", help="Roda sem agente (determinístico)")
    parser.add_argument("--model", default="llama3-70b-8192", help="Nome do modelo LLM")
    parser.add_argument("--use-openai", action="store_true", help="Usar OpenAI em vez de Groq")
    args = parser.parse_args()

    if args.no_llm or not os.getenv("GROQ_API_KEY"):
        run_deterministic(args.input, args.mes, args.output, args.template)
    else:
        use_groq = not args.use_openai
        run_with_agent(args.input, args.mes, args.output, args.template, args.model, use_groq)
