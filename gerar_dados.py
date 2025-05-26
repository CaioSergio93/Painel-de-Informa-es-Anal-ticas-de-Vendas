import pandas as pd
import numpy as np
from random import choice, randint
from datetime import datetime, timedelta
import os

# Criar pasta se não existir
os.makedirs('data', exist_ok=True)

# Clientes
clientes = pd.DataFrame({
    'id_cliente': range(1, 11),
    'nome': [f'Cliente {i}' for i in range(1, 11)],
    'cidade': np.random.choice(['Recife', 'São Paulo', 'Salvador', 'Fortaleza', 'Curitiba'], 10),
    'estado': np.random.choice(['PE', 'SP', 'BA', 'CE', 'PR'], 10),
    'sexo': np.random.choice(['M', 'F'], 10),
    'idade': np.random.randint(18, 65, 10)
})
clientes.to_csv('data/clientes.csv', index=False)

# Produtos
produtos = pd.DataFrame({
    'id_produto': range(1, 6),
    'nome_produto': ['Notebook Lenovo', 'Mouse Logitech', 'Monitor LG', 'Teclado Redragon', 'HD Externo Seagate'],
    'categoria': ['Informática', 'Acessórios', 'Informática', 'Acessórios', 'Armazenamento'],
    'fornecedor_id': [1, 2, 1, 2, 1]
})
produtos.to_csv('data/produtos.csv', index=False)

# Vendedores
vendedores = pd.DataFrame({
    'id_vendedor': range(1, 4),
    'nome': ['José Lima', 'Fernanda Souza', 'Rafael Torres'],
    'região': ['Nordeste', 'Sudeste', 'Sul']
})
vendedores.to_csv('data/vendedores.csv', index=False)

# Fornecedores
fornecedores = pd.DataFrame({
    'id_fornecedor': [1, 2],
    'nome_empresa': ['TechFornece Ltda', 'InfoService SA'],
    'cidade': ['São Paulo', 'Rio de Janeiro'],
    'estado': ['SP', 'RJ']
})
fornecedores.to_csv('data/fornecedores.csv', index=False)

# Gerar vendas de 2022 a 2024
vendas = []
id_venda = 1
for ano in [2022, 2023, 2024]:
    for _ in range(100):  # 100 vendas por ano
        data = datetime(ano, randint(1, 12), randint(1, 28))
        id_cliente = choice(clientes['id_cliente'])
        id_produto = choice(produtos['id_produto'])
        id_vendedor = choice(vendedores['id_vendedor'])
        quantidade = randint(1, 5)
        valor_unitario = randint(100, 3000)
        valor_total = quantidade * valor_unitario
        vendas.append([
            id_venda, id_cliente, id_produto, id_vendedor,
            data.strftime('%Y-%m-%d'), quantidade, valor_total
        ])
        id_venda += 1

df_vendas = pd.DataFrame(vendas, columns=[
    'id_venda', 'id_cliente', 'id_produto', 'id_vendedor',
    'data', 'quantidade', 'valor_total'
])
df_vendas.to_csv('data/vendas.csv', index=False)

print("✅ Arquivos CSV com dados para 3 anos gerados na pasta 'data/'")
