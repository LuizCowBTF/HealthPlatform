# check_tables.py - VERSÃO CORRIGIDA
import sqlite3
from pathlib import Path

def check_tables():
    # CAMINHO CORRETO - banco na MESMA pasta
    db_path = Path("health_platform.db")
    
    print(f"🔍 VERIFICANDO BANCO: {db_path.absolute()}")
    print(f"📁 Arquivo existe: {db_path.exists()}")
    
    if not db_path.exists():
        print("❌ Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("🔍 VERIFICANDO ESTRUTURA DAS TABELAS...")
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"📊 TABELAS ENCONTRADAS ({len(tables)}):")
    
    for table in tables:
        table_name = table[0]
        print(f"\n🗃️  TABELA: {table_name}")
        
        # Contar registros
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"   📈 Registros: {count}")
        
        # Mostrar colunas
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        print(f"   📝 Colunas ({len(columns)}):")
        for col in columns[:5]:  # Mostrar apenas 5 primeiras colunas
            print(f"      - {col[1]} ({col[2]})")
        if len(columns) > 5:
            print(f"      ... e mais {len(columns) - 5} colunas")
    
    conn.close()

if __name__ == "__main__":
    check_tables()