# Contrato de Dados

Este documento descreve as regras esperadas para os dados utilizados no projeto `school-data-pipeline`.

As regras descritas aqui correspondem às validações implementadas no módulo `src/validacao.py`.

O objetivo é garantir que os dados provenientes de simulados, provas e projetos pedagógicos apresentem uma estrutura consistente antes das etapas de consolidação, cálculo de médias e geração de relatórios.

## 1. Estrutura após transformação para formato longo

Após a aplicação de `melt()`, cada fonte deve produzir uma tabela no formato longo.
Toda tabela deve conter obrigatoriamente as seguintes colunas:

* `turma`
* `aluno`
* `disciplina`
* uma coluna de nota correspondente à fonte

A coluna de nota varia de acordo com a origem:

| Fonte     | Coluna de nota  |
| --------- | --------------- |
| Simulados | `nota_simulado` |
| Provas    | `nota_prova`    |
| Projetos  | `nota_projeto`  |


## 2. Granularidade dos dados

Após o `melt()`, cada linha representa:
**1 aluno + 1 disciplina + 1 nota dentro de uma determinada fonte.**

Exemplo:

```text
turma | aluno | disciplina | nota_simulado
6A    | Ana   | Matemática | 8.5
6A    | Ana   | Ciências   | 7.0
```

Isso significa que Ana possui um registro para Matemática e outro registro para Ciências.


## 3. Chave lógica

A identificação de cada registro é feita pela combinação das colunas:

```text
turma + aluno + disciplina
```

Essas três colunas formam a chave lógica utilizada pelo projeto.

Exemplo:

```text
6A + Ana + Matemática
```

Essa combinação deve identificar apenas um registro dentro de cada fonte.


## 4. Política de duplicidade

A combinação:

```text
turma + aluno + disciplina
```

não pode aparecer mais de uma vez na mesma fonte.

Exemplo inválido:

```text
turma | aluno | disciplina | nota_simulado
6A    | Ana   | Matemática | 8.0
6A    | Ana   | Matemática | 9.0
```

Embora as notas sejam diferentes, os dois registros possuem a mesma chave lógica.

Nesse caso, a validação deve interromper o fluxo.


## 5. Política de valores nulos

As colunas que fazem parte da chave lógica não podem possuir valores nulos:

* `turma`
* `aluno`
* `disciplina`

Exemplo inválido:

```text
turma | aluno | disciplina | nota_prova
6A    | Ana   | NaN        | 8.0
```

Nesse caso, o registro não possui uma identidade completa e deve ser rejeitado.


## 6. Regras das notas

As notas devem ser convertíveis para valores numéricos.

Valores textuais que não representam números são considerados inválidos.

Exemplos:

```text
8
7.5
"9"
```

podem ser convertidos para valores numéricos.
Por outro lado:

```text
"oito"
"ausente"
"erro"
```

não representam notas válidas.
A função de validação utiliza `pd.to_numeric(..., errors="coerce")`. Valores não convertíveis tornam-se `NaN` e são posteriormente identificados como inválidos.


## 7. Faixa válida das notas

Cada fonte possui sua própria faixa permitida.

| Fonte     | Coluna          | Mínimo | Máximo |
| --------- | --------------- | -----: | -----: |
| Simulados | `nota_simulado` |      0 |     10 |
| Provas    | `nota_prova`    |      0 |     10 |
| Projetos  | `nota_projeto`  |      0 |      5 |

Os limites são inclusivos.
Portanto:

```text
Simulados e provas:
0 <= nota <= 10

Projetos:
0 <= nota <= 5
```

Exemplo inválido para simulados:

```text
nota_simulado = 11
```

Exemplo inválido para projetos:

```text
nota_projeto = 7
```


## 8. Contrato dos simulados

### Arquivos de entrada

```text
simulado_*.csv
```

### Após o `melt()`

Colunas obrigatórias:

```text
turma
aluno
disciplina
nota_simulado
```

### Regras

