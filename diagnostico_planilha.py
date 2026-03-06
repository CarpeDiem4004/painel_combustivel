import pandas as pd

# Lê a planilha
arquivo = 'Dados.xlsx'
aba = 'Transações'
df = pd.read_excel(arquivo, sheet_name=aba)

# Mostra tipos das colunas principais
def mostra_tipos(col):
    print(f"Coluna: {col}")
    print('  Tipos:', df[col].dtype)
    print('  Exemplos:', df[col].unique()[:10])
    print('  Nulos:', df[col].isnull().sum())
    print('  Zeros:', (df[col]==0).sum())
    print()

for col in ['VALOR EMISSAO', 'VL/LITRO', 'LITROS']:
    if col in df.columns:
        mostra_tipos(col)
    else:
        print(f'Coluna não encontrada: {col}')

# Tenta converter para número e mostra linhas problemáticas
def confere_conversao(col):
    if col in df.columns:
        temp = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
        print(f'Conversão para número ({col}):')
        print('  Não numéricos:', temp.isnull().sum())
        print('  Primeiros não numéricos:')
        print(df.loc[temp.isnull(), col].head())
        print()

for col in ['VALOR EMISSAO', 'VL/LITRO', 'LITROS']:
    confere_conversao(col)
