from database import Database
from datetime import datetime

db = Database()

class Corretora:
    def __init__(self, id=None, nome=None, saldo=0):
        self.id = id
        self.nome = nome
        self.saldo = saldo
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE corretoras SET nome = ?, saldo = ? WHERE id = ?",
                (self.nome, self.saldo, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO corretoras (nome, saldo) VALUES (?, ?)",
                (self.nome, self.saldo)
            )
    
    @staticmethod
    def buscar_todas():
        results = db.fetch_all("SELECT * FROM corretoras ORDER BY nome")
        return [Corretora(id=row[0], nome=row[1], saldo=row[2]) for row in results]
    
    @staticmethod
    def buscar_por_id(id):
        result = db.fetch_one("SELECT * FROM corretoras WHERE id = ?", (id,))
        if result:
            return Corretora(id=result[0], nome=result[1], saldo=result[2])
        return None

class Ativo:
    def __init__(self, id=None, ticker=None, nome=None, categoria=None):
        self.id = id
        self.ticker = ticker
        self.nome = nome
        self.categoria = categoria
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE ativos SET ticker = ?, nome = ?, categoria = ? WHERE id = ?",
                (self.ticker, self.nome, self.categoria, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO ativos (ticker, nome, categoria) VALUES (?, ?, ?)",
                (self.ticker, self.nome, self.categoria)
            )
    
    @staticmethod
    def buscar_todos():
        results = db.fetch_all("SELECT * FROM ativos ORDER BY ticker")
        return [Ativo(id=row[0], ticker=row[1], nome=row[2], categoria=row[3]) for row in results]
    
    @staticmethod
    def buscar_por_ticker(ticker):
        result = db.fetch_one("SELECT * FROM ativos WHERE ticker = ?", (ticker,))
        if result:
            return Ativo(id=result[0], ticker=result[1], nome=result[2], categoria=result[3])
        return None

class Operacao:
    def __init__(self, id=None, data=None, corretora_id=None, ativo_id=None, 
                 tipo=None, quantidade=None, preco_unitario=None, taxas=0, total=None):
        self.id = id
        self.data = data
        self.corretora_id = corretora_id
        self.ativo_id = ativo_id
        self.tipo = tipo
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.taxas = taxas
        self.total = total
    
    def salvar(self):
        # Calcular total
        if self.tipo == 'compra':
            self.total = (self.quantidade * self.preco_unitario) + self.taxas
        else:  # venda ou dividendo
            self.total = (self.quantidade * self.preco_unitario) - self.taxas
        
        if self.id:
            db.execute_query('''
                UPDATE operacoes SET data = ?, corretora_id = ?, ativo_id = ?, tipo = ?,
                quantidade = ?, preco_unitario = ?, taxas = ?, total = ? WHERE id = ?
            ''', (self.data, self.corretora_id, self.ativo_id, self.tipo,
                  self.quantidade, self.preco_unitario, self.taxas, self.total, self.id))
        else:
            db.execute_query('''
                INSERT INTO operacoes (data, corretora_id, ativo_id, tipo, quantidade, 
                preco_unitario, taxas, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.data, self.corretora_id, self.ativo_id, self.tipo,
                  self.quantidade, self.preco_unitario, self.taxas, self.total))
    
    @staticmethod
    def buscar_todas():
        results = db.fetch_all('''
            SELECT o.*, c.nome as corretora_nome, a.ticker as ativo_ticker, a.nome as ativo_nome
            FROM operacoes o
            JOIN corretoras c ON o.corretora_id = c.id
            JOIN ativos a ON o.ativo_id = a.id
            ORDER BY o.data DESC
        ''')
        operacoes = []
        for row in results:
            op = Operacao(
                id=row[0], data=row[1], corretora_id=row[2], ativo_id=row[3],
                tipo=row[4], quantidade=row[5], preco_unitario=row[6],
                taxas=row[7], total=row[8]
            )
            op.corretora_nome = row[9]
            op.ativo_ticker = row[10]
            op.ativo_nome = row[11]
            operacoes.append(op)
        return operacoes

class Relatorio:
    @staticmethod
    def calcular_preco_medio_por_ativo(corretora_id=None):
        query = '''
            SELECT 
                a.ticker,
                a.nome,
                a.categoria,
                SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END) as quantidade_total,
                SUM(CASE WHEN o.tipo = 'compra' THEN o.total ELSE -o.total END) as valor_total,
                CASE 
                    WHEN SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END) > 0 
                    THEN SUM(CASE WHEN o.tipo = 'compra' THEN o.total ELSE -o.total END) / 
                         SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END)
                    ELSE 0 
                END as preco_medio
            FROM operacoes o
            JOIN ativos a ON o.ativo_id = a.id
        '''
        
        if corretora_id:
            query += " WHERE o.corretora_id = ?"
            params = (corretora_id,)
        else:
            params = ()
            
        query += '''
            GROUP BY a.ticker, a.nome, a.categoria
            HAVING quantidade_total > 0
            ORDER BY a.categoria, a.ticker
        '''
        
        return db.fetch_all(query, params)
    
    @staticmethod
    def calcular_preco_medio_por_categoria(corretora_id=None):
        query = '''
            SELECT 
                a.categoria,
                SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END) as quantidade_total,
                SUM(CASE WHEN o.tipo = 'compra' THEN o.total ELSE -o.total END) as valor_total,
                CASE 
                    WHEN SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END) > 0 
                    THEN SUM(CASE WHEN o.tipo = 'compra' THEN o.total ELSE -o.total END) / 
                         SUM(CASE WHEN o.tipo = 'compra' THEN o.quantidade ELSE -o.quantidade END)
                    ELSE 0 
                END as preco_medio
            FROM operacoes o
            JOIN ativos a ON o.ativo_id = a.id
        '''
        
        if corretora_id:
            query += " WHERE o.corretora_id = ?"
            params = (corretora_id,)
        else:
            params = ()
            
        query += '''
            GROUP BY a.categoria
            HAVING quantidade_total > 0
            ORDER BY a.categoria
        '''
        
        return db.fetch_all(query, params)
