import sys
import os

# Adiciona a raiz do projeto (pasta acima) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from conexao_boavista import conectar_impala

def testar_conexao():
    try:
        print("🔌 Tentando conectar no Impala...")

        conn = conectar_impala()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tabelas = cursor.fetchall()

        print("✅ Conexão bem-sucedida!")
        print("📋 Listando as primeiras 10 tabelas:")

        for tabela in tabelas[:10]:
            print(f" - {tabela[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Erro ao conectar no Impala:")
        print(e)


if __name__ == "__main__":
    testar_conexao()
