from database import Database
from datetime import datetime

db = Database()

class Corretora:
    def __init__(self, id=None, nome=None):
        self.id = id
        self.nome = nome
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE corretoras SET nome = ? WHERE id = ?",
                (self.nome, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO corretoras (nome) VALUES (?)",
                (self.nome,)
            )
    
    @staticmethod
    def buscar_todas():
        results = db.fetch_all("SELECT * FROM corretoras ORDER BY nome")
        return [Corretora(id=row[0], nome=row[1]) for row in results]
    
    @staticmethod
    def buscar_por_id(id):
        result = db.fetch_one("SELECT * FROM corretoras WHERE id = ?", (id,))
        if result:
            return Corretora(id=result[0], nome=result[1])
        return None

class Deposito:
    def __init__(self, id=None, data=None, corretora_id=None, valor=None):
        self.id = id
        self.data = data
        self.corretora_id = corretora_id
        self.valor = valor
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE depositos SET data = ?, corretora_id = ?, valor = ? WHERE id = ?",
                (self.data, self.corretora_id, self.valor, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO depositos (data, corretora_id, valor) VALUES (?, ?, ?)",
                (self.data, self.corretora_id, self.valor)
            )
    
    @staticmethod
    def buscar_todos():
        results = db.fetch_all('''
            SELECT d.*, c.nome as corretora_nome 
            FROM depositos d 
            JOIN corretoras c ON d.corretora_id = c.id 
            ORDER BY d.data DESC
        ''')
        depositos = []
        for row in results:
            dep = Deposito(id=row[0], data=row[1], corretora_id=row[2], valor=row[3])
            dep.corretora_nome = row[4]
            depositos.append(dep)
        return depositos

class NotaCorretagem:
    def __init__(self, id=None, data=None, corretora_id=None, numero_nota=None, valor_total=None):
        self.id = id
        self.data = data
        self.corretora_id = corretora_id
        self.numero_nota = numero_nota
        self.valor_total = valor_total
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE notas_corretagem SET data = ?, corretora_id = ?, numero_nota = ?, valor_total = ? WHERE id = ?",
                (self.data, self.corretora_id, self.numero_nota, self.valor_total, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO notas_corretagem (data, corretora_id, numero_nota, valor_total) VALUES (?, ?, ?, ?)",
                (self.data, self.corretora_id, self.numero_nota, self.valor_total)
            )
            # Retornar o ID da nota inserida
            result = db.fetch_one("SELECT last_insert_rowid()")
            return result[0] if result else None
        return self.id
    
    @staticmethod
    def buscar_todas():
        results = db.fetch_all('''
            SELECT n.*, c.nome as corretora_nome 
            FROM notas_corretagem n 
            JOIN corretoras c ON n.corretora_id = c.id 
            ORDER BY n.data DESC
        ''')
        notas = []
        for row in results:
            nota = NotaCorretagem(id=row[0], data=row[1], corretora_id=row[2], 
                                numero_nota=row[3], valor_total=row[4])
            nota.corretora_nome = row[5]
            notas.append(nota)
        return notas
    
    @staticmethod
    def buscar_por_id(id):
        result = db.fetch_one('''
            SELECT n.*, c.nome as corretora_nome 
            FROM notas_corretagem n 
            JOIN corretoras c ON n.corretora_id = c.id 
            WHERE n.id = ?
        ''', (id,))
        if result:
            nota = NotaCorretagem(id=result[0], data=result[1], corretora_id=result[2], 
                                numero_nota=result[3], valor_total=result[4])
            nota.corretora_nome = result[5]
            return nota
        return None

class Operacao:
    def __init__(self, id=None, nota_id=None, ticker=None, tipo=None, quantidade=None, preco=None, total=None):
        self.id = id
        self.nota_id = nota_id
        self.ticker = ticker
        self.tipo = tipo
        self.quantidade = quantidade
        self.preco = preco
        self.total = total
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE operacoes SET nota_id = ?, ticker = ?, tipo = ?, quantidade = ?, preco = ?, total = ? WHERE id = ?",
                (self.nota_id, self.ticker, self.tipo, self.quantidade, self.preco, self.total, self.id)
            )
        else:
            db.execute_query(
                "INSERT INTO operacoes (nota_id, ticker, tipo, quantidade, preco, total) VALUES (?, ?, ?, ?, ?, ?)",
                (self.nota_id, self.ticker, self.tipo, self.quantidade, self.preco, self.total)
            )
    
    @staticmethod
    def buscar_por_nota(nota_id):
        results = db.fetch_all('''
            SELECT * FROM operacoes WHERE nota_id = ? ORDER BY ticker
        ''', (nota_id,))
        operacoes = []
        for row in results:
            op = Operacao(id=row[0], nota_id=row[1], ticker=row[2], tipo=row[3], 
                         quantidade=row[4], preco=row[5], total=row[6])
            operacoes.append(op)
        return operacoes

class Relatorio:
    @staticmethod
    def calcular_saldo_corretoras():
        """Calcula o saldo atual de cada corretora"""
        query = '''
            SELECT 
                c.id,
                c.nome,
                COALESCE(SUM(d.valor), 0) as total_depositado,
                COALESCE(SUM(n.valor_total), 0) as total_notas,
                COALESCE(SUM(d.valor), 0) - COALESCE(SUM(n.valor_total), 0) as saldo
            FROM corretoras c
            LEFT JOIN depositos d ON c.id = d.corretora_id
            LEFT JOIN notas_corretagem n ON c.id = n.corretora_id
            GROUP BY c.id, c.nome
            ORDER BY c.nome
        '''
        return db.fetch_all(query)
    
    @staticmethod
    def calcular_carteira():
        """Calcula a carteira atual de ativos"""
        query = '''
            SELECT 
                ticker,
                SUM(CASE WHEN tipo = 'C' THEN quantidade ELSE -quantidade END) as quantidade,
                SUM(CASE WHEN tipo = 'C' THEN total ELSE -total END) as valor_investido,
                CASE 
                    WHEN SUM(CASE WHEN tipo = 'C' THEN quantidade ELSE -quantidade END) > 0 
                    THEN SUM(CASE WHEN tipo = 'C' THEN total ELSE -total END) / 
                         SUM(CASE WHEN tipo = 'C' THEN quantidade ELSE -quantidade END)
                    ELSE 0 
                END as preco_medio
            FROM operacoes
            GROUP BY ticker
            HAVING quantidade > 0
            ORDER BY ticker
        '''
        return db.fetch_all(query)
