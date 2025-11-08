'''from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Corretora, Ativo, Operacao, Relatorio
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    corretoras = Corretora.buscar_todas()
    ativos = Ativo.buscar_todos()
    operacoes = Operacao.buscar_todas()[:10]  # Últimas 10 operações
    
    # Calcular totais
    total_investido = sum(op.total for op in operacoes if op.tipo == 'compra')
    total_retirado = sum(op.total for op in operacoes if op.tipo in ['venda', 'dividendo'])
    
    return render_template('index.html', 
                         corretoras=corretoras,
                         ativos=ativos,
                         operacoes=operacoes,
                         total_investido=total_investido,
                         total_retirado=total_retirado)

@app.route('/lancamentos', methods=['GET', 'POST'])
def lancamentos():
    if request.method == 'POST':
        # Processar novo lançamento
        data = request.form['data']
        corretora_id = request.form['corretora_id']
        ativo_ticker = request.form['ativo_ticker']
        tipo = request.form['tipo']
        quantidade = int(request.form['quantidade'])
        preco_unitario = float(request.form['preco_unitario'])
        taxas = float(request.form.get('taxas', 0))
        
        # Buscar ou criar ativo
        ativo = Ativo.buscar_por_ticker(ativo_ticker)
        if not ativo:
            ativo_nome = request.form.get('ativo_nome', '')
            ativo_categoria = request.form.get('ativo_categoria', 'Ações')
            ativo = Ativo(ticker=ativo_ticker, nome=ativo_nome, categoria=ativo_categoria)
            ativo.salvar()
            ativo = Ativo.buscar_por_ticker(ativo_ticker)
        
        # Criar operação
        operacao = Operacao(
            data=data,
            corretora_id=corretora_id,
            ativo_id=ativo.id,
            tipo=tipo,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            taxas=taxas
        )
        operacao.salvar()
        
        return redirect(url_for('lancamentos'))
    
    corretoras = Corretora.buscar_todas()
    ativos = Ativo.buscar_todos()
    operacoes = Operacao.buscar_todas()
    
    return render_template('lancamentos.html',
                         corretoras=corretoras,
                         ativos=ativos,
                         operacoes=operacoes)

@app.route('/visualizacao')
def visualizacao():
    corretora_id = request.args.get('corretora_id')
    agrupar_por = request.args.get('agrupar_por', 'ativo')
    
    corretoras = Corretora.buscar_todas()
    corretora_selecionada = None
    
    if corretora_id:
        corretora_selecionada = Corretora.buscar_por_id(corretora_id)
    
    if agrupar_por == 'ativo':
        dados = Relatorio.calcular_preco_medio_por_ativo(corretora_id)
    else:
        dados = Relatorio.calcular_preco_medio_por_categoria(corretora_id)
    
    return render_template('visualizacao.html',
                         corretoras=corretoras,
                         corretora_selecionada=corretora_selecionada,
                         dados=dados,
                         agrupar_por=agrupar_por)

@app.route('/api/corretoras', methods=['POST'])
def criar_corretora():
    nome = request.json['nome']
    saldo = request.json.get('saldo', 0)
    
    corretora = Corretora(nome=nome, saldo=saldo)
    corretora.salvar()
    
    return jsonify({'success': True})

@app.route('/debug')
def debug():
    from models import Corretora, Database
    
    # Verificar corretoras no banco
    corretoras = Corretora.buscar_todas()
    result = f"Corretoras encontradas: {len(corretoras)}<br>"
    
    for c in corretoras:
        result += f"ID: {c.id}, Nome: {c.nome}<br>"
    
    # Verificar estrutura do banco
    db = Database()
    tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    result += "<br>Tabelas no banco:<br>"
    for table in tables:
        result += f"{table[0]}<br>"
    
    return result

if __name__ == '__main__':
    # Criar alguns dados de exemplo
    from database import Database
    db = Database()
    
    # Corretoras exemplo
    try:
        db.execute_query("INSERT OR IGNORE INTO corretoras (nome, saldo) VALUES (?, ?)", 
                        ('XP Investimentos', 10000))
        db.execute_query("INSERT OR IGNORE INTO corretoras (nome, saldo) VALUES (?, ?)", 
                        ('Clear Corretora', 5000))
    except:
        pass
    
    app.run(debug=True, port=5000)
'''
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Corretora, Deposito, NotaCorretagem, Operacao, Relatorio
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    # Saldo das corretoras
    saldos = Relatorio.calcular_saldo_corretoras()
    
    # Carteira atual
    carteira = Relatorio.calcular_carteira()
    
    # Últimos depósitos
    ultimos_depositos = Deposito.buscar_todos()[:5]
    
    # Últimas notas
    ultimas_notas = NotaCorretagem.buscar_todas()[:5]
    
    # Totais gerais
    total_depositado = sum(row[2] for row in saldos)
    total_investido = sum(row[3] for row in saldos)
    saldo_total = sum(row[4] for row in saldos)
    
    return render_template('index.html',
                         saldos=saldos,
                         carteira=carteira,
                         ultimos_depositos=ultimos_depositos,
                         ultimas_notas=ultimas_notas,
                         total_depositado=total_depositado,
                         total_investido=total_investido,
                         saldo_total=saldo_total)

