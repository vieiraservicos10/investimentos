from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import Corretora, Deposito, NotaCorretagem, Operacao, Relatorio
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Saldo das corretoras - CORRETO
        saldos = Relatorio.calcular_resumo_por_corretora()
        
        # Carteira atual geral
        carteira = Relatorio.calcular_carteira_por_corretora()
        
        # Últimos depósitos
        ultimos_depositos = Deposito.buscar_todos()[:5]
        
        # Últimas notas
        ultimas_notas = NotaCorretagem.buscar_todas()[:5]
        
        # Totais gerais - CORRIGIDOS
        total_depositado = sum(row[2] for row in saldos)
        total_compras = sum(row[3] for row in saldos)
        total_vendas = sum(row[4] for row in saldos)
        saldo_total = sum(row[5] for row in saldos)
        total_investido = sum(row[6] for row in saldos)
        
        return render_template('index.html',
                             saldos=saldos,
                             carteira=carteira,
                             ultimos_depositos=ultimos_depositos,
                             ultimas_notas=ultimas_notas,
                             total_depositado=total_depositado,
                             total_compras=total_compras,
                             total_vendas=total_vendas,
                             total_investido=total_investido,
                             saldo_total=saldo_total)
    except Exception as e:
        return f"Erro no dashboard: {e}"

@app.route('/depositos', methods=['GET', 'POST'])
def depositos():
    if request.method == 'POST':
        try:
            data = request.form['data']
            corretora_id = request.form['corretora_id']
            valor = float(request.form['valor'])
            
            deposito = Deposito(data=data, corretora_id=corretora_id, valor=valor)
            deposito.salvar()
            
            return redirect(url_for('depositos'))
        except Exception as e:
            return f"Erro ao salvar depósito: {e}"
    
    corretoras = Corretora.buscar_todas()
    depositos = Deposito.buscar_todos()
    
    return render_template('depositos.html',
                         corretoras=corretoras,
                         depositos=depositos)

@app.route('/notas', methods=['GET', 'POST'])
def notas_corretagem():
    if request.method == 'POST':
        try:
            print("=== INICIANDO PROCESSAMENTO DA NOTA ===")
            
            # Criar nota de corretagem
            data = request.form['data']
            corretora_id = request.form['corretora_id']
            numero_nota = request.form['numero_nota']
            valor_total = float(request.form['valor_total'])
            
            print(f"Dados da nota: Data={data}, Corretora_ID={corretora_id}, N°={numero_nota}, Total={valor_total}")
            
            nota = NotaCorretagem(data=data, corretora_id=corretora_id, 
                                numero_nota=numero_nota, valor_total=valor_total)
            nota_id = nota.salvar()
            
            print(f"Nota salva com ID: {nota_id}")
            
            # Processar operações
            operacoes_data = request.form.getlist('operacoes[]')
            print(f"Operações recebidas: {len(operacoes_data)}")
            
            operacoes_salvas = 0
            for i, op_data in enumerate(operacoes_data):
                if op_data and op_data.strip():
                    print(f"Processando operação {i}: {op_data}")
                    
                    try:
                        # Separar os dados da operação
                        partes = op_data.split('|')
                        print(f"Partes: {partes}")
                        
                        if len(partes) == 5:
                            ticker, tipo, quantidade, preco, total = partes
                            
                            # Validar e converter dados
                            if ticker.strip() and quantidade and preco:
                                operacao = Operacao(
                                    nota_id=nota_id,
                                    ticker=ticker.strip().upper(),
                                    tipo=tipo.strip(),
                                    quantidade=int(quantidade),
                                    preco=float(preco),
                                    total=float(total)
                                )
                                operacao.salvar()
                                operacoes_salvas += 1
                                print(f"✓ Operação {ticker} salva")
                            else:
                                print(f"✗ Dados inválidos na operação {i}")
                        else:
                            print(f"✗ Formato inválido: {len(partes)} partes")
                    except Exception as op_error:
                        print(f"✗ Erro na operação {i}: {op_error}")
                        continue
            
            print(f"=== PROCESSAMENTO FINALIZADO: {operacoes_salvas} operações salvas ===")
            
            return redirect(url_for('notas_corretagem'))
            
        except Exception as e:
            print(f"ERRO GRAVE: {e}")
            return f"Erro ao processar nota: {e}", 500
    
    corretoras = Corretora.buscar_todas()
    notas = NotaCorretagem.buscar_todas()
    
    return render_template('notas_corretagem.html',
                         corretoras=corretoras,
                         notas=notas)

