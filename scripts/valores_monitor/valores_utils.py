import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scripts.config.conexao_boavista import conectar_impala_vw
from scripts.config.config import VW_VALIDACAO
from datetime import datetime
import os
from scraping_weblic import (
    obter_valor_referencia,
    obter_valor_homologado_modalidade_padrao,
    obter_valor_homologado_pe_parcial,
    obter_valor_homologado_pe_pdf
)

view_validacao = VW_VALIDACAO

def obter_amostra_dw(qtd):
    conn = conectar_impala_vw()
    cursor = conn.cursor()

    query = f"""
    SELECT cod_processo, total_valor_referencia, total_valor_homologado,
           cod_orgao_promotor, num_processo_edital, num_processo_edital_ano,
           cod_processo_modalidade, sgl_processo_modalidade, sta_processo_homologacao_parcial, edital_completo
    FROM {view_validacao}
    WHERE sta_processo_resultado = 'HOMOLOGADO'
    AND rand() < 0.05
    LIMIT {qtd}
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    processos = []
    for row in rows:
        processos.append({
            "cod_processo": row[0],
            "total_valor_referencia": row[1],
            "total_valor_homologado": row[2],
            "cod_orgao_promotor": row[3],
            "num_processo_edital": row[4],
            "num_processo_edital_ano": row[5],
            "cod_processo_modalidade": row[6],
            "sgl_processo_modalidade": row[7],
            "sta_processo_homologacao_parcial": row[8],
            "edital_completo": row[9]
        })

    conn.close()
    return processos


def obter_valores_weblic(processo):
    valor_ref = obter_valor_referencia(
        processo["cod_orgao_promotor"],
        processo["num_processo_edital"],
        processo["num_processo_edital_ano"],
        processo["cod_processo_modalidade"]
    )

    if processo["sgl_processo_modalidade"] == "PE":
        if processo["sta_processo_homologacao_parcial"] == 1:
            valor_homologado = obter_valor_homologado_pe_parcial(processo["cod_processo"])
        else:
            valor_homologado = obter_valor_homologado_pe_pdf(processo["cod_processo"])
    else:
        valor_homologado = obter_valor_homologado_modalidade_padrao(processo["cod_processo"])

    return {
        "valor_estimado": valor_ref,
        "valor_homologado": valor_homologado
    }


def comparar_valores(cod_processo, edital_completo,valores_dw, valores_weblic):
    status = "OK" if valores_dw == valores_weblic else "Divergente"
    return {
        "cod_processo": cod_processo,
        "edital_completo": edital_completo,
        "valores_dw": valores_dw,
        "valores_weblic": valores_weblic,
        "status": status
    }


def gerar_log(resultados):
    logs_dir = os.path.join(os.path.dirname(__file__),"logs")
    os.makedirs(logs_dir, exist_ok=True)

    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"log_valores_{data_hora}.txt")

    with open(log_file, "w", encoding="utf-8") as f:
        for r in resultados:
            f.write(str(r) + "\n")

    print(f"📝 Log salvo em {log_file}")
