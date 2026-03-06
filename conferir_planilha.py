import pandas as pd
arquivo = 'Dados.xlsx'
aba = 'Transações'
df = pd.read_excel(arquivo, sheet_name=aba)
print('Colunas:', list(df.columns))
print('Primeira linha:')
print(df.iloc[0])
print('Tipos:')
print(df.dtypes)
print('Resumo estatístico:')
print(df.describe())