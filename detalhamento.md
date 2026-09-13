# Detalhamento do projeto — School Data Pipeline

Documento de referência dos módulos deste pipeline de dados escolares. Cada seção descreve um desafio a ser implementado: requisitos, entradas, saídas e critérios de aceite — sem prescrever a solução em código.

**Escola fictícia:** Colégio Caminhos do Futuro  
**Status geral:** v1 concluída — Desafios 1 a 7 implementados; Desafio 8 em backlog

> Pretendo revisitar este projeto muitas vezes. A v1 funciona, mas ainda estou assimilando etapas mais densas (consolidação, boletins e dashboard) e refinando aos poucos.

## Contexto geral

Este projeto simula a rotina de uma coordenação escolar fictícia. Os dados são inventados e não representam alunos ou instituições reais.

**Turmas:**

- 6º ano Matutino — 26 alunos
- 7º ano Matutino — 25 alunos
- 8º ano Matutino — 20 alunos

**Disciplinas:**

1. Língua Portuguesa
2. Matemática
3. Ciências
4. História
5. Geografia
6. Inglês
7. Educação Física
8. Artes
9. Ensino Religioso
10. Redação

**Fontes de notas:**

| Fonte | Formato | Origem fictícia |
|-------|---------|-----------------|
| Simulado | CSV | Portal HTML local |
| Provas | Excel | Professores |
| Projeto pedagógico | PDF | Coordenação |

## Visão do pipeline

Este projeto combina três camadas de um pipeline de dados escolares:

| Camada | Descrição |
|--------|-----------|
| **Interface (RPA)** | PyAutoGUI simula a interação humana no portal local — login, navegação e download dos CSVs de simulado. |
| **Dados** | Leitura e consolidação de CSV, Excel e PDF em uma base única, com cálculo de médias e regras pedagógicas. |
| **Saída** | Base consolidada em CSV e dashboard interativo com indicadores, download individual de boletim em CSV e download em ZIP por turma. |

Cenário inspirado na rotina escolar: várias fontes de nota, portal sem API e tarefas repetitivas que podem ser automatizadas.

### Ambiente calibrado (PyAutoGUI)

| Item | Valor |
|------|-------|
| Resolução do monitor | 1920×1080 |
| Escala do Windows | 125% (1536×864 lógico) |
| Navegador | Google Chrome maximizado |
| Zoom do navegador | 100% |

---

## Desafio 1 — Mapeamento dos dados de entrada

### Contexto

Antes de automatizar qualquer rotina, é preciso entender de onde vêm as notas e como estão organizadas.

### O que o sistema deve fazer

- Identificar as três fontes de dados: simulado, provas e projeto pedagógico.
- Confirmar que existem arquivos para as séries do 6º, 7º e 8º ano.
- Diferenciar claramente dados de entrada dos arquivos que o sistema irá gerar.

### Entradas

- `dados/simulados/`
- `dados/provas/`
- `dados/projetos/`
- `portal_simulado/`

### Saídas esperadas

Nenhum arquivo gerado nesta etapa. O resultado é a compreensão do cenário e dos formatos envolvidos.

### Critérios de aceite

- [x] Consigo explicar a origem e o formato de cada tipo de nota.
- [x] Existem arquivos de entrada para as três séries.

### Status

- [x] Concluído

### Aprendizados

- Mapeei três fontes distintas (portal/CSV, Excel de provas, PDF de projetos) antes de pensar em código de consolidação.
- Entender o cenário fictício da escola facilitou decidir o que automatizar primeiro: o simulado, por ser repetitivo e acessível via portal.

---

## Desafio 2 — Validação do portal fictício

### Contexto

O simulado escolar fica em um portal local. Antes de automatizar, o fluxo manual precisa funcionar.

### O que o sistema deve fazer

- Abrir o portal local a partir dos arquivos do projeto.
- Realizar login com as credenciais de demonstração.
- Acessar o painel e as páginas das três séries.
- Baixar manualmente os CSVs de simulado para validar o fluxo.

### Entradas

- `portal_simulado/login.html`
- Credenciais fictícias descritas no README

### Saídas esperadas

Confirmação de que o portal funciona e CSVs de teste disponíveis.

### Critérios de aceite

- [x] O login funciona com as credenciais de demonstração.
- [x] Consigo acessar o painel e as páginas das três séries.
- [x] Consigo baixar o CSV de simulado de cada série.

### Status

- [x] Concluído

### Aprendizados

- Testar o fluxo manualmente antes do PyAutoGUI evitou automatizar um caminho errado.
- Validar login, painel e download série por série deu segurança para a etapa de RPA.

---

## Desafio 3 — Automação do download do simulado

### Contexto

Baixar os relatórios de simulado manualmente, série por série, não escala. Esta etapa introduz automação de interface (RPA) com PyAutoGUI em um cenário próximo da rotina escolar — simular cliques e digitação no navegador quando o portal não oferece API.

### O que o sistema deve fazer

- Acessar o portal local de forma automatizada com PyAutoGUI.
- Autenticar com as credenciais de demonstração.
- Navegar pelas páginas das três séries e acionar o download dos CSVs.
- Registrar evidência da execução (capturas de tela, log ou equivalente).

### Entradas

- Portal em `portal_simulado/`
- Credenciais fictícias descritas no README

### Saídas esperadas

- CSVs do simulado prontos para uso nas etapas seguintes
- Evidência da execução em pasta de saída (ex.: `saidas/prints/`)

### Critérios de aceite

- [x] Os CSVs das três séries são obtidos sem intervenção manual repetida.
- [x] A automação com PyAutoGUI funciona de forma reproduzível na máquina local.
- [x] Há registro visual ou log da execução.

### Status

- [x] Concluído

### Aprendizados

- Este foi meu **primeiro projeto de automação** em Python. No início o fluxo parecia complexo — portal, login, três séries, downloads — mas, ao repetir funções (`fazer_login`, `painel_simulado_da_turma`, `baixar_csv_turma`, `botao_voltar`), o processo começou a ficar automático na minha cabeça também.
- Mapear coordenadas com pausa no código exigiu paciência, mas foi o passo que mais deixou claro como o PyAutoGUI enxerga a tela.
- Ver o script executar sozinho depois de calibrar tudo trouxe grande satisfação: percebi que consegui chegar a um projeto que, à princípio, parecia difícil, mas foi se tornando compreensível aos poucos.
- Registrei o mapeamento e o fluxo completo em GIFs (`gifs/rpa-mapeamento-coordenadas.gif` e `gifs/rpa-fluxo-completo-portal.gif`) como evidência do processo.

---

## Desafio 4 — Leitura dos arquivos de notas

### Contexto

As notas chegam em formatos diferentes. O sistema precisa transformá-las em uma estrutura única e utilizável.

### O que o sistema deve fazer

- Ler arquivos CSV de simulado.
- Ler planilhas Excel de provas, com um aluno por linha e as disciplinas organizadas em colunas.
- Reconhecer a aba adicional de professores presente nas planilhas de prova.
- Ler PDFs simples de projeto pedagógico.
- Produzir dados estruturados e consultáveis (turma, aluno, disciplina, nota).

### Entradas

- `dados/simulados/`
- `dados/provas/`
- `dados/projetos/`

### Saídas esperadas

Dados carregados e inspecionáveis, prontos para consolidação.

### Critérios de aceite

- [x] CSV, Excel e PDF são lidos com sucesso.
- [x] Consigo visualizar uma amostra dos dados carregados.
- [x] O formato das provas (largo, com disciplinas em colunas) é reconhecido.

### Status

- [x] Concluído

### Aprendizados

- Cada formato exigiu uma abordagem diferente: `read_csv`, `read_excel` e extração de tabela em PDF com PDFPlumber.
- Transformar planilhas largas em formato longo (`melt`) foi o passo que mais exigiu atenção: turma, aluno e disciplina precisam bater entre as três fontes.
- Separei a leitura em três módulos (`leitor_simulados`, `leitor_provas`, `leitor_projetos`) para manter cada responsabilidade isolada.
- Ainda reviso esta etapa para entender melhor como os dados se encaixam antes da consolidação.

---

## Desafio 5 — Consolidação e cálculo de médias

### Contexto

Com todas as notas lidas, o sistema deve reunir simulado, prova e projeto pedagógico e aplicar a regra pedagógica de aprovação.

### O que o sistema deve fazer

- Combinar as notas por turma, aluno e disciplina.
- Aplicar média ponderada considerando pesos distintos para simulado, prova e projeto pedagógico.
- Tratar a escala do projeto pedagógico de forma coerente com as demais avaliações.
- Classificar cada aluno como aprovado ou em recuperação, com base no critério mínimo de 6,0.

### Entradas

Dados estruturados produzidos na etapa anterior.

### Saídas esperadas

Base consolidada com média e situação por aluno e disciplina.

### Critérios de aceite

- [x] Cada aluno possui média calculada nas 10 disciplinas.
- [x] Uma amostra manual confere com o resultado esperado.
- [x] A situação (aprovado ou recuperação) está definida para cada registro.

### Status

- [x] Concluído

### Aprendizados

- O `merge` por turma, aluno e disciplina exige que os nomes e formatos das colunas estejam alinhados entre simulado, prova e projeto.
- A conversão da nota de projeto (× 2) e a média ponderada foram regras que precisei revisar mais de uma vez para não errar o cálculo.
- A saída consolidada em CSV (`saidas/relatorios/notas_consolidadas.csv`) virou a base para boletins e dashboard.
- Enfrentei conflito de imports entre módulos nesta fase; padronizar `from src.*` destravou as etapas seguintes.
- Volto a esta etapa para conferir amostras manualmente e consolidar meu entendimento da regra pedagógica.

---

## Desafio 6 — Disponibilização de boletins

### Contexto

A coordenação precisa consultar o desempenho individual de cada aluno e baixar esse resultado para conferência ou compartilhamento.

### O que o sistema deve fazer

- Exibir o boletim de um aluno selecionado no dashboard.
- Apresentar notas, médias e situação final.
- Permitir o download do boletim individual em CSV.
- Preparar o arquivo para download sem criar arquivos temporários no projeto.

### Entradas

Base consolidada com médias e situação.

### Saídas esperadas

Boletim individual disponível para download em CSV no dashboard. O arquivo é preparado em memória e o navegador define o local onde será salvo.

### Critérios de aceite

- [x] É possível selecionar uma turma e um aluno no dashboard.
- [x] Todas as disciplinas, notas, médias e situações aparecem no boletim.
- [x] É possível baixar o boletim individual em CSV.
- [x] Médias e situação conferem em uma amostra verificada manualmente.

### Status

- [x] Concluído

### Aprendizados

- Passei da geração de arquivos HTML para boletins CSV disponibilizados diretamente no dashboard.
- Cada boletim reúne disciplina, notas, média e situação do aluno selecionado.
- O CSV é criado em memória, sem gravar arquivos temporários no projeto.
- A codificação UTF-8 com BOM facilita a abertura dos arquivos no Excel sem perder acentos.

---

## Desafio 7 — Dashboard escolar

### Contexto

Além dos boletins individuais, a coordenação precisa enxergar o desempenho das turmas de forma agregada.

### O que o sistema deve fazer

- Criar um painel interativo executável localmente.
- Exibir indicadores como:
  - média da turma por disciplina;
  - percentual de alunos acima e abaixo da média;
  - disciplinas com melhor e pior desempenho;
  - alunos em recuperação.
- Permitir o download do boletim CSV de um aluno selecionado.
- Permitir o download, em ZIP, dos boletins de todos os alunos da turma selecionada.

### Entradas

Base consolidada com médias e situação.

### Saídas esperadas

- Dashboard interativo aberto no navegador.
- Download individual de boletim em CSV.
- Download em lote dos boletins da turma em arquivo ZIP.

### Critérios de aceite

- [x] O painel abre localmente sem erro.
- [x] Os indicadores refletem os dados consolidados.
- [x] É possível explorar a visão geral ou filtrar por turma.
- [x] É possível baixar o boletim individual do aluno selecionado em CSV.
- [x] É possível baixar os boletins de toda a turma em arquivo ZIP.

### Status

- [x] Concluído

### Aprendizados

- Esta foi a etapa em que senti mais densidade de conteúdo: além de ler dados, precisei pensar em indicadores, layout e bibliotecas novas (Streamlit e Plotly).
- Houve conflito de imports entre módulos (`from leitor_*` vs `from src.*`), o que atrasou a execução do dashboard até padronizar os caminhos.
- Mantive o painel simples de propósito: métricas, gráfico por disciplina e tabela de recuperação. Filtros avançados e visual mais elaborado ficam para a v2.
- Não encaro esta etapa como “dominada de vez”: volto ao dashboard para entender melhor cada indicador e melhorar o projeto com calma.

---

## Desafio 8 — Evoluções (versão 2)

### Contexto

Lista de melhorias futuras. Nenhuma delas é obrigatória para concluir a primeira versão do projeto.

### Ideias

- Substituir poucas planilhas centrais por mais arquivos, aproximando o fluxo real (ex.: uma planilha por professor e turma).
- Exportar boletins em PDF.
- Adicionar filtros avançados no dashboard.
- Personalizar o visual do painel.
- Incluir testes automatizados.
- Registrar logs de execução da automação.

### Status

- [ ] Backlog

### Aprendizados

_(preencher conforme evoluir o projeto)_