@app.route('/nota/<int:nota_id>')
def detalhes_nota(nota_id):
    try:
        nota = NotaCorretagem.buscar_por_id(nota_id)
        operacoes = Operacao.buscar_por_nota(nota_id)
        
        print(f"Detalhes nota {nota_id}: {len(operacoes)} operações encontradas")
        
        return render_template('detalhes_nota.html',
                             nota=nota,
                             operacoes=operacoes)
    except Exception as e:
        return f"Erro ao carregar nota: {e}"

@app.route('/corretoras', methods=['GET', 'POST'])
def gerenciar_corretoras():
    if request.method == 'POST':
        try:
            nome = request.form['nome']
            if nome.strip():
                corretora = Corretora(nome=nome.strip())
                corretora.salvar()
            return redirect(url_for('gerenciar_corretoras'))
        except Exception as e:
            return f"Erro ao salvar corretora: {e}"
    
    corretoras = Corretora.buscar_todas()
    return render_template('corretoras.html', corretoras=corretoras)

@app.route('/debug')
def debug():
    try:
        from database import Database
        db = Database()
        
        result = "<h2>DEBUG - ESTADO DO SISTEMA</h2>"
        
        # Corretoras
        corretoras = Corretora.buscar_todas()
        result += f"<h3>Corretoras: {len(corretoras)}</h3>"
        for c in corretoras:
            result += f"ID: {c.id}, Nome: {c.nome}<br>"
        
        # Depósitos
        depositos = Deposito.buscar_todos()
        result += f"<h3>Depósitos: {len(depositos)}</h3>"
        for d in depositos:
            result += f"ID: {d.id}, Data: {d.data}, Corretora: {d.corretora_nome}, Valor: {d.valor}<br>"
        
        # Notas
        notas = NotaCorretagem.buscar_todas()
        result += f"<h3>Notas: {len(notas)}</h3>"
        for n in notas:
            result += f"ID: {n.id}, Data: {n.data}, Corretora: {n.corretora_nome}, Total: {n.valor_total}<br>"
            
            # Operações de cada nota
            operacoes = Operacao.buscar_por_nota(n.id)
            result += f"  Operações: {len(operacoes)}<br>"
            for op in operacoes:
                result += f"  - Ticker: {op.ticker}, Tipo: {op.tipo}, Qtd: {op.quantidade}, Preço: {op.preco}, Total: {op.total}<br>"
        
        return result
    except Exception as e:
        return f"Erro no debug: {e}"

@app.route('/fix_operations')
def fix_operations():
    """Rota de emergência para verificar operações"""
    from database import Database
    db = Database()
    
    # Ver todas as operações no banco
    operacoes = db.fetch_all("SELECT * FROM operacoes")
    result = f"<h2>OPERACOES NO BANCO: {len(operacoes)}</h2>"
    
    for op in operacoes:
        result += f"ID: {op[0]}, Nota_ID: {op[1]}, Ticker: {op[2]}, Tipo: {op[3]}, Qtd: {op[4]}, Preço: {op[5]}, Total: {op[6]}<br>"
    
    return result

if __name__ == '__main__':
    # Criar corretoras padrão se não existirem
    try:
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
                'Inter',
                'Agora',
                'Toro Investimentos'
            ]
            
            for nome in corretoras_padrao:
                corretora = Corretora(nome=nome)
                corretora.salvar()
            
            print("Corretoras criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar corretoras padrão: {e}")
    
    app.run(debug=True, port=5000)
