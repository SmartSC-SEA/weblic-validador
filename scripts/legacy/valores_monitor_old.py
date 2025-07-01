from scraping_weblic import obter_valores_processo_weblic
from valores_utils import obter_amostra_dw, comparar_valores, gerar_log
import os


def main():
    # Obter amostra de processos do DW
    processos = obter_amostra_dw(qtd=5)  # ✅ Número configurável

    resultados = []

    for proc in processos:
        cod_processo = proc["cod_processo"]
        print(f"🔍 Validando processo {cod_processo}...")

        try:
            valores_weblic = obter_valores_processo_weblic(cod_processo)
            valores_dw = {
                "valor_estimado": round(proc["total_valor_referencia"], 2),
                "valor_homologado": round(proc["total_valor_homologado"], 2)
            }

            resultado = comparar_valores(cod_processo, valores_dw, valores_weblic)
            resultados.append(resultado)

        except Exception as e:
            print(f"❌ Erro no processo {cod_processo}: {e}")
            resultados.append({
                "cod_processo": cod_processo,
                "status": "Erro",
                "detalhes": str(e)
            })

    gerar_log(resultados)


if __name__ == "__main__":
    main()
