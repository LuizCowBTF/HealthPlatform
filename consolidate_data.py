# consolidate_data.py - EXECUTAR DA PASTA RAIZ
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

def consolidate_data():
    print("🔄 CONSOLIDANDO DADOS DOS CORRETORES...")
    
    # Caminho CORRETO do banco (na raiz)
    db_path = Path("health_platform.db")
    conn = sqlite3.connect(str(db_path))
    
    # Lista de tabelas de corretores
    broker_tables = [
        'bruna_mamedes', 'maiara_andrade', 'fernando_diamantino', 
        'marcio_jorge', 'amanda_facundo', 'camila_adao', 'diogo_lima',
        'leandro_drumond', 'leandro_nascimento', 'roberto_ramos',
        'rodrigo_oliveira', 'darlin_amorim', 'lucas_almeida', 'anteriores'
    ]
    
    # 1. CONSOLIDAR LEADS
    print("\n📥 CONSOLIDANDO LEADS...")
    all_leads = []
    lead_id_counter = 1
    
    for broker_table in broker_tables:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {broker_table}")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"   📋 {broker_table}: {count} registros")
                
                df = pd.read_sql(f"SELECT * FROM {broker_table}", conn)
                
                for _, row in df.iterrows():
                    # Só processar se tiver nome
                    if pd.notna(row.get('NOME COMPLETO')) or pd.notna(row.get('NOME')):
                        lead = {
                            'id': lead_id_counter,
                            'full_name': str(row.get('NOME COMPLETO') or row.get('NOME') or '').strip(),
                            'phone': str(row.get('TELEFONE') or ''),
                            'email': str(row.get('E-MAIL') or ''),
                            'source': str(row.get('ORIGEM') or ''),
                            'status': str(row.get('STATUS') or 'Novo'),
                            'broker_id': get_broker_id(broker_table),
                            'created_at': parse_date(row.get('DATA INCLUSÃO') or row.get('DATA DE DIGITAÇÃO'))
                        }
                        
                        if lead['full_name']:  # Só adicionar se tiver nome
                            all_leads.append(lead)
                            lead_id_counter += 1
                        
        except Exception as e:
            print(f"   ❌ Erro em {broker_table}: {e}")
            continue
    
    # Salvar leads consolidados
    if all_leads:
        df_leads = pd.DataFrame(all_leads)
        df_leads.to_sql('leads', conn, if_exists='replace', index=False)
        print(f"   ✅ LEADS: {len(all_leads)} registros")
    
    # 2. CRIAR TABELA DE CORRETORES
    print("\n👑 CRIANDO CORRETORES...")
    
    brokers_data = [
        {'id': 1, 'name': 'Bruna Mamedes', 'email': 'bruna@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 2, 'name': 'Maiara Andrade', 'email': 'maiara@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 3, 'name': 'Fernando Diamantino', 'email': 'fernando@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 4, 'name': 'Marcio Jorge', 'email': 'marcio@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 5, 'name': 'Amanda Facundo', 'email': 'amanda@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 6, 'name': 'Camila Adão', 'email': 'camila@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 7, 'name': 'Diogo Lima', 'email': 'diogo@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 8, 'name': 'Leandro Drumond', 'email': 'leandro@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 9, 'name': 'Leandro Nascimento', 'email': 'leandro.n@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 10, 'name': 'Roberto Ramos', 'email': 'roberto@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 11, 'name': 'Rodrigo Oliveira', 'email': 'rodrigo@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 12, 'name': 'Darlin Amorim', 'email': 'darlin@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 13, 'name': 'Lucas Almeida', 'email': 'lucas@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True},
        {'id': 14, 'name': 'Corretores Anteriores', 'email': 'anteriores@alcon.com', 'phone': '(21) 99999-9999', 'monthly_goal': 10000.0, 'is_active': True}
    ]
    
    df_brokers = pd.DataFrame(brokers_data)
    df_brokers.to_sql('brokers', conn, if_exists='replace', index=False)
    print(f"   ✅ CORRETORES: {len(brokers_data)} registros")
    
    # 3. IDENTIFICAR VENDAS
    print("\n💰 IDENTIFICANDO VENDAS...")
    all_sales = []
    sale_id_counter = 1
    
    for broker_table in broker_tables:
        try:
            # Buscar registros que parecem vendas (com valor de orçamento)
            df_sales = pd.read_sql(f"""
                SELECT * FROM {broker_table} 
                WHERE "VALOR ORÇAMENTO" IS NOT NULL 
                AND "VALOR ORÇAMENTO" != ''
                AND "VALOR ORÇAMENTO" != '0'
            """, conn)
            
            if len(df_sales) > 0:
                print(f"   💰 {broker_table}: {len(df_sales)} possíveis vendas")
                
                for _, row in df_sales.iterrows():
                    valor = parse_currency(row.get('VALOR ORÇAMENTO'))
                    if valor and valor > 0:
                        sale = {
                            'id': sale_id_counter,
                            'lead_id': None,  # Poderia ligar com leads depois
                            'broker_id': get_broker_id(broker_table),
                            'plan_type': str(row.get('PLANO DE INTERESSE') or ''),
                            'operator': extract_operator(str(row.get('PLANO DE INTERESSE') or '')),
                            'value': valor,
                            'commission_value': valor * 0.05,  # 5% comissão
                            'status': 'completed',
                            'sale_date': parse_date(row.get('DATA DE DIGITAÇÃO') or row.get('DATA INCLUSÃO'))
                        }
                        all_sales.append(sale)
                        sale_id_counter += 1
                        
        except Exception as e:
            print(f"   ❌ Erro em {broker_table}: {e}")
            continue
    
    # Salvar vendas
    if all_sales:
        df_sales = pd.DataFrame(all_sales)
        df_sales.to_sql('sales', conn, if_exists='replace', index=False)
        print(f"   ✅ VENDAS: {len(all_sales)} registros")
    
    conn.close()
    
    print(f"\n🎉 CONSOLIDAÇÃO CONCLUÍDA!")
    print(f"📊 RESUMO FINAL:")
    print(f"   👥 Leads: {len(all_leads)}")
    print(f"   👑 Corretores: {len(brokers_data)}")
    print(f"   💰 Vendas: {len(all_sales)}")

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
    if not plan_text:
        return 'Não especificado'
    plan_text = str(plan_text).upper()
    if 'AMIL' in plan_text: return 'Amil'
    if 'BRADESCO' in plan_text: return 'Bradesco'
    if 'SULAMERICA' in plan_text: return 'SulAmérica'
    if 'UNIMED' in plan_text: return 'Unimed'
    if 'NOTREDAME' in plan_text: return 'NotreDame'
    return 'Outra'

def parse_currency(value):
    if pd.isna(value) or value in ['', '0', 0]:
        return 0
    try:
        if isinstance(value, str):
            value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return float(value)
    except:
        return 0

def parse_date(date_value):
    if pd.isna(date_value):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        if isinstance(date_value, str):
            return date_value
        return date_value.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    consolidate_data()