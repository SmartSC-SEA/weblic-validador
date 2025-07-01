import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scraping_weblic import atualizar_token
from valores_utils import obter_amostra_dw, obter_valores_weblic, comparar_valores, gerar_log


def main():
    atualizar_token()  # Atualiza o token antes de tudo

    processos = obter_amostra_dw(5)  # 🔧 Pode mudar a quantidade da amostra aqui

    resultados = []

    for proc in processos:
        cod_processo = proc["cod_processo"]
        edital_completo = proc["edital_completo"]
        print(f"🔍 Validando processo {cod_processo}...")

        try:
            valores_weblic = obter_valores_weblic(proc)
            valores_dw = {
                "valor_estimado": round(proc["total_valor_referencia"], 2),
                "valor_homologado": round(proc["total_valor_homologado"], 2)
            }

            resultado = comparar_valores(cod_processo, edital_completo, valores_dw, valores_weblic)
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
