#============================== PARTE 1

import requests
import json
import os
import sys

# Adiciona a raiz do projeto (pasta acima) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config

TOKEN_FILE = "token.json"


def atualizar_token():
    url = config.url_login
    payload = config.payload

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic YW5ndWxhcjpAbmd1bEByMA=="
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        dados = response.json()
        access_token = dados.get("access_token")

        if not access_token:
            raise Exception("❌ Não foi possível obter o access_token na resposta.")

        token = "Bearer " + access_token

        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)

        print("✅ Token atualizado com sucesso!")
        return token

    else:
        print(f"❌ Erro ao atualizar token: {response.status_code}")
        print(response.text)
        raise Exception("Erro no login do Weblic")




def carregar_token():
    if not os.path.exists(TOKEN_FILE):
        print("⚠️ Token não encontrado. Gerando novo...")
        return atualizar_token()

    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data["token"]


#============================== PARTE 2

from datetime import datetime


def obter_valores_processo_weblic(cod_processo):
    token = carregar_token()

    headers = {
        "Authorization": token,
        "Accept": "application/json"
    }

    # 1. Buscar dados do processo
    url_proc = f"{config.url_processos}/{cod_processo}"
    r = requests.get(url_proc, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Erro ao buscar dados do processo {cod_processo}: {r.status_code}")

    dados_proc = r.json()

    valor_estimado = dados_proc.get("valorEstimado")
    tipo_cotacao = (
        "item" if dados_proc.get("cotacao", {}).get("porItem")
        else "lote"
    )

    # 2. Buscar homologações
    url_homologacoes = f"{config.url_processos_get_homo}/{cod_processo}/homologacoes"
    r = requests.get(url_homologacoes, headers=headers)

    if r.status_code != 200:
        raise Exception(f"Erro ao buscar homologacoes do processo {cod_processo}: {r.status_code}")

    homologacoes = r.json()

    # 3. Montar dicionário {item_id: (data, valor)}
    itens_homologados = {}

    for homol in homologacoes:
        id_homol = homol.get("id")
        data_homol = datetime.fromisoformat(homol.get("data"))

        url_itens = f"{config.url_processo_get_items_homo_parcial}/{id_homol}/"
        url_itens += "itens" if tipo_cotacao == "item" else "lotes"

        r = requests.get(url_itens, headers=headers)
        if r.status_code != 200:
            raise Exception(f"Erro ao buscar itens da homologação {id_homol}: {r.status_code}")

        itens = r.json()

        for item in itens:
            item_id = item.get("id")
            valor_homol = item.get("valorHomologado", 0.0)

            if item_id not in itens_homologados:
                itens_homologados[item_id] = {"data": data_homol, "valor": valor_homol}
            else:
                if data_homol > itens_homologados[item_id]["data"]:
                    itens_homologados[item_id] = {"data": data_homol, "valor": valor_homol}

    # 4. Soma dos valores da última homologação válida de cada item
    valor_homologado = sum([v["valor"] for v in itens_homologados.values()])

    return {
        "valor_estimado": round(valor_estimado, 2) if valor_estimado else 0.0,
        "valor_homologado": round(valor_homologado, 2)
    }
