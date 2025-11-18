# import_excel_final.py - VERSÃO COM CAMINHO CORRETO
import pandas as pd
import sqlite3
from pathlib import Path

def import_excel_data():
    print("🎯 IMPORTANDO DADOS DO CRM ALCON...")
    
    # CAMINHOS ABSOLUTOS CORRETOS
    project_root = Path(__file__).parent
    excel_path = project_root / "Documentacao" / "EXCEL" / "CRM_Almeida_Consultoria.xlsx"
    db_path = project_root / "health_platform.db"
    
    print(f"📁 Excel: {excel_path}")
    print(f"🗄️  Banco: {db_path}")
    print(f"✅ Excel existe: {excel_path.exists()}")
    
    if not excel_path.exists():
        print("❌ Arquivo Excel não encontrado!")
        return
    
    try:
        # Ler o Excel
        xl = pd.ExcelFile(excel_path)
        print(f"📑 Planilhas: {xl.sheet_names}")
        
        # Conectar ao SQLite na RAIZ
        conn = sqlite3.connect(str(db_path))
        
        total_imported = 0
        
        for sheet_name in xl.sheet_names:
            print(f"\n📋 {sheet_name}")
            
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet_name)
                print(f"   📊 {len(df)} linhas × {len(df.columns)} colunas")
                
                # Nome da tabela
                table_name = clean_table_name(sheet_name)
                print(f"   🗃️  {table_name}")
                
                # Importar
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                print(f"   ✅ {len(df)} registros")
                total_imported += len(df)
                
            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue
        
        conn.close()
        
        print(f"\n🎉 IMPORTADO: {total_imported} registros totais")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

def clean_table_name(name):
    name = name.lower().replace(" ", "_").replace("-", "_")
    return ''.join(c for c in name if c.isalnum() or c == '_')

if __name__ == "__main__":
    import_excel_data()