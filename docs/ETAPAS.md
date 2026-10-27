**Checklist do projeto**

Marcar uma etapa somente depois de implementar e validar seus criterios. Testes de regras acompanham a funcionalidade; a etapa final amplia a verificacao integrada. Consulte [o escopo completo](ESCOPO.md) para requisitos e decisoes.

- [x] 0. Ler o desafio e documentar escopo, regras e decisoes propostas.
- [x] 1. Ambiente: ferramentas, Git, protecao de credenciais, Compose e MySQL saudavel. Guia: [AMBIENTE.md](AMBIENTE.md). Validado localmente; commits aguardam revisao do candidato.
- [ ] 2. Base Django: dependencias, projeto, conexao MySQL, usuario customizado antes da primeira migration e endpoint de saude.
- [ ] 3. Base Next.js: TypeScript, estrutura, estilos e comunicacao com a API pelo mesmo dominio.
- [ ] 4. Autenticacao: sessao, CSRF, papeis, permissoes e dados demonstrativos.
- [ ] 5. Catalogo: consulta ao DummyJSON, busca, categorias, copia local de atributos e imagens e tratamento de falhas.
- [ ] 6. Lotes: publicacao, datas, valores, estados, vitrine e painel do leiloeiro.
- [ ] 7. Carteira: deposito simulado, saldo total/disponivel e movimentacoes idempotentes.
- [ ] 8. Lances: validacoes, reservas, liberacao, concorrencia e prorrogacao.
- [ ] 9. Sala: atualizacao sem recarregar, cronometro, historico, posicao e mensagens de feedback.
- [ ] 10. Encerramento: processo continuo, liquidacao unica, comprador/vendedor e lotes sem vencedor.
- [ ] 11. Arremates: participacoes, resultados e comprovante publico compartilhavel.
- [ ] 12. Cancelamento: permissao do dono, liberacao automatica, historico preservado e exclusao da vitrine.
- [ ] 13. Auditoria: cadeia autenticada, testemunho independente, reconciliacao, verificacao publica e privacidade.
- [ ] 14. Busca e filtros locais de lotes, ordenacao e paginacao.
- [ ] 15. Tema claro/escuro, persistencia de preferencia e acabamento responsivo/acessivel.
- [ ] 16. Validacao integrada: testes de navegador, concorrencia no MySQL, falhas externas e recuperacao; CI.
- [ ] 17. Deploy: HTTPS, persistencia, segredos, migrations, processo de encerramento e demonstracao publica. Publicar uma base minima cedo.
- [ ] 18. Entrega: README reproduzivel, contas demo, lote aberto, limitacoes, relato de IA e links exigidos.

Em cada marco: explicar a regra, implementar uma unidade pequena, validar e sinalizar o commit. Usar branches curtas e commits coesos; nao publicar credenciais.

Mensagens iniciais sugeridas:

1. `docs(scope): define requisitos e plano de entrega`
2. `chore(env): configura ambiente local e MySQL com Docker`
3. `chore(backend): inicializa Django com MySQL`
4. `chore(frontend): inicializa Next.js com TypeScript`
