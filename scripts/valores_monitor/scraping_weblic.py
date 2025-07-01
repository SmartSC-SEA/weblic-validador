import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# imports
from scripts.config import config
import requests
import json
import os
from datetime import datetime
import sys


TOKEN_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'token.json')


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
        token = "Bearer " + dados.get("access_token")
        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)
        return token
    else:
        raise Exception("Erro no login Weblic")


def carregar_token():
    if not os.path.exists(TOKEN_FILE):
        return atualizar_token()
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
        return data["token"]


def request_seguro(method, url, **kwargs):
    token = carregar_token()
    headers = kwargs.get("headers", {})
    headers["Authorization"] = token
    headers["Accept"] = "application/json"
    kwargs["headers"] = headers

    response = requests.request(method, url, **kwargs)
    if response.status_code == 401:
        token = atualizar_token()
        headers["Authorization"] = token
        response = requests.request(method, url, **kwargs)

    return response


def obter_valor_referencia(cod_orgao, num_edital, ano_edital, cod_modalidade):
    url = f"{config.url_padrao_get_val_ref}idOrgao={cod_orgao}&numeroProcesso={num_edital}&anoProcesso={ano_edital}&idModalidade={cod_modalidade}"
    r = request_seguro("GET", url)
    data = r.json()

    content = data.get("content", [])
    if content:
        valor = content[0].get("valorEstimado", 0.0)
    else:
        valor = 0.0

    return round(valor, 2)



def obter_valor_homologado_modalidade_padrao(id_processo):
    url = f"{config.url_padrao_result}/{id_processo}/resultados"
    r = request_seguro("GET", url)
    itens = r.json()

    total = sum(item.get("melhorLance", 0) * item.get("quantidade", 0) for item in itens)
    return round(total, 2)


def obter_valor_homologado_pe_parcial(id_processo):
    url_homologacoes = f"{config.url_padrao_result}/{id_processo}/homologacoes"
    r = request_seguro("GET", url_homologacoes)
    homologacoes = r.json()

    itens_map = {}

    for homol in homologacoes:
        id_homol = homol["id"]
        data_homol = datetime.fromisoformat(homol["data"])

        url_itens = f"{config.url_padrao_get_itens_homo_parc}/{id_homol}/itens"
        r = request_seguro("GET", url_itens)
        itens = r.json()

        for item in itens:
            item_id = item["itemId"]
            valor = item.get("valorHomologadoTotal", 0.0)

            if item_id not in itens_map or data_homol > itens_map[item_id]["data"]:
                itens_map[item_id] = {"data": data_homol, "valor": valor}

    total = sum(v["valor"] for v in itens_map.values())
    return round(total, 2)


def obter_valor_homologado_pe_pdf(id_processo):
    raise NotImplementedError("Integração com PDF ainda não implementada.")
