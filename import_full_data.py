# import_full_data.py
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re

def import_full_data():
    print("🎯 IMPORTANDO DADOS COMPLETOS DO EXCEL...")
    
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
        print(f"📑 Planilhas: {xl.sheet_names}")
        
        # Conectar ao banco
        conn = sqlite3.connect(str(db_path))
        
        # 1. PRIMEIRO: Importar todas as planilhas como estão
        print("\n📥 IMPORTANDO PLANILHAS ORIGINAIS...")
        imported_tables = {}
        
        for sheet_name in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet_name)
            table_name = clean_table_name(sheet_name)
            
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            imported_tables[table_name] = len(df)
            print(f"   ✅ {sheet_name} → {table_name}: {len(df)} registros")
        
        # 2. AGORA: Consolidar dados nas tabelas principais
        print("\n🔄 CONSOLIDANDO DADOS NAS TABELAS PRINCIPAIS...")
        
        # Lista de tabelas de corretores (baseado nas planilhas)
        broker_tables = [
            'bruna_mamedes', 'maiara_andrade', 'fernando_diamantino', 
            'marcio_jorge', 'amanda_facundo', 'camila_adao', 'diogo_lima',
            'leandro_drumond', 'leandro_nascimento', 'roberto_ramos',
            'rodrigo_oliveira', 'darlin_amorim', 'lucas_almeida', 'anteriores'
        ]
        
        # Consolidar LEADS
        print("📥 Consolidando LEADS...")
        all_leads = []
        lead_id = 1
        
        for broker_table in broker_tables:
            if broker_table in imported_tables:
                try:
                    df = pd.read_sql(f"SELECT * FROM {broker_table}", conn)
                    
                    for _, row in df.iterrows():
                        # Verificar se tem dados básicos
                        nome = str(row.get('NOME COMPLETO') or row.get('NOME') or '').strip()
                        telefone = str(row.get('TELEFONE') or '')
                        
                        if nome and nome != 'nan' and nome != 'None':
                            lead = {
                                'id': lead_id,
                                'full_name': nome,
                                'phone': telefone,
                                'email': str(row.get('E-MAIL') or ''),
                                'source': str(row.get('ORIGEM') or ''),
                                'status': str(row.get('STATUS') or 'Novo'),
                                'broker_id': get_broker_id(broker_table),
                                'created_at': parse_date(row.get('DATA INCLUSÃO') or row.get('DATA DE DIGITAÇÃO')),
                                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            all_leads.append(lead)
                            lead_id += 1
                            
                except Exception as e:
                    print(f"   ⚠️  Erro em {broker_table}: {e}")
                    continue
        
        # Salvar leads
        if all_leads:
            df_leads = pd.DataFrame(all_leads)
            df_leads.to_sql('leads', conn, if_exists='replace', index=False)
            print(f"   ✅ LEADS: {len(all_leads)} registros")
        
        # Consolidar VENDAS
        print("💰 Consolidando VENDAS...")
        all_sales = []
        sale_id = 1
        
        for broker_table in broker_tables:
            if broker_table in imported_tables:
                try:
                    # Buscar registros com valor de orçamento
                    df_sales = pd.read_sql(f"""
                        SELECT * FROM {broker_table} 
                        WHERE "VALOR ORÇAMENTO" IS NOT NULL 
                        AND "VALOR ORÇAMENTO" != '' 
                        AND "VALOR ORÇAMENTO" != '0'
                    """, conn)
                    
                    for _, row in df_sales.iterrows():
                        valor = parse_currency(row.get('VALOR ORÇAMENTO'))
                        if valor and valor > 0:
                            sale = {
                                'id': sale_id,
                                'lead_id': None,  # Poderia ligar com lead depois
                                'broker_id': get_broker_id(broker_table),
                                'plan_type': str(row.get('PLANO DE INTERESSE') or ''),
                                'operator': extract_operator(str(row.get('PLANO DE INTERESSE') or '')),
                                'value': valor,
                                'commission_value': valor * 0.05,
                                'status': 'completed',
                                'sale_date': parse_date(row.get('DATA DE DIGITAÇÃO') or row.get('DATA INCLUSÃO'))
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
            print(f"   ✅ VENDAS: {len(all_sales)} registros")
        
        conn.close()
        
        print(f"\n🎉 IMPORTACAÇÃO E CONSOLIDAÇÃO CONCLUÍDAS!")
        print(f"📊 RESUMO FINAL:")
        print(f"   👥 Leads: {len(all_leads)}")
        print(f"   👑 Corretores: 14")
        print(f"   💰 Vendas: {len(all_sales)}")
        print(f"   📑 Tabelas originais: {len(imported_tables)}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

def clean_table_name(name):
    name = name.lower().replace(" ", "_").replace("-", "_")
    return ''.join(c for c in name if c.isalnum() or c == '_')

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
    import_full_data()