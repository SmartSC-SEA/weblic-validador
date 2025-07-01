import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scripts.config.alerta_email import enviar_log_por_email
from schema_utils import coletar_schema, salvar_snapshot, carregar_snapshot_anterior, comparar_snapshots, gerar_log



if not os.path.exists('snapshots'):
    os.makedirs('snapshots')

if not os.path.exists('logs'):
    os.makedirs('logs')

print("🔍 Coletando schema atual do DW...")
schema_atual = coletar_schema()
arquivo_snapshot = salvar_snapshot(schema_atual)
print(f"📥 Snapshot salvo em: {arquivo_snapshot}")

snapshot_anterior = carregar_snapshot_anterior(arquivo_snapshot)

if snapshot_anterior is None:
    print("ℹ️ Nenhum snapshot anterior para comparar ou sem alterações detectadas.")
else:
    print("🔗 Comparando com o snapshot anterior...")
    resultado = comparar_snapshots(snapshot_anterior, schema_atual)

    # Verificar se houve qualquer alteração
    houve_diferenca = any(len(itens) > 0 for itens in resultado.values())    

    arquivo_log = gerar_log(resultado)
    print(f"📝 Log gerado em: {arquivo_log}")

    if houve_diferenca:
        print("🚨 Diferença detectada no schema! Enviando alerta por e-mail...")
        caminho_logs = os.path.join('schema_monitor', 'logs')
        enviar_log_por_email(caminho_logs)
    else:
        print("✅ Nenhuma diferença detectada. Nenhum alerta enviado.")