@app.route('/depositos', methods=['GET', 'POST'])
def depositos():
    if request.method == 'POST':
        data = request.form['data']
        corretora_id = request.form['corretora_id']
        valor = float(request.form['valor'])
        
        deposito = Deposito(data=data, corretora_id=corretora_id, valor=valor)
        deposito.salvar()
        
        return redirect(url_for('depositos'))
    
    corretoras = Corretora.buscar_todas()
    depositos = Deposito.buscar_todos()
    
    return render_template('depositos.html',
                         corretoras=corretoras,
                         depositos=depositos)

@app.route('/notas', methods=['GET', 'POST'])
def notas_corretagem():
    if request.method == 'POST':
        # Criar nota de corretagem
        data = request.form['data']
        corretora_id = request.form['corretora_id']
        numero_nota = request.form['numero_nota']
        valor_total = float(request.form['valor_total'])
        
        nota = NotaCorretagem(data=data, corretora_id=corretora_id, 
                            numero_nota=numero_nota, valor_total=valor_total)
        nota_id = nota.salvar()
        
        # Processar operações
        operacoes_data = request.form.getlist('operacoes[]')
        for op_data in operacoes_data:
            if op_data.strip():
                ticker, tipo, quantidade, preco, total = op_data.split('|')
                operacao = Operacao(
                    nota_id=nota_id,
                    ticker=ticker.upper(),
                    tipo=tipo,
                    quantidade=int(quantidade),
                    preco=float(preco),
                    total=float(total)
                )
                operacao.salvar()
        
        return redirect(url_for('notas_corretagem'))
    
    corretoras = Corretora.buscar_todas()
    notas = NotaCorretagem.buscar_todas()
    
    return render_template('notas_corretagem.html',
                         corretoras=corretoras,
                         notas=notas)

@app.route('/nota/<int:nota_id>')
def detalhes_nota(nota_id):
    nota = NotaCorretagem.buscar_por_id(nota_id)
    operacoes = Operacao.buscar_por_nota(nota_id)
    
    return render_template('detalhes_nota.html',
                         nota=nota,
                         operacoes=operacoes)

@app.route('/corretoras', methods=['GET', 'POST'])
def gerenciar_corretoras():
    if request.method == 'POST':
        nome = request.form['nome']
        corretora = Corretora(nome=nome)
        corretora.salvar()
        return redirect(url_for('gerenciar_corretoras'))
    
    corretoras = Corretora.buscar_todas()
    return render_template('corretoras.html', corretoras=corretoras)

@app.route('/debug')
def debug():
    # Verificar corretoras no banco
    corretoras = Corretora.buscar_todas()
    result = f"Corretoras encontradas: {len(corretoras)}<br>"
    
    for c in corretoras:
        result += f"ID: {c.id}, Nome: {c.nome}<br>"
    
    # Verificar estrutura do banco
    from database import Database
    db = Database()
    tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    result += "<br>Tabelas no banco:<br>"
    for table in tables:
        result += f"{table[0]}<br>"
    
    return result

if __name__ == '__main__':
    # Criar corretoras padrão se não existirem
    from models import Corretora
    corretoras_existentes = Corretora.buscar_todas()
    
    if not corretoras_existentes:
        print("Criando corretoras padrão...")
        corretoras_padrao = [
            'XP Investimentos',
            'Clear Corretora', 
            'Rico Investimentos',
            'BTG Pactual',
            'Avenue',
            'Inter'
        ]
        
        for nome in corretoras_padrao:
            corretora = Corretora(nome=nome)
            corretora.salvar()
        
        print("Corretoras criadas com sucesso!")
    
    app.run(debug=True, port=5000)





