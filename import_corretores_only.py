# import_corretores_only.py - APENAS CORRETORES REAIS
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime

def import_corretores_only():
    print("🎯 IMPORTANDO APENAS DADOS DOS CORRETORES...")
    
    # Caminhos
    excel_path = Path("Documentacao/EXCEL/CRM_Almeida_Consultoria.xlsx")
    db_path = Path("health_platform.db")
    
    print(f"📁 Excel: {excel_path}")
    print(f"✅ Excel existe: {excel_path.exists()}")
    
    if not excel_path.exists():
        print("❌ Arquivo Excel não encontrado!")
        return
    
    try:
        # Ler o Excel
        xl = pd.ExcelFile(excel_path)
        print(f"📑 Todas as planilhas: {xl.sheet_names}")
        
        # APENAS planilhas dos corretores reais (evitar "Corretor 1", "Corretor 2", etc.)
        corretores_sheets = [
            'Bruna Mamedes', 'Maiara Andrade', 'Fernando Diamantino',
            'Marcio Jorge', 'Amanda Facundo', 'Camila Adão', 'Diogo Lima',
            'Leandro Drumond', 'Leandro Nascimento', 'Roberto Ramos',
            'Rodrigo Oliveira', 'Darlin Amorim', 'Lucas Almeida', 'Anteriores'
        ]
        
        print(f"🎯 Planilhas dos corretores: {corretores_sheets}")
        
        # Conectar ao banco
        conn = sqlite3.connect(str(db_path))
        
        # 1. IMPORTAR PLANILHAS DOS CORRETORES
        print("\n📥 IMPORTANDO PLANILHAS DOS CORRETORES...")
        imported_tables = {}
        
        for sheet_name in corretores_sheets:
            if sheet_name in xl.sheet_names:
                try:
                    df = pd.read_excel(excel_path, sheet_name=sheet_name)
                    table_name = clean_table_name(sheet_name)
                    
                    # Limpar nomes de colunas problemáticos
                    df.columns = [clean_column_name(col) for col in df.columns]
                    
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    imported_tables[table_name] = len(df)
                    print(f"   ✅ {sheet_name} → {table_name}: {len(df)} registros")
                    
                except Exception as e:
                    print(f"   ❌ Erro em {sheet_name}: {e}")
                    continue
        
        # 2. CONSOLIDAR LEADS
        print("\n📥 CONSOLIDANDO LEADS...")
        all_leads = []
        lead_id = 1
        
        for broker_table in imported_tables.keys():
            try:
                df = pd.read_sql(f"SELECT * FROM {broker_table}", conn)
                print(f"   📋 Processando {broker_table}: {len(df)} registros")
                
                for _, row in df.iterrows():
                    # Verificar se tem dados básicos
                    nome = str(row.get('NOME_COMPLETO') or row.get('NOME_COMPLETO') or '').strip()
                    telefone = str(row.get('TELEFONE') or '')
                    
                    if nome and nome != 'nan' and nome != 'None' and len(nome) > 2:
                        lead = {
                            'id': lead_id,
                            'full_name': nome[:200],  # Limitar tamanho
                            'phone': telefone[:20],   # Limitar tamanho
                            'email': str(row.get('E_MAIL') or '')[:100],
                            'source': str(row.get('ORIGEM') or '')[:50],
                            'status': str(row.get('STATUS') or 'Novo')[:50],
                            'broker_id': get_broker_id(broker_table),
                            'created_at': parse_date(row.get('DATA_INCLUSAO') or row.get('DATA_DE_DIGITACAO')),
                            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        all_leads.append(lead)
                        lead_id += 1
                        
            except Exception as e:
                print(f"   ⚠️  Erro consolidando {broker_table}: {e}")
                continue
        
        # Salvar leads
        if all_leads:
            df_leads = pd.DataFrame(all_leads)
            df_leads.to_sql('leads', conn, if_exists='replace', index=False)
            print(f"   ✅ LEADS CONSOLIDADOS: {len(all_leads)} registros")
        
        # 3. CONSOLIDAR VENDAS
        print("\n💰 CONSOLIDANDO VENDAS...")
        all_sales = []
        sale_id = 1
        
        for broker_table in imported_tables.keys():
            try:
                # Buscar registros com valor de orçamento
                df_sales = pd.read_sql(f"""
                    SELECT * FROM {broker_table} 
                    WHERE "VALOR_ORCAMENTO" IS NOT NULL 
                    AND "VALOR_ORCAMENTO" != '' 
                    AND "VALOR_ORCAMENTO" != '0'
                """, conn)
                
                if len(df_sales) > 0:
                    print(f"   💰 {broker_table}: {len(df_sales)} possíveis vendas")
                    
                    for _, row in df_sales.iterrows():
                        valor = parse_currency(row.get('VALOR_ORCAMENTO'))
                        if valor and valor > 0:
                            sale = {
                                'id': sale_id,
                                'lead_id': None,
                                'broker_id': get_broker_id(broker_table),
                                'plan_type': str(row.get('PLANO_DE_INTERESSE') or '')[:50],
                                'operator': extract_operator(str(row.get('PLANO_DE_INTERESSE') or '')),
                                'value': valor,
                                'commission_value': valor * 0.05,
                                'status': 'completed',
                                'sale_date': parse_date(row.get('DATA_DE_DIGITACAO') or row.get('DATA_INCLUSAO'))
                            }
                            all_sales.append(sale)
                            sale_id += 1
                            
            except Exception as e:
                print(f"   ⚠️  Erro em vendas {broker_table}: {e}")
                continue
        
        # Salvar vendas
        if all_sales:
            df_sales = pd.DataFrame(all_sales)
            df_sales.to_sql('sales', conn, if_exists='replace', index=False)
            print(f"   ✅ VENDAS IDENTIFICADAS: {len(all_sales)} registros")
        
        conn.close()
        
        print(f"\n🎉 PROCESSO CONCLUÍDO!")
        print(f"📊 RESUMO FINAL:")
        print(f"   👥 Leads: {len(all_leads)}")
        print(f"   💰 Vendas: {len(all_sales)}")
        print(f"   📑 Tabelas de corretores: {len(imported_tables)}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def clean_table_name(name):
    name = name.lower().replace(" ", "_").replace("-", "_")
    return ''.join(c for c in name if c.isalnum() or c == '_')

def clean_column_name(col_name):
    """Limpar nomes de colunas para serem válidos no SQL"""
    if pd.isna(col_name):
        return 'unknown_column'
    col_name = str(col_name).strip()
    col_name = col_name.replace(' ', '_').replace('-', '_').replace('/', '_')
    col_name = col_name.replace('(', '').replace(')', '').replace('Ã', 'A').replace('Ç', 'C')
    col_name = ''.join(c for c in col_name if c.isalnum() or c == '_')
    return col_name.upper()  # SQLite é case-insensitive, mas melhor padronizar

def get_broker_id(broker_table):
    mapping = {
        'bruna_mamedes': 1, 'maiara_andrade': 2, 'fernando_diamantino': 3,
        'marcio_jorge': 4, 'amanda_facundo': 5, 'camila_adao': 6,
        'diogo_lima': 7, 'leandro_drumond': 8, 'leandro_nascimento': 9,
        'roberto_ramos': 10, 'rodrigo_oliveira': 11, 'darlin_amorim': 12,
        'lucas_almeida': 13, 'anteriores': 14
    }
    return mapping.get(broker_table, 14)

def extract_operator(plan_text):
    if not plan_text or plan_text == 'nan':
        return 'Não especificado'
    plan_text = str(plan_text).upper()
    if 'AMIL' in plan_text: return 'Amil'
    if 'BRADESCO' in plan_text: return 'Bradesco'
    if 'SULAMERICA' in plan_text or 'SULAMÉRICA' in plan_text: return 'SulAmérica'
    if 'UNIMED' in plan_text: return 'Unimed'
    if 'NOTREDAME' in plan_text: return 'NotreDame'
    return 'Outra'

def parse_currency(value):
    if pd.isna(value) or value in ['', '0', 0, 'nan']:
        return 0
    try:
        if isinstance(value, str):
            value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(value)
    except:
        return 0

def parse_date(date_value):
    if pd.isna(date_value) or date_value in ['', 'nan']:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        if isinstance(date_value, str):
            return date_value
        return date_value.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    import_corretores_only()