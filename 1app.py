# primeira versão
from flask import Flask, render_template, request, redirect, url_for, jsonify
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
