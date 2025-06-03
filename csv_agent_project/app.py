# app.py
import os
from dotenv import load_dotenv # Adicionado para carregar .env
from utils import file_handler
from agents import invoice_agent

# --- Main Application Logic ---
def main():
    """Main function to run the CSV question answering agent."""
    load_dotenv() # Carrega variáveis do arquivo .env
    print("Starting LangChain CSV Question Answering Agent...")

    # 1. Ensure data is ready (unzip if necessary)
    file_handler.unzip_data()

    # 2. Get CSV file paths
    csv_header_file, csv_items_file = file_handler.get_csv_file_paths()

    if not os.path.exists(csv_header_file) or not os.path.exists(csv_items_file):
        print("Error: One or both CSV files are missing after attempting to prepare data.")
        print(f"Checked for: {csv_header_file}")
        print(f"Checked for: {csv_items_file}")
        print("Please ensure the zip file is correct or place the CSV files manually in the 'data/extracted' directory.")
        return

    # 3. Create the LangChain agent
    # The agent needs a list of file paths
    agent_executor = invoice_agent.create_invoice_agent([csv_header_file, csv_items_file])

    if not agent_executor:
        print("Failed to create the invoice agent. Exiting.")
        return

    print("\n--- Ask questions about your CSV data ---")
    print("Type 'exit' to quit.")

    while True:
        user_question = input("\nQuestion: ")
        if user_question.lower() == 'exit':
            print("Exiting...")
            break
        if user_question:
            try:
                # Use the agent to get an answer            
                answer = agent_executor.invoke({"input": user_question})
                print(f"Answer: {answer}")
            except Exception as e:
                print(f"Error processing question: {e}")
                print("This might be due to an issue with the LLM, the generated code, or your API key.")

if __name__ == "__main__":
    load_dotenv() # Carrega variáveis do arquivo .env também aqui para a verificação inicial
    # Check for DEEPSEEK_API_KEY at the very start if critical
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("\nCRITICAL WARNING: DEEPSEEK_API_KEY environment variable not set.")
        print("The application will likely fail to initialize the LangChain agent.")
        print("Please set the DEEPSEEK_API_KEY environment variable in your .env file or system-wide and try again.")
        print("Example .env file content: DEEPSEEK_API_KEY='your_key_here'")
        # Optionally, you could exit here: return
    main()
