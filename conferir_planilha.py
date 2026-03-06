import pandas as pd

df = pd.read_excel('Dados.xlsx', sheet_name='Transações')
print('Colunas:', list(df.columns))
print('Tipos de dados:')
print(df.dtypes)
print('Primeiras linhas:')
print(df.head())
print('Valores nulos por coluna:')
print(df.isnull().sum())