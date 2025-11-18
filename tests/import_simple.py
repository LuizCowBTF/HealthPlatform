# import_simple.py
import pandas as pd
import sqlite3
from pathlib import Path

def import_simple():
    print("🔄 IMPORTACAÇÃO SIMPLES...")
    
    excel_path = Path("Documentacao/EXCEL/CRM_Almeida_Consultoria.xlsx")
    
    if not excel_path.exists():
        print("❌ Arquivo não encontrado!")
        return
    
    # Ler todas as planilhas
    all_sheets = pd.read_excel(excel_path, sheet_name=None)
    
    conn = sqlite3.connect("health_platform.db")
    
    for sheet_name, df in all_sheets.items():
        print(f"📋 {sheet_name}: {len(df)} registros")
        
        # Usar nome simples para tabela
        table_name = sheet_name.lower().replace(" ", "_")[:10]
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"   ✅ Salvo como: {table_name}")
    
    conn.close()
    print("🎉 DADOS IMPORTADOS!")

if __name__ == "__main__":
    import_simple()