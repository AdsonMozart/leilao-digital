**Escopo do desafio — Leilão Digital / Verzel**

Planejamento baseado na leitura das sete páginas do PDF fornecido e na documentação oficial consultada em 24/10/2026. Este documento descreve a implementação futura; não representa funcionalidades já implementadas.

O enunciado define os requisitos. As escolhas de arquitetura e as interpretações identificadas como decisões propostas são recomendações para implementar esses requisitos com simplicidade. Os cinco opcionais entram no escopo por decisão do candidato.

**1. Objetivo e entrega**

Construir uma casa de leilões de produtos do DummyJSON. O leiloeiro seleciona um produto externo, publica um lote e recebe o valor da venda. O licitante deposita dinheiro fictício, disputa lotes e acessa comprovantes. Visitantes consultam lotes, histórico e auditoria sem login.

Entregar repositório público no GitHub, aplicação pública funcionando, banco configurado, dados demonstrativos e README reproduzível. O PDF estabelece sete dias corridos a partir do recebimento; a data de recebimento ainda não foi informada.

O PDF dispensa nota fiscal, revenda entre usuários, aplicativo nativo e recuperação de senha. Pagamentos reais, frete e integração com estoque também não são necessários para o fluxo solicitado.

**2. Tecnologias e arquitetura propostas**

| Parte | Escolha e responsabilidade |
|---|---|
| Interface | React com Next.js e TypeScript: telas, formulários, temas e atualização dos dados |
| API | Python, Django e Django REST Framework: autenticação, permissões e todas as regras de negócio |
| Banco | MySQL 8.4 com InnoDB: dados persistentes, transações e bloqueios |
| Processo de encerramento | Comando Django executado continuamente em container próprio, usando o mesmo código da API |
| Execução | Docker Compose para banco, API, frontend, processo de encerramento e proxy |
| Acesso público | Proxy como Caddy: HTTPS e encaminhamento de `/api/` para Django e demais páginas para Next.js |
| Arquivos | Volume persistente para imagens locais e armazenamento independente do MySQL para testemunhos de auditoria |

Um repositório com `backend/`, `frontend/`, `infra/` e `docs/`. Dividir o Django em módulos pequenos: contas, catálogo, leilões e carteira. Regras como aceitar lance e liquidar lote ficam em funções de serviço explícitas, reutilizadas por endpoints e pelo processo de encerramento.

