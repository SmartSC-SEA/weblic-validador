# Weblic Validador

Este projeto realiza a raspagem dos dados públicos do Weblic (Sistema de Compras Públicas de SC) via requisições HTTP, com objetivo de validar os valores no Data Warehouse (DW) Boavista.

## 🔍 Objetivo

Comparar os valores de referência, adjudicados e homologados entre o sistema Weblic e os dados carregados no DW.

## 🧱 Estrutura

- `scripts/`: scripts principais de scraping e validação
- `scripts/config/`: arquivos de configuração e conexão
- `logs/`: arquivos de log da execução
- `docs/`: explicações técnicas e metodológicas

## ⚙️ Requisitos

- Python 3.10+
- Dependências:

```bash
pip install -r requirements.txt
```

## 🔐 Configuração

1. Renomeie `config.py.example` e `conexao_boavista.py.example` para `config.py` e `conexao_boavista.py`
2. Preencha os dados de API e banco

## 🚀 Execução

Rode o script principal de validação:

```bash
python scripts/valores_monitor.py
```

## ⚠️ Aviso

Este projeto utiliza apenas dados públicos extraídos do Weblic.