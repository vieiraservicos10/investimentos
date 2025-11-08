import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='investimentos.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de corretoras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS corretoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                saldo REAL DEFAULT 0
            )
        ''')
        
        # Tabela de ativos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                nome TEXT,
                categoria TEXT
            )
        ''')
        
        # Tabela de operações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                corretora_id INTEGER NOT NULL,
                ativo_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('compra', 'venda', 'dividendo')),
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                taxas REAL DEFAULT 0,
                total REAL NOT NULL,
                FOREIGN KEY (corretora_id) REFERENCES corretoras (id),
                FOREIGN KEY (ativo_id) REFERENCES ativos (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
    
    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result