* `turma`, `aluno` e `disciplina` não podem ser nulos;
* `turma + aluno + disciplina` deve ser uma combinação única;
* `nota_simulado` deve ser numérica;
* `nota_simulado` deve estar entre 0 e 10;
* após validação, a nota é padronizada como `float`.


## 9. Contrato das provas

### Arquivos de entrada

```text
provas_*.xlsx
```

### Aba utilizada

```text
Notas das Provas
```

### Após o `melt()`

Colunas obrigatórias:

```text
turma
aluno
disciplina
nota_prova
```

### Regras

* `turma`, `aluno` e `disciplina` não podem ser nulos;
* `turma + aluno + disciplina` deve ser uma combinação única;
* `nota_prova` deve ser numérica;
* `nota_prova` deve estar entre 0 e 10;
* após validação, a nota é padronizada como `float`.

---

## 10. Contrato dos projetos

### Arquivos de entrada

```text
projeto_*.pdf
```

Após a extração do PDF, as colunas:

```text
Turma
Aluno
```

são padronizadas para:

```text
turma
aluno
```

### Após o `melt()`

Colunas obrigatórias:

```text
turma
aluno
disciplina
nota_projeto
```

### Regras

* `turma`, `aluno` e `disciplina` não podem ser nulos;
* `turma + aluno + disciplina` deve ser uma combinação única;
* `nota_projeto` deve ser numérica;
* `nota_projeto` deve estar entre 0 e 5;
* após validação, a nota é padronizada como `float`.



## 11. Exemplos de violações do contrato

### Coluna obrigatória ausente

Exemplo:

```text
turma | aluno | nota_simulado
```

A coluna `disciplina` está ausente.

Resultado esperado:

```text
ValueError
```


### Chave nula

Exemplo:

```text
turma | aluno | disciplina | nota_simulado
6A    | NaN   | Matemática | 8.0
```

Resultado esperado:

```text
ValueError
```



### Chave duplicada

Exemplo:

```text
6A | Ana | Matemática | 8.0
6A | Ana | Matemática | 9.0
```

Resultado esperado:

```text
ValueError
```


### Nota não numérica

Exemplo:

```text
nota_simulado = "oito"
```

O valor não pode ser convertido para número.

Resultado esperado:

```text
ValueError
```


### Nota fora da faixa

Exemplo:

```text
nota_simulado = 12
```

A nota é numérica, porém está fora da faixa válida de 0 a 10.

Resultado esperado:

```text
ValueError
```


## 12. Fluxo esperado

```text
arquivo de origem
↓
leitura
↓
concatenação
↓
melt()
↓
formato longo
↓
validar_tabela_longa()
↓
verificação das colunas
↓
verificação de chaves nulas
↓
verificação de duplicidade
↓
conversão das notas
↓
verificação da faixa
↓
padronização das notas como float
↓
DataFrame validado
↓
restante do pipeline
```


## 13. Manutenção deste contrato

Este documento deve acompanhar o comportamento real do código.

Sempre que alguma regra de validação for alterada em `src/validacao.py`, este contrato também deve ser revisado.

Código, testes e documentação devem representar as mesmas regras de dados.


## 14. Responsabilidade sobre o contrato de dados

O contrato de dados deve ser tratado como parte ativa do projeto, e não apenas como documentação inicial.
Sempre que houver alteração em alguma regra de entrada, transformação ou validação, deve ser verificado se este documento também precisa ser atualizado.

Exemplos de mudanças que exigem revisão do contrato:

* alteração no nome de uma coluna;
* inclusão de uma nova coluna obrigatória;
* mudança na faixa válida das notas;
* alteração da chave lógica;
* mudança na política de valores nulos;
* alteração na regra de duplicidade;
* inclusão de uma nova fonte de dados;
* mudança no formato dos arquivos de entrada.

A recomendação é manter sempre coerentes três partes do projeto:

```text
código
↓
testes
↓
documentação
```

Se o código mudar e o contrato não for atualizado, a documentação passa a representar um comportamento que já não corresponde ao sistema real.
Por isso, o `contrato_de_dados.md` deve ser revisado sempre que houver mudanças relevantes em `validacao.py` ou nos módulos responsáveis pela leitura e transformação dos dados.
