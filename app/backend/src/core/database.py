# app/backend/src/core/database.py - VERSÃO SIMPLIFICADA
import aiosqlite
import os
from pathlib import Path
import sys

# Caminhos
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "health_platform.db"

print(f"📁 Database path: {DATABASE_PATH}")

async def init_database():
    """Inicializa o banco de dados SQLite"""
    
    SQL_CREATE_TABLES = """
    -- TABELA DE USUÁRIOS
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('admin', 'gerente', 'corretor', 'cliente')),
        ativo BOOLEAN DEFAULT 1,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- TABELA DE LEADS
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT,
        telefone TEXT,
        status TEXT DEFAULT 'novo',
        origem TEXT,
        corretor_id INTEGER,
        valor_estimado DECIMAL(10,2),
        data_contato TIMESTAMP,
        data_fechamento TIMESTAMP,
        observacoes TEXT,
        data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- TABELA DE CLIENTES
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER UNIQUE,
        nome TEXT NOT NULL,
        cpf_cnpj TEXT UNIQUE,
        email TEXT,
        telefone TEXT,
        endereco TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'ativo'
    );
    
    -- TABELA DE VENDAS
    CREATE TABLE IF NOT EXISTS vendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        corretor_id INTEGER,
        produto TEXT NOT NULL,
        valor_total DECIMAL(10,2) NOT NULL,
        comissao_percentual DECIMAL(5,2) DEFAULT 0.0,
        status TEXT DEFAULT 'pendente',
        data_venda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_pagamento TIMESTAMP,
        observacoes TEXT
    );
    
    -- TABELA DE COMISSÕES
    CREATE TABLE IF NOT EXISTS comissoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venda_id INTEGER UNIQUE,
        corretor_id INTEGER,
        valor_comissao DECIMAL(10,2) NOT NULL,
        status TEXT DEFAULT 'pendente',
        data_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        data_pagamento TIMESTAMP
    );
    
    -- TABELA DE MENSAGENS WHATSAPP
    CREATE TABLE IF NOT EXISTS mensagens_whatsapp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telefone_origem TEXT NOT NULL,
        telefone_destino TEXT NOT NULL,
        mensagem TEXT NOT NULL,
        tipo TEXT,
        status TEXT DEFAULT 'enviada',
        data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        lead_id INTEGER
    );
    """
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.executescript(SQL_CREATE_TABLES)
            await db.commit()
            print("✅ Banco de dados inicializado!")
            return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

# Função auxiliar para obter conexão
async def get_db():
    """Obtém uma conexão com o banco de dados"""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row  # Para retornar dicionários
    return db