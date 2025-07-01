from enum_utils import (
    coletar_enum_atual,
    salvar_snapshot_enum,
    carregar_referencia,
    comparar_com_referencia,
    gerar_log_enum
)
import sys, os

# Adiciona a raiz do projeto (pasta acima) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.config.alerta_email import  enviar_log_por_email


print("🔍 Coletando valores ENUM atuais...")
df_atual = coletar_enum_atual()

arquivo_snapshot = salvar_snapshot_enum(df_atual)
print(f"📥 Snapshot salvo em: {arquivo_snapshot}")

referencia = carregar_referencia()

if referencia is None:
    print("⚠️ Não há snapshot de referência. Crie o arquivo na pasta 'referencia/'.")
else:
    print("🔗 Comparando com a referência padrão...")

    resultado = comparar_com_referencia(df_atual, referencia)

    houve_diferenca = any(len(itens) > 0 for itens in resultado.values())

    arquivo_log = gerar_log_enum(resultado)
    print(f"📝 Log gerado em: {arquivo_log}")

    if houve_diferenca:
        print("🚨 Diferença detectada nos ENUMs! Enviando alerta por e-mail...")
        caminho_logs = os.path.join('enum_monitor', 'logs')
        enviar_log_por_email(caminho_logs)
    else:
        print("✅ Nenhuma diferença detectada. Nenhum alerta enviado.")
