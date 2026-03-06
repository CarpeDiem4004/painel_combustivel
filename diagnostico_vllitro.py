import pandas as pd

arquivo = 'Dados.xlsx'
aba = 'Transações'
df = pd.read_excel(arquivo, sheet_name=aba)

print('Colunas:', list(df.columns))

# Diagnóstico da coluna VL/LITRO
colunas_possiveis = ['VL/LITRO', 'Valor por litro', 'Preço Médio', 'PREÇO MÉDIO']
col_encontrada = None
for col in colunas_possiveis:
    if col in df.columns:
        col_encontrada = col
        break
if col_encontrada:
    print(f'Coluna encontrada para preço médio: {col_encontrada}')
    print('Primeiros valores:', df[col_encontrada].head(10))
    # Conversão para float
    serie = df[col_encontrada].astype(str).str.replace(',', '.').str.replace(r'[^0-9.\-]', '', regex=True)
    serie = pd.to_numeric(serie, errors='coerce')
    print('Primeiros valores convertidos:', serie.head(10))
    print('Valores únicos:', serie.unique()[:10])
    print('Nulos:', serie.isnull().sum())
    print('Entre 2 e 10:', serie[(serie >= 2) & (serie <= 10)].count())
    print('Média entre 2 e 10:', serie[(serie >= 2) & (serie <= 10)].mean())
else:
    print('Nenhuma coluna de preço médio encontrada!')
