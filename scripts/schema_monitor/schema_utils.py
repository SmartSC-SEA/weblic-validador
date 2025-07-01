import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scripts.config.conexao_boavista import conectar_impala
from scripts.config.config import SCHEMA_PREFIX
import pandas as pd
from datetime import datetime


# Define o caminho absoluto da pasta onde o script está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Caminhos das pastas específicas
PASTA_SNAPSHOTS = os.path.join(os.path.dirname(__file__),"snapshots")
PASTA_LOGS = os.path.join(os.path.dirname(__file__),"logs")

# Cria as pastas se não existirem
os.makedirs(PASTA_SNAPSHOTS, exist_ok=True)
os.makedirs(PASTA_LOGS, exist_ok=True)

def coletar_schema():
    conn = conectar_impala()
    cursor = conn.cursor()

    # Listar tabelas com 'weblic' no nome
    cursor.execute(f"SHOW TABLES")
    tabelas = [row[0] for row in cursor.fetchall() if SCHEMA_PREFIX in row[0]]

    schema_data = []

    for tabela in tabelas:
        cursor.execute(f"DESCRIBE {tabela}")
        descricao = cursor.fetchall()

        for idx, linha in enumerate(descricao):
            coluna, tipo = linha[0], linha[1]
            if coluna == '':
                continue  # Ignora linhas vazias que aparecem às vezes no DESCRIBE
            schema_data.append({
                "tabela": tabela,
                "coluna": coluna,
                "tipo": tipo,
                "posicao": idx + 1
            })

    df = pd.DataFrame(schema_data)
    conn.close()
    return df


def salvar_snapshot(df):
    data = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = os.path.join(PASTA_SNAPSHOTS, f'snapshot_schema_{data}.csv')
    df.to_csv(nome_arquivo, index=False)
    return nome_arquivo


def carregar_snapshot_anterior(snapshot_atual):
    arquivos = sorted(os.listdir(PASTA_SNAPSHOTS))

    # Remove o snapshot atual da lista
    arquivos = [f for f in arquivos if f != os.path.basename(snapshot_atual)]

    if not arquivos:
        return None

    caminho = os.path.join(PASTA_SNAPSHOTS, arquivos[-1])
    return pd.read_csv(caminho)


def comparar_snapshots(snapshot_antigo, snapshot_atual):
    resultado = {
        "tabelas_adicionadas": [],
        "tabelas_removidas": [],
        "colunas_adicionadas": [],
        "colunas_removidas": [],
        "tipos_alterados": []
    }

    tabelas_antigas = set(snapshot_antigo['tabela'].unique())
    tabelas_atuais = set(snapshot_atual['tabela'].unique())

    resultado['tabelas_adicionadas'] = list(tabelas_atuais - tabelas_antigas)
    resultado['tabelas_removidas'] = list(tabelas_antigas - tabelas_atuais)

    colunas_antigas = set(zip(snapshot_antigo['tabela'], snapshot_antigo['coluna']))
    colunas_atuais = set(zip(snapshot_atual['tabela'], snapshot_atual['coluna']))

    resultado['colunas_adicionadas'] = list(colunas_atuais - colunas_antigas)
    resultado['colunas_removidas'] = list(colunas_antigas - colunas_atuais)

    df_merged = pd.merge(
        snapshot_antigo, snapshot_atual,
        on=['tabela', 'coluna'], how='inner', suffixes=('_antigo', '_atual')
    )

    tipos_diferentes = df_merged[df_merged['tipo_antigo'] != df_merged['tipo_atual']]

    for _, linha in tipos_diferentes.iterrows():
        resultado['tipos_alterados'].append({
            "tabela": linha['tabela'],
            "coluna": linha['coluna'],
            "tipo_antigo": linha['tipo_antigo'],
            "tipo_atual": linha['tipo_atual']
        })

    return resultado


def gerar_log(resultado):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nome_arquivo = os.path.join(PASTA_LOGS, f'log_schema_{datetime.now().strftime("%Y%m%d")}.txt')

    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f'Log de validação de schema - {data_hora}\n\n')

        for chave, itens in resultado.items():
            f.write(f'{chave.upper()}:\n')
            if not itens:
                f.write('  Nenhum.\n')
            else:
                for item in itens:
                    f.write(f'  {item}\n')
            f.write('\n')

    return nome_arquivo
