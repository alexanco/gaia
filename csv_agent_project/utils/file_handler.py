import os
import zipfile
import pandas as pd

# --- Configuration ---
# Adjusted to reflect the new structure
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data") # csv_agent_project/data
EXTRACTED_DIR = os.path.join(DATA_DIR, "extracted") # csv_agent_project/data/extracted
ZIP_FILE_PATH = os.path.join(DATA_DIR, "202401_NFs.zip") # csv_agent_project/data/202401_NFs.zip
CSV_HEADER_FILE = os.path.join(EXTRACTED_DIR, "202401_NFs_Cabecalho.csv")
CSV_ITEMS_FILE = os.path.join(EXTRACTED_DIR, "202401_NFs_Itens.csv")

def ensure_data_directories():
    """Ensures the data and extracted directories exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")
    if not os.path.exists(EXTRACTED_DIR):
        os.makedirs(EXTRACTED_DIR)
        print(f"Created directory: {EXTRACTED_DIR}")

def unzip_data():
    """Unzips the data file into the 'extracted' directory if it hasn't been unzipped already."""
    ensure_data_directories()
    if not os.path.exists(CSV_HEADER_FILE) or not os.path.exists(CSV_ITEMS_FILE):
        if os.path.exists(ZIP_FILE_PATH):
            print(f"Unzipping {ZIP_FILE_PATH} to {EXTRACTED_DIR}...")
            with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
                zip_ref.extractall(EXTRACTED_DIR)
            print("Unzipping complete.")
            # Verify extraction
            if not os.path.exists(CSV_HEADER_FILE) or not os.path.exists(CSV_ITEMS_FILE):
                print(f"Error: CSV files not found in {EXTRACTED_DIR} after attempting to unzip.")
                print("Please check the zip file contents and structure.")
                print("Creating dummy CSV files as placeholders...")
                create_dummy_csv_files()

        else:
            print(f"Error: {ZIP_FILE_PATH} not found. Please place the zip file in the '{DATA_DIR}' directory.")
            print("Creating dummy CSV files as placeholders...")
            create_dummy_csv_files()
    else:
        print("CSV files already exist in 'extracted' directory. Skipping unzip.")

def create_dummy_csv_files():
    """Creates dummy CSV files for development if the zip file is not present."""
    ensure_data_directories() # Ensure extracted dir exists for dummy files
    header_df = pd.DataFrame({
        'Chave NF': ['NFE123', 'NFE456'],
        'Data Emissao': ['2024-01-15 10:00:00', '2024-01-16 11:30:00'],
        'CNPJ Emitente': ['11111111000111', '22222222000122'],
        'Nome Emitente': ['Fornecedor A', 'Fornecedor B'],
        'Valor Total NF': [1500.75, 2300.50]
    })
    items_df = pd.DataFrame({
        'Chave NF': ['NFE123', 'NFE123', 'NFE456'],
        'Numero Item': [1, 2, 1],
        'Descricao Item': ['Produto X', 'Produto Y', 'Produto Z'],
        'Quantidade': [10.0, 5.0, 20.0],
        'Valor Unitario': [100.00, 100.15, 115.025],
        'Valor Total Item': [1000.00, 500.75, 2300.50]
    })
    header_df.to_csv(CSV_HEADER_FILE, index=False, sep=',', decimal='.')
    items_df.to_csv(CSV_ITEMS_FILE, index=False, sep=',', decimal='.')
    print(f"Created dummy {CSV_HEADER_FILE}")
    print(f"Created dummy {CSV_ITEMS_FILE}")
    print(f"Please replace these with the actual '{ZIP_FILE_PATH}' and run again.")

def get_csv_file_paths():
    """Returns the paths to the CSV files."""
    return CSV_HEADER_FILE, CSV_ITEMS_FILE
