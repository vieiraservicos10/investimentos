# **Sistema de Controle de Investimentos**

Sistema completo para controle de investimentos em bolsa de valores, com gestão de múltiplas corretoras, registro de depósitos e notas de corretagem.

## **📋 Funcionalidades**

### **✅ Gestão de Corretoras**
- Cadastro de múltiplas corretoras
- Controle individual por corretora
- Listagem e organização

### **✅ Registro de Depósitos**
- Controle de valores depositados em cada corretora
- Histórico completo de depósitos
- Data e valor dos aportes

### **✅ Notas de Corretagem**
- Cadastro completo de notas de corretagem
- Múltiplas operações por nota (compras e vendas)
- Cálculo automático de totais
- Detalhamento completo das operações

### **✅ Dashboard Inteligente**
- **Saldo por Corretora**: Visualização individualizada
- **Cálculos Automáticos**:
  - Total depositado
  - Total em compras
  - Total em vendas  
  - Saldo disponível
  - Carteira atual com preço médio
- **Histórico**: Últimos depósitos e notas

## **🛠️ Tecnologias**

- **Backend**: Python + Flask
- **Banco de Dados**: SQLite
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Templates**: Jinja2

## **🚀 Instalação e Execução**

### **Pré-requisitos**
- Python 3.8+
- pip (gerenciador de pacotes Python)

### **1. Clone ou Baixe os Arquivos**
```bash
# Estrutura do projeto
sistema_investimentos/
├── app.py
├── database.py
├── models.py
├── requirements.txt
└── templates/
    ├── base.html
    ├── index.html
    ├── corretoras.html
    ├── depositos.html
    ├── notas_corretagem.html
    └── detalhes_nota.html
```

### **2. Instale as Dependências**
```bash
pip install -r requirements.txt
```

### **3. Execute o Sistema**
```bash
python app.py
```

### **4. Acesse no Navegador**
```
http://localhost:5000
```

## **📊 Como Usar**

### **Fluxo Recomendado:**

1. **Cadastre suas Corretoras**
   - Acesse: `Corretoras` no menu
   - Adicione todas as corretoras que utiliza

2. **Registre os Depósitos**
   - Acesse: `Depósitos` no menu  
   - Informe data, corretora e valor depositado

3. **Cadastre as Notas de Corretagem**
   - Acesse: `Notas` no menu
   - Preencha os dados da nota
   - Adicione as operações (compras/vendas)
   - O sistema calcula automaticamente os totais

4. **Acompanhe no Dashboard**
   - Veja saldos por corretora
   - Acompanhe a carteira atual
   - Verifique o histórico de operações

## **🎯 Estrutura do Banco de Dados**

### **Tabelas Principais:**

- **corretoras**: Cadastro das corretoras
- **depositos**: Registro de depósitos por corretora  
- **notas_corretagem**: Cabeçalho das notas
- **operacoes**: Operações individuais (compras/vendas) de cada nota

### **Relacionamentos:**
```
corretoras (1) ← (N) depositos
corretoras (1) ← (N) notas_corretagem  
notas_corretagem (1) ← (N) operacoes
```

## **📈 Cálculos Automáticos**

### **Saldo por Corretora:**
```
Saldo Disponível = Total Depositado - Total Compras + Total Vendas
```

### **Carteira:**
- Quantidade atual por ativo
- Valor total investido
- Preço médio de custo

### **Totais Gerais:**
- Soma de todos os depósitos
- Soma de todas as compras
- Soma de todas as vendas
- Saldo disponível total

## **🔧 Rotas de Debug**

Para desenvolvimento e troubleshooting:

- **`/debug`**: Estado completo do sistema
- **`/fix_operations`**: Ver todas as operações no banco

## **📝 Exemplo de Uso**

### **Cenário Típico:**
1. **Depósito**: R$ 10.000 na XP Investimentos
2. **Nota de Corretagem**:
   - Compra: 100 PETR4 @ R$ 25,00 = R$ 2.500,00
   - Compra: 50 VALE3 @ R$ 65,00 = R$ 3.250,00
   - Total da nota: R$ 5.750,00

### **Resultado no Dashboard:**
- **Saldo XP**: R$ 10.000,00 - R$ 5.750,00 = R$ 4.250,00
- **Carteira**: PETR4 (100 ações), VALE3 (50 ações)
- **Preço Médio**: Calculado automaticamente

## **⚠️ Observações Importantes**

- Os dados são armazenados localmente (SQLite)
- Backup regular do arquivo `investimentos.db` é recomendado
- Sistema desenvolvido para uso pessoal
- Cálculos validados e testados

## **🆘 Suporte**

Em caso de problemas:

1. Verifique os logs no terminal
2. Use as rotas de debug (`/debug`)
3. Confirme que todas as dependências estão instaladas

## **📄 Licença**

Sistema desenvolvido para uso educacional e pessoal.

---

**🎯 Objetivo**: Controle preciso e organizado dos investimentos em múltiplas corretoras com cálculos automáticos confiáveis.# investimentos
