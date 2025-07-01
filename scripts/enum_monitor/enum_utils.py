import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scripts.config.conexao_boavista import  conectar_impala
import pandas as pd
from datetime import datetime


# === Pasta Base ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# === Caminhos ===
PASTA_SNAPSHOTS = os.path.join(os.path.dirname(__file__),"snapshots")
PASTA_REFERENCIA = os.path.join(os.path.dirname(__file__),"referencia")
PASTA_LOGS = os.path.join(os.path.dirname(__file__),"logs")

# Cria pastas se não existirem
os.makedirs(PASTA_SNAPSHOTS, exist_ok=True)
os.makedirs(PASTA_REFERENCIA, exist_ok=True)
os.makedirs(PASTA_LOGS, exist_ok=True)


# === Lista de tabelas e campos ===
TABELAS_CAMPOS = {
    "fat_weblic_pedido_aquisicao": ["sta_pedido"],
    "fat_weblic_pedido_aquisicao_item": ["sta_item_pedido_estimado", "sta_item_pedido_nao_acumulativo", "tpo_produto"],
    "fat_weblic_processo": ["sta_processo_sistema_registro_preco", "sta_processo_homologacao_parcial", "sta_processo", "sta_processo_resultado"],
    "fat_weblic_processo_item_resultado": ["sta_item_processo", "sta_fornecedor_estrangeiro"],
    "fat_weblic_processo_subitem": ["sta_item_processo_estimado", "sta_item_processo_nao_acumulativo", "sta_item_processo_me_epp", "sta_item_processo_resultado", "sta_item_processo_lote", "tpo_produto"],
    "fat_weblic_requisicao": ["sta_requisicao", "tpo_requisicao"],
    "fat_weblic_requisicao_subitem": ["sta_item_requisicao_estimado", "sta_item_requisicao_nao_acumulativo", "tpo_produto"]
}


# === Função para coletar valores únicos ===
def coletar_enum_atual():
    conn = conectar_impala()
    cursor = conn.cursor()

    dados = []

    for tabela, campos in TABELAS_CAMPOS.items():
        for campo in campos:
            query = f"SELECT DISTINCT {campo} FROM {tabela}"
            try:
                cursor.execute(query)
                resultados = cursor.fetchall()

                for resultado in resultados:
                    valor = resultado[0]
                    dados.append({
                        'tabela': tabela,
                        'campo': campo,
                        'valor': str(valor) if valor is not None else 'NULL'
                    })

            except Exception as e:
                print(f"Erro na tabela {tabela}, campo {campo}: {e}")

    conn.close()

    df = pd.DataFrame(dados)
    return df


# === Função para salvar snapshot ===
def salvar_snapshot_enum(df):
    data = datetime.now().strftime('%Y%m%d_%H%M%S')
    caminho = os.path.join(PASTA_SNAPSHOTS, f'snapshot_enum_{data}.csv')
    df.to_csv(caminho, index=False)
    return caminho


# === Função para carregar referência ===
def carregar_referencia():
    caminho = os.path.join(PASTA_REFERENCIA, 'snapshot_enum_padrao.csv')
    if not os.path.exists(caminho):
        print("⚠️ Snapshot de referência não encontrado!")
        return None
    return pd.read_csv(caminho, dtype=str, keep_default_na=False)


# === Função para comparar ===
def comparar_com_referencia(snapshot_atual, referencia):
    atual = set(zip(snapshot_atual['tabela'], snapshot_atual['campo'], snapshot_atual['valor']))
    ref = set(zip(referencia['tabela'], referencia['campo'], referencia['valor']))

    novos = atual - ref
    removidos = ref - atual

    return {
        'valores_novos': list(novos),
        'valores_removidos': list(removidos)
    }


# === Função para gerar log ===
def gerar_log_enum(resultado):
    data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    nome_arquivo = f'log_enum_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    caminho_log = os.path.join(PASTA_LOGS, nome_arquivo)

    with open(caminho_log, 'w', encoding='utf-8') as f:
        f.write(f'Log de validação ENUM - {data_hora}\n\n')

        for chave, itens in resultado.items():
            f.write(f'{chave.upper()}:\n')
            if not itens:
                f.write('  Nenhum.\n')
            else:
                for item in itens:
                    f.write(f'  {item}\n')
            f.write('\n')

    return caminho_log
