from conexao_boavista import conectar_impala_vw
import pandas as pd
from datetime import datetime
import os


def obter_amostra_dw(qtd=5):
    conn = conectar_impala_vw()
    cursor = conn.cursor()

    query = f"""
    SELECT cod_processo, total_valor_referencia, total_valor_homologado
    FROM vw_weblic_val_ref_e_val_homo
    WHERE sta_processo_resultado = 'HOMOLOGADO'
    ORDER BY rand()
    LIMIT {qtd}
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    processos = []
    for row in rows:
        processos.append({
            "cod_processo": row[0],
            "total_valor_referencia": row[1],
            "total_valor_homologado": row[2]
        })

    conn.close()
    return processos


def comparar_valores(cod_processo, valores_dw, valores_weblic):
    status = "OK" if valores_dw == valores_weblic else "Divergente"

    return {
        "cod_processo": cod_processo,
        "valores_dw": valores_dw,
        "valores_weblic": valores_weblic,
        "status": status
    }


def gerar_log(resultados):
    logs_dir = "valores_monitor/logs"
    os.makedirs(logs_dir, exist_ok=True)

    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"log_valores_{data_hora}.txt")

    with open(log_file, "w", encoding="utf-8") as f:
        for r in resultados:
            f.write(str(r) + "\n")

    print(f"📝 Log salvo em {log_file}")
