# Metodologia de Validação dos Dados do Weblic

## Etapas:

1. **Raspagem** dos endpoints públicos do Weblic (processos, itens, arquivos).
2. **Extração** de dados complementares de PDFs (se necessário).
3. **Comparação** com dados do DW (Boavista).
4. **Registro** de divergências em logs ou tabelas temporárias.
5. **Validação manual** em casos de erro ou inconsistência.

## Notas

- O projeto não expõe credenciais ou informações sensíveis.
- A raspagem respeita os limites e regras do site.