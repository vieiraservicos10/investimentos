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
    def __init__(self, id=None, data=None, corretora_id=None, numero_nota=None, valor_total=None, taxas=0):
        self.id = id
        self.data = data
        self.corretora_id = corretora_id
        self.numero_nota = numero_nota
        self.valor_total = valor_total
        self.taxas = taxas
    
    def salvar(self):
        if self.id:
            db.execute_query(
                "UPDATE notas_corretagem SET data = ?, corretora_id = ?, numero_nota = ?, valor_total = ?, taxas = ? WHERE id = ?",
                (self.data, self.corretora_id, self.numero_nota, self.valor_total, self.taxas, self.id)
            )
            return self.id
        else:
            # CORREÇÃO: Usar conexão direta para obter o ID correto
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notas_corretagem (data, corretora_id, numero_nota, valor_total, taxas) VALUES (?, ?, ?, ?, ?)",
                (self.data, self.corretora_id, self.numero_nota, self.valor_total, self.taxas)
            )
            nota_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return nota_id
    
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
                                numero_nota=row[3], valor_total=row[4], taxas=row[5])
            nota.corretora_nome = row[6]
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
                                numero_nota=result[3], valor_total=result[4], taxas=result[5])
            nota.corretora_nome = result[6]
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
    def calcular_resumo_por_corretora():
        """Calcula resumo detalhado por corretora - COM TAXAS"""
        query = '''
            SELECT 
                c.id,
                c.nome,
                COALESCE((
                    SELECT SUM(d.valor) 
                    FROM depositos d 
                    WHERE d.corretora_id = c.id
                ), 0) as total_depositado,
                COALESCE((
                    SELECT SUM(
                        CASE 
                            WHEN o.tipo = 'C' THEN o.total
                            ELSE 0 
                        END
                    )
                    FROM operacoes o
                    JOIN notas_corretagem n ON o.nota_id = n.id
                    WHERE n.corretora_id = c.id
                ), 0) as total_compras,
                COALESCE((
                    SELECT SUM(
                        CASE 
                            WHEN o.tipo = 'V' THEN o.total
                            ELSE 0 
                        END
                    )
                    FROM operacoes o
                    JOIN notas_corretagem n ON o.nota_id = n.id
                    WHERE n.corretora_id = c.id
                ), 0) as total_vendas,
                COALESCE((
                    SELECT SUM(n.taxas)
                    FROM notas_corretagem n
                    WHERE n.corretora_id = c.id
                ), 0) as total_taxas,
                COALESCE((
                    SELECT SUM(d.valor) 
                    FROM depositos d 
                    WHERE d.corretora_id = c.id
                ), 0) + COALESCE((
                    SELECT SUM(
                        CASE 
                            WHEN o.tipo = 'C' THEN -o.total
                            WHEN o.tipo = 'V' THEN o.total
                            ELSE 0 
                        END
                    ) - SUM(n.taxas)
                    FROM operacoes o
                    JOIN notas_corretagem n ON o.nota_id = n.id
                    WHERE n.corretora_id = c.id
                ), 0) as saldo_disponivel,
                COALESCE((
                    SELECT SUM(
                        CASE 
                            WHEN o.tipo = 'C' THEN o.total
                            WHEN o.tipo = 'V' THEN -o.total
                            ELSE 0 
                        END
                    )
                    FROM operacoes o
                    JOIN notas_corretagem n ON o.nota_id = n.id
                    WHERE n.corretora_id = c.id
                ), 0) as valor_investido_liquido
            FROM corretoras c
            ORDER BY c.nome
        '''
        return db.fetch_all(query)
    
    @staticmethod
    def calcular_carteira_por_corretora(corretora_id=None):
        """Calcula a carteira atual por corretora"""
        if corretora_id:
            query = '''
                SELECT 
                    o.ticker,
                    SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END) as quantidade,
                    SUM(CASE WHEN o.tipo = 'C' THEN o.total ELSE -o.total END) as valor_investido,
                    CASE 
                        WHEN SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END) > 0 
                        THEN SUM(CASE WHEN o.tipo = 'C' THEN o.total ELSE -o.total END) / 
                             SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END)
                        ELSE 0 
                    END as preco_medio
                FROM operacoes o
                JOIN notas_corretagem n ON o.nota_id = n.id
                WHERE n.corretora_id = ?
                GROUP BY o.ticker
                HAVING quantidade > 0
                ORDER BY o.ticker
            '''
            return db.fetch_all(query, (corretora_id,))
        else:
            query = '''
                SELECT 
                    o.ticker,
                    SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END) as quantidade,
                    SUM(CASE WHEN o.tipo = 'C' THEN o.total ELSE -o.total END) as valor_investido,
                    CASE 
                        WHEN SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END) > 0 
                        THEN SUM(CASE WHEN o.tipo = 'C' THEN o.total ELSE -o.total END) / 
                             SUM(CASE WHEN o.tipo = 'C' THEN o.quantidade ELSE -o.quantidade END)
                        ELSE 0 
                    END as preco_medio
                FROM operacoes o
                GROUP BY o.ticker
                HAVING quantidade > 0
                ORDER BY o.ticker
            '''
            return db.fetch_all(query)
