import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
# imports
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import ALERTA_EMAIL

def enviar_log_por_email(caminho_logs):
    nome_log, conteudo_log = obter_ultimo_log(caminho_logs)

    if not nome_log:
        print("⚠️ Nenhum log encontrado para envio.")
        return

    assunto = f"🛠️ Auditoria DW Weblic — Log {nome_log}"
    mensagem = conteudo_log

    enviar_email(assunto, mensagem)



def obter_ultimo_log(caminho_logs):
    if not os.path.exists(caminho_logs):
        print(f"⚠️ Pasta de logs '{caminho_logs}' não encontrada.")
        return None, None

    arquivos = sorted(os.listdir(caminho_logs))
    if not arquivos:
        print(f"⚠️ Nenhum log encontrado na pasta '{caminho_logs}'.")
        return None, None

    ultimo_log = arquivos[-1]
    caminho_log = os.path.join(caminho_logs, ultimo_log)

    with open(caminho_log, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    return ultimo_log, conteudo


def enviar_email(assunto, mensagem):
    if not ALERTA_EMAIL["ativado"]:
        print("🔕 Alerta de e-mail está desativado no config.")
        return

    try:
        # Configurações
        smtp_server = ALERTA_EMAIL["smtp_server"]
        port = ALERTA_EMAIL["port"]
        user = ALERTA_EMAIL["user"]
        password = ALERTA_EMAIL["password"]
        destinatarios = ALERTA_EMAIL["destinatarios"]

        # Montar e-mail
        email = MIMEMultipart()
        email['From'] = user
        email['To'] = ", ".join(destinatarios)
        email['Subject'] = assunto

        email.attach(MIMEText(mensagem, 'plain'))

        # Enviar
        with smtplib.SMTP(smtp_server, port) as servidor:
            servidor.starttls()
            servidor.login(user, password)
            servidor.send_message(email)

        print("✅ E-mail enviado com sucesso!")

    except Exception as e:
        print("❌ Falha ao enviar e-mail:")
        print(e)