Base sugerida: Python 3.13 e Django 5.2 LTS, com patches de segurança atualizados. Fixar versões compatíveis das dependências no início, incluindo Next.js, Node e driver MySQL. A escolha usa uma linha do Django com suporte prolongado; Python 3.13 consta na matriz de compatibilidade. [Suporte do Django](https://www.djangoproject.com/download/), [compatibilidade com Python](https://docs.djangoproject.com/en/5.2/faq/install/#what-python-version-can-i-use-with-django).

Autenticação proposta: sessões do Django, cookie de sessão HttpOnly, Secure em produção e proteção CSRF também no login. Um único domínio simplifica cookies e chamadas da interface. Contas demonstrativas serão criadas por comando de seed; cadastro público não é requisito explícito e não é necessário para demonstrar o desafio.

**3. Papéis e permissões**

| Perfil | Permissões |
|---|---|
| Visitante | Vitrine, sala em modo de leitura, auditoria e comprovante compartilhado |
| Leiloeiro | Consultar produtos externos, criar e cancelar os próprios lotes, consultar resultados e total recebido; nunca dar lances |
| Licitante | Consultar carteira, depositar saldo fictício, dar lances, acompanhar participação e acessar arremates |

Validar papel e propriedade em cada endpoint protegido. Esconder um botão não constitui controle de acesso. Uma conta possui um papel de negócio; o cliente não pode alterar esse papel pelo payload. O superusuário técnico do Django não deve ser confundido com o perfil de leiloeiro.

**4. Telas e critérios de aceite**

| Tela | O que deve permitir verificar |
|---|---|
| Login | Entrada, saída, mensagens de erro e direcionamento conforme o papel |
| Vitrine | Separação entre agendados, ao vivo e encerrados; cancelados ausentes; paginação, busca e filtros |
| Painel do leiloeiro | Seus lotes, busca de produtos, criação, cancelamento, resultado de cada lote e soma das vendas liquidadas |
| Criação de lote | Produto com imagem e atributos, lance inicial, incremento mínimo, início e fim |
| Sala do lote | Lance atual, próximo mínimo, histórico, posição do participante, cronômetro, formulário e avisos de liderança/superação |
| Carteira | Saldo total, comprometido e disponível, depósito simulado e movimentações |
| Minhas participações e arremates | Todos os lotes em que participou, situação atual, lotes vencidos e respectivos comprovantes |
| Comprovante público | Produto, lote, valor, data, identificadores públicos das partes, código e link compartilhável |
| Auditoria pública | Histórico completo, ordenação verificável e resultado da checagem de integridade, sem exigir login |

Todas as telas devem ter estados de carregamento, vazio e erro; formulários acessíveis e interface utilizável no celular. O tema claro/escuro deve funcionar em todas elas, guardar a preferência e considerar o tema do sistema na primeira visita.

A sala fará polling aproximadamente a cada dois segundos enquanto estiver visível, além de atualizar imediatamente após ações locais. Isso atende à atualização sem recarregar a página; o atraso esperado deve ser documentado. O servidor retorna seu horário e o fim atualizado para sincronizar o contador. Dados da sala e da carteira não podem ser servidos de um cache desatualizado. WebSocket não é necessário para esta primeira entrega.

Posição proposta: ranking pelo melhor lance aceito de cada participante; quem nunca ofertou aparece como sem participação. Apenas o líder tem saldo comprometido. O usuário recebe mensagens específicas para lance abaixo do mínimo, saldo insuficiente, liderança atual, lote não iniciado, encerrado ou cancelado e falta de permissão.

**5. Produtos do DummyJSON e independência da API**

A integração será feita pelo Django. Endpoints externos necessários:

| Uso | Endpoint |
|---|---|
| Catálogo paginado | `GET https://dummyjson.com/products?limit=20&skip=0` |
| Busca | `GET https://dummyjson.com/products/search?q=phone` |
| Detalhes para criação | `GET https://dummyjson.com/products/{id}` |
| Categorias | `GET https://dummyjson.com/products/categories` |
| Produtos por categoria | `GET https://dummyjson.com/products/category/{slug}` |

A resposta da listagem contém `products`, `total`, `skip` e `limit`. Não fixar quantidade de produtos nem IDs de exemplos. Nome, descrição, categoria, marca quando existir, preço de referência e imagens fornecem os dados necessários. A API simula operações de escrita, portanto nossos lotes ficam no MySQL. [Documentação do DummyJSON](https://dummyjson.com/docs/products).

Ao criar um lote, o backend consulta o ID externo e salva uma cópia dos atributos selecionados, a origem e a data de importação. Baixa também a imagem principal para armazenamento próprio. Não confiar em um título ou preço externo arbitrário enviado pelo navegador.

Depois de publicado, o lote usa sua cópia local. Vitrine, sala, comprovante e auditoria não consultam o DummyJSON. Uma atualização do catálogo não modifica lotes existentes. Cache local de resultados recentes, timeout e poucas tentativas de recuperação protegem a pesquisa; na indisponibilidade, apresentar dados já importados ou explicar que uma nova importação está temporariamente indisponível.

Decisão proposta: valores do leilão em BRL fictício. O preço externo será apenas referência, sem conversão cambial implícita; o leiloeiro define o lance inicial. Estoque, descontos, frete e quantidade mínima do DummyJSON não viram regras de leilão. Cada lote representa uma unidade demonstrativa.

**6. Ciclo do lote e regras de lance**

Fluxo público: `AGENDADO → AO VIVO → ENCERRADO`. Cancelamento permitido antes do encerramento; lote cancelado não reabre. Separar o estado de negócio do processamento de liquidação para não mostrar um comprovante antes de concluir o pagamento.

| Regra | Critério verificável |
|---|---|
| Publicação | Produto válido, imagem local ou alternativa local, lance inicial positivo, incremento positivo, início válido e fim posterior ao início |
| Horários | Datas persistidas em UTC e exibidas no fuso do usuário; relógio do servidor decide |
| Janela de lances | Aceitar somente se `inicio <= agora < fim_efetivo`, sem cancelamento ou encerramento |
| Primeiro lance | Valor maior ou igual ao lance inicial |
| Próximos lances | Valor maior ou igual ao lance líder somado ao incremento mínimo |
| Liderança | O líder não pode aumentar o próprio lance |
| Saldo | O valor integral deve caber no saldo disponível do novo líder |
| Histórico | Somente lances aceitos compõem o histórico oficial; não editar nem excluir lances por endpoints |
| Disputa simultânea | Validar e gravar com bloqueio do lote e das carteiras envolvidas |

Uma disputa simultânea será resolvida pela ordem efetiva das transações no servidor. A segunda operação revalida mínimo, tempo e saldo depois de obter o bloqueio. Ela pode ser aceita se ainda satisfizer as regras; não há promessa de desempate pelo horário do navegador.

Decisão proposta para anti-sniping: um lance aceito quando faltarem até 120 segundos redefine `fim_efetivo = agora + 120 segundos`. Novos lances nessa janela podem repetir a prorrogação. Guardar também o fim original e registrar as prorrogações. O PDF não especifica com precisão se os dois minutos partem do lance ou do fim anterior; essa interpretação ficará explícita no README e isolada em uma função para ajuste.

Para limitar o escopo, termos financeiros e datas ficam imutáveis após a publicação. O gerenciamento é feito por criação, acompanhamento e cancelamento; o enunciado não exige edição genérica de lotes publicados.

**7. Carteira, concorrência e liquidação**

Usar `Decimal` no Python e `DECIMAL` no MySQL, sempre com duas casas decimais. Na API, dinheiro pode ser representado por strings decimais. Rejeitar valor negativo, zero quando não fizer sentido, casas excedentes e valores acima do limite definido. Não usar `float` para cálculos financeiros.

`saldo_disponivel = saldo_total - saldo_comprometido`

O comprometido é a soma das reservas dos lotes em que o usuário está liderando. Exemplo: com R$ 500 de saldo total e um lance líder de R$ 150, o disponível é R$ 350. Se outra pessoa superar esse lance, os R$ 150 voltam ao disponível sem aumentar o saldo total.

Ao aceitar um lance, na mesma transação: validar regras, reservar o valor do novo líder, liberar a reserva do anterior, criar o lance, atualizar liderança e eventual prorrogação. Bloquear carteiras em ordem consistente para reduzir deadlocks, inclusive quando uma pessoa disputa vários lotes. Repetições controladas usam a mesma chave de idempotência.

`transaction.atomic()` fornece tudo-ou-nada no banco; `select_for_update()` bloqueia os registros envolvidos até o fim da transação. Testar esse comportamento com MySQL real. [Transações do Django](https://docs.djangoproject.com/en/5.2/topics/db/transactions/), [bloqueio de registros](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update).

Um processo contínuo verifica lotes vencidos, por exemplo a cada segundo. Ao obter o bloqueio do lote, revalida o fim efetivo para respeitar uma prorrogação concorrente. Deve funcionar sem navegador aberto e recuperar lotes pendentes após reinício.

Com vencedor: reduzir o saldo total do comprador, consumir sua reserva, creditar a carteira do leiloeiro, registrar movimentações e gerar um comprovante único. Sem lances: encerrar sem vencedor, transferência ou comprovante de arremate. A mesma liquidação executada novamente não pode cobrar nem creditar outra vez. Não há taxa de venda prevista no enunciado.

Depósitos simulados também exigem idempotência para não duplicar crédito por repetição da requisição. Saldo total e disponível nunca podem ficar negativos. O total recebido do leiloeiro considera vendas efetivamente liquidadas, não lances ainda abertos.

**8. Cancelamento com estorno automático**

Requisito base: o dono cancela um lote ainda sem lances. Opcional incluído: permitir cancelar também um lote com lances, enquanto não estiver encerrado.

Decisão proposta: aceitar cancelamento de lote agendado ou ao vivo pelo próprio leiloeiro, com motivo registrado; rejeitar depois do término efetivo e após liquidação. Preservar o histórico e a auditoria e retirar o lote da vitrine. O detalhe público pode continuar acessível por link, identificado como cancelado.

Com lances, liberar imediatamente a reserva do líder, registrar a liberação e atualizar as interfaces. Como a cobrança só acontece no encerramento, esse estorno devolve disponibilidade e não acrescenta dinheiro ao saldo total. Participantes já superados não possuem reserva a devolver. Não emitir comprovante de venda.

Cancelamento, lance e liquidação disputam o mesmo bloqueio do lote. Repetir o cancelamento não pode gerar nova liberação. Reversão de uma venda já liquidada não faz parte dessa interpretação do opcional.

**9. Auditoria e privacidade**

O PDF exige detectar alteração, remoção e inserção posterior no histórico, inclusive diretamente no banco. Um hash simples, ou uma cadeia cujo único ponto de referência fique no mesmo banco, não cobre adequadamente esse requisito.

Projeto proposto: registros em ordem sequencial por lote, serialização determinística e HMAC-SHA-256 incluindo versão do formato, lote, sequência, identificador público do participante, valor, horário e assinatura anterior. A chave fica fora do MySQL e do Git. HMAC autentica registros por meio de uma chave secreta; não é uma assinatura verificável com chave pública. [Biblioteca HMAC do Python](https://docs.python.org/3/library/hmac.html).

Além da cadeia, manter testemunhos independentes do MySQL contendo lote, sequência, quantidade e assinatura final. Um diário persistente fora do banco, escrito por acréscimo e com acesso restrito, é suficiente para o modelo de ameaça de alguém adulterando apenas o MySQL. Isso permite detectar também truncamento do final do histórico ou restauração de registros antigos.

Banco e diário são dois recursos distintos: não fingir que uma transação SQL cobre ambos. Antes de confirmar sucesso de um lance, seu testemunho precisa estar persistido. Prever estados pendentes e reconciliação por identificador da operação para falhas entre as escritas; bloquear novas alterações de um lote com divergência até reconciliar. Testar reinício em cada ponto crítico. A implementação exata desse protocolo será trabalhada e explicada na etapa de auditoria.

A página pública recalcula o histórico inteiro e compara com o testemunho independente, mostrando íntegro, adulterado ou verificação temporariamente indisponível. Nunca informar íntegro se não foi possível verificar. Testar mudança de valor/autor/horário, inserção, exclusão no meio, exclusão no fim, remoção de todos os lances, reordenação e recálculo de hashes comuns.

Limite documentado: esse mecanismo detecta adulteração do banco; não garante proteção se um invasor controlar também a aplicação, as chaves e o armazenamento independente. Não há necessidade de blockchain.

Usar apelidos aleatórios por participante e por lote em histórico e comprovante. Não publicar nome completo, e-mail, dados da carteira, tokens ou identificadores internos correlacionáveis. O comprovante é uma página pública com identificador aleatório e link copiável; um PDF para download não é exigido.

**10. Modelo de dados mínimo**

| Entidade | Dados essenciais |
|---|---|
| Usuário | Autenticação Django, papel e dados privados |
| Carteira | Usuário, saldo total e controle transacional |
| Movimentação | Carteira, tipo, valor, operação idempotente, lote quando aplicável e data |
| Produto importado | Provedor, ID externo, atributos e imagem local |
| Lote | Dono, cópia imutável do produto, valores, início, fim original/efetivo, estado, liderança e processamento |
| Participante do lote | Usuário, lote e pseudônimo público aleatório |
| Lance | Lote, participante, valor, sequência, horário e elementos de integridade |
| Reserva | Carteira, lote, valor e situação; no máximo uma reserva ativa por lote |
| Liquidação | Lote único, comprador, vendedor, valor e operação única |
| Comprovante | Liquidação única, identificador público aleatório e dados imutáveis da venda |
| Operação de auditoria | Identificador, sequência e estado necessário para reconciliação com o diário independente |

Criar índices para estado/horários/dono dos lotes e lote/sequência dos lances. Usar unicidade para sequência por lote, liquidação por lote, comprovante por liquidação e operações idempotentes. Os históricos financeiros e de lances não devem sumir por exclusão em cascata de uma conta.

**11. Contrato inicial da API**

| Grupo | Endpoints propostos |
|---|---|
| Sessão | `GET /api/auth/csrf/`, `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/` |
| Catálogo do leiloeiro | `GET /api/catalog/products/`, `GET /api/catalog/products/{id}/`, `GET /api/catalog/categories/` |
| Lotes | `GET /api/lots/`, `GET /api/lots/{id}/`, `POST /api/lots/` |
| Sala | `GET /api/lots/{id}/room/`, `POST /api/lots/{id}/bids/` |
| Cancelamento | `POST /api/lots/{id}/cancel/` |
| Carteira | `GET /api/wallet/`, `GET /api/wallet/transactions/`, `POST /api/wallet/deposits/` |
| Painéis | `GET /api/me/lots/`, `GET /api/me/participations/`, `GET /api/me/awards/`, `GET /api/me/sales-summary/` |
| Consulta pública | `GET /api/lots/{id}/audit/`, `GET /api/receipts/{public_id}/` |
| Operação | `GET /api/health/` |

Busca de lotes usa dados locais: título/descrição, categoria, estado e faixa de valor, com ordenação e paginação. Definir que faixa de valor considera o lance atual ou o inicial quando não houver lances. Cancelados continuam excluídos da vitrine mesmo com filtros.

Erros retornam código estável, mensagem compreensível e campos relevantes, como o mínimo atualizado. A resposta da sala é consistente e inclui estado, horário do servidor, fim efetivo, histórico e informações privadas apenas para o usuário autenticado. A auditoria verifica o histórico completo, mesmo quando sua apresentação é paginada.

**12. Configuração do MySQL e credenciais**

O caminho principal será MySQL em Docker desde o início, evitando diferenças entre o MySQL do Windows e o banco do deploy. O Django acessa o serviço `db` na porta interna `3306`. Quando ferramentas no computador precisarem se conectar, uma porta de desenvolvimento pode ser publicada somente em `127.0.0.1`; nesse caso o host usado por essas ferramentas é `127.0.0.1`, não `db`.

Preparar um `.env.example` com nomes e valores fictícios. Cada desenvolvedor copia para `.env` e gera localmente os segredos. Exemplo de contrato, ainda sem efeito até criarmos o Compose:

```dotenv
MYSQL_DATABASE=leilao_digital
MYSQL_USER=leilao_app
MYSQL_PASSWORD=GERAR_LOCALMENTE
MYSQL_ROOT_PASSWORD=GERAR_OUTRA_SENHA_LOCALMENTE
DB_HOST=db
DB_PORT=3306
DJANGO_SECRET_KEY=GERAR_LOCALMENTE
AUDIT_HMAC_KEY=GERAR_UMA_CHAVE_INDEPENDENTE
DJANGO_DEBUG=True
```

O Compose mapeará explicitamente essas variáveis para cada serviço: Django recebe apenas as que precisa e usa `MYSQL_DATABASE`, `MYSQL_USER` e `MYSQL_PASSWORD` para configurar `DATABASES`. O frontend não recebe credenciais do MySQL nem chaves de auditoria. O `.env` usado para interpolar o Compose não injeta automaticamente todas as variáveis em todos os containers. [Variáveis do Compose](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).

O serviço do banco cria o banco e um usuário de aplicação separado do root durante a inicialização. Em produção, limitar esse usuário ao banco da aplicação e separar permissões de migração das permissões de execução quando configurarmos a infraestrutura. Usar `django.db.backends.mysql` e o driver `mysqlclient`. Configurar `utf8mb4`, InnoDB e modo estrito para transações e armazenamento correto. [Django com MySQL](https://docs.djangoproject.com/en/5.2/ref/databases/#mysql-notes).

O fluxo documentado será: configurar ambiente, subir banco, aguardar healthcheck, aplicar migrations e executar seed. `depends_on` sozinho não significa banco pronto; usar a condição de saúde e tratamento de conexão. [Inicialização no Compose](https://docs.docker.com/compose/how-tos/startup-order/).

Cuidados que fazem parte da implementação:

- Ignorar `.env`, volumes, dumps e arquivos locais de segredos no Git e no contexto de build das imagens; versionar somente exemplos e migrations.
- Não colocar senhas em comandos, logs, screenshots, README ou mensagens; não solicitar que sejam enviadas pelo chat.
- Nunca usar prefixo `NEXT_PUBLIC_` em segredos: esse prefixo expõe o valor ao código enviado ao navegador. [Variáveis do Next.js](https://nextjs.org/docs/app/guides/environment-variables).
- Usar credenciais distintas para desenvolvimento, testes e produção; contas demonstrativas não são contas de infraestrutura.
- Proteger e manter estáveis as chaves de auditoria; backups e rotação precisam preservar a verificação dos registros antigos.
- Manter volumes persistentes e documentar backup/restauração. As variáveis de inicialização do banco não trocam automaticamente senhas de um volume já existente; alterações exigem procedimento explícito, sem apagar dados. [MySQL em Docker](https://dev.mysql.com/doc/refman/8.4/en/docker-mysql-more-topics.html).
- Criar banco de testes separado com permissão apropriada; nunca executar testes destrutivos no banco de produção.

**13. Testes e critérios de conclusão**

Automatizar regras no backend com testes do Django/DRF, usando MySQL também para concorrência. Usar testes de navegador, por exemplo Playwright, para os fluxos principais.

| Área | Casos indispensáveis |
|---|---|
| Permissões | Leiloeiro não dá lance, licitante não cria lote e terceiros não cancelam lotes alheios |
| Valores | Primeiro lance e incremento nos limites, saldo insuficiente e rejeição do líder atual |
| Tempo | Antes do início, no início, no término, anti-sniping dentro/fora da janela e prorrogações sucessivas |
| Carteira | Reserva, liberação, vários lotes simultâneos, depósitos repetidos e ausência de saldo negativo |
| Concorrência | Lances no mesmo lote, mesma carteira em lotes diferentes e lance concorrendo com cancelamento/encerramento |
| Liquidação | Débito e crédito corretos, lote sem vencedor, execução repetida e reinício do processo |
| Cancelamento | Sem lances, com lances, estorno único, remoção da vitrine e rejeição após encerramento |
| API externa | Timeout, resposta inválida, produto inexistente e funcionalidades locais com DummyJSON indisponível |
| Auditoria | Histórico íntegro e todas as adulterações descritas, inclusive truncamento e falhas entre diário e banco |
| Privacidade | Respostas públicas sem dados pessoais ou valores de carteira |
| Interface | Dois participantes em contextos distintos, mensagens de liderança, comprovante compartilhável e persistência do tema |
| Execução | Instalação limpa, migrations, seed repetível, build e fluxo público no ambiente publicado |

Concluir uma funcionalidade significa: regra implementada no backend, interface correspondente funcional, testes relevantes aprovados, README atualizado quando necessário e commit coeso pronto para revisão. Testes de bloqueio exigem transações reais e conexões independentes; um teste sequencial com SQLite não comprova segurança em concorrência.

**14. Versionamento e execução em sete dias**

Usar `main` estável e branches curtas por funcionalidade, com pull requests mesmo trabalhando sozinho. Commits pequenos e completos: `feat`, `fix`, `test`, `docs` e `chore`. Testes relevantes acompanham a funcionalidade; a etapa de testes ao final amplia os fluxos de integração.

| Ordem | Entrega revisável | Commit sugerido |
|---|---|---|
| 0 | Escopo e decisões documentados | `docs(scope): define requisitos e plano de entrega` |
| 1 | Estrutura, Git, exemplos de ambiente e Compose com MySQL | `chore(setup): configura monorepo e ambiente docker` |
| 2 | Usuários, papéis, sessão e seed inicial | `feat(auth): adiciona autenticacao e permissoes` |
| 3 | Catálogo DummyJSON, cópias locais e criação de lotes | `feat(lots): integra catalogo e publicacao de lotes` |
| 4 | Carteira, depósitos e reservas | `feat(wallet): implementa saldo e reservas` |
| 5 | Lances transacionais e prorrogação | `feat(bids): implementa disputa e anti-sniping` |
| 6 | Encerramento, liquidação e comprovantes | `feat(settlement): liquida lotes e gera comprovantes` |
| 7 | Cancelamento com liberação automática | `feat(lots): adiciona cancelamento e estorno` |
| 8 | Auditoria e testes de adulteração/recuperação | `feat(audit): verifica integridade do historico` |
| 9 | Vitrine, sala, carteira e painéis integrados | `feat(web): integra telas aos fluxos do leilao` |
| 10 | Busca e filtros locais | `feat(search): adiciona busca e filtros de lotes` |
| 11 | Temas e acabamento responsivo | `feat(theme): adiciona temas claro e escuro` |
| 12 | Fluxos de navegador e CI | `test(e2e): valida fluxos completos de disputa` |
| 13 | Publicação, seed demonstrativo e documentação final | `chore(deploy): publica aplicacao e documenta operacao` |

Essa tabela indica marcos, não proíbe commits intermediários quando houver unidades menores completas. A cada entrega, a orientação deve explicar o que mudou, por quê, como validar e quais arquivos selecionar. Antes do commit, revisar o diff e conferir que não há credenciais. Não criar commits artificiais de funcionalidades ainda não concluídas.

Distribuição sugerida: dia 1 ambiente, MySQL, autenticação e primeira publicação básica; dia 2 catálogo e lotes; dia 3 carteira e lances; dia 4 encerramento, comprovantes e cancelamento; dia 5 auditoria e integração das telas; dia 6 filtros, temas e testes completos; dia 7 validação no deploy, README e entrega. Trabalhar a interface mínima junto de cada fluxo. Reservar atenção especial à auditoria e à concorrência desde o início.

**15. Deploy, demonstração e envio**

Proposta inicial: servidor Linux com Docker Compose, um domínio HTTPS e processos contínuos para API e encerramento. A máquina precisa manter os volumes de MySQL, mídia e testemunhos de auditoria. Seleção de provedor e custos será feita na etapa de infraestrutura; este escopo não pressupõe contratação.

Publicar uma versão mínima cedo para validar rede, HTTPS e execução dos containers. No deploy final: build de produção do Next.js, servidor WSGI como Gunicorn para Django, `DEBUG=False`, hosts permitidos e origens CSRF corretos, cookies seguros, banco fora da rede pública, migrations executadas uma vez e logs sem segredos. Aplicar o checklist oficial do Django. [Checklist de deploy](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).

Manter comando de seed idempotente com um leiloeiro, dois licitantes e pelo menos um lote ao vivo apto a receber lances. Recomenda-se também exemplo agendado e encerrado, sem substituir o lote aberto exigido. Como o horário expira, o procedimento demonstrativo deve permitir preparar uma nova sessão de avaliação sem apagar o histórico existente. Contas demo usam exclusivamente dados e saldo fictícios, sem privilégios administrativos.

README final deve conter: objetivo; stack; requisitos; comandos para instalação e execução; configuração do MySQL e variáveis; migrations; seed; contas demo; testes; arquitetura; regras financeiras; interpretação da prorrogação e do cancelamento; técnica e limites da auditoria; comportamento em falhas; deploy; limitações conhecidas e explicação do uso de IA.

Critério final: clonar o repositório e executar seguindo o README; abrir o endereço público; entrar como os três perfis demonstrativos; disputar um lote entre dois clientes; observar reserva e liberação; encerrar e conferir transferência/comprovante; cancelar outro lote; verificar auditoria; alternar tema; repetir as consultas locais com a API externa indisponível.

Segundo a página 7 do PDF, o envio exige nome/e-mail, link do repositório público, link público obrigatório do deploy e relato de onde e como foi usada IA, incluindo revisões e ajustes feitos pelo candidato. O formulário indicado no PDF é `https://elitedev.verzel.com.br/?elite-dev-2026-2`; confirmar sua disponibilidade na ocasião do envio. Não houve envio nem publicação nesta etapa.

**Forma de acompanhamento**

Cada etapa será conduzida em unidades pequenas: explicar o objetivo e o conceito, orientar a implementação mínima, validar o comportamento com exemplos e testes e sinalizar o momento de versionar. O candidato deve conseguir explicar as decisões, especialmente reserva de saldo, bloqueios, liquidação idempotente e auditoria. O próximo passo prático é preparar a estrutura do repositório e subir o MySQL com credenciais locais protegidas.
