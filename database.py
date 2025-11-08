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
                nome TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Tabela de depósitos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS depositos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                corretora_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                FOREIGN KEY (corretora_id) REFERENCES corretoras (id)
            )
        ''')
        
        # Tabela de notas de corretagem
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notas_corretagem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE NOT NULL,
                corretora_id INTEGER NOT NULL,
                numero_nota TEXT,
                valor_total REAL NOT NULL,
                FOREIGN KEY (corretora_id) REFERENCES corretoras (id)
            )
        ''')
        
        # Tabela de operações dentro das notas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nota_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('C', 'V')),
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (nota_id) REFERENCES notas_corretagem (id)
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
