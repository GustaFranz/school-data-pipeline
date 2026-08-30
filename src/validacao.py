import pandas as pd

# Colunas que, juntas, identificam um registro.
# Neste projeto, turma + aluno + disciplina formam uma chave composta.

CHAVES = ["turma", "aluno", "disciplina"]

def validar_tabela_longa(df, fonte, nota_col, minimo, maximo):
    """
    Valida um DataFrame de notas no formato longo.
    A função verifica se os dados respeitam o contrato mínimo esperado
    antes de serem usados em merges, cálculos, dashboards ou relatórios.
    Validações realizadas:
        1. Existência das colunas obrigatórias.
        2. Ausência de valores nulos nas colunas-chave.
        3. Ausência de chaves duplicadas.
        4. Conversão das notas para valores numéricos.
        5. Verificação da faixa mínima e máxima das notas.
    """

    obrigatorias = set(CHAVES + [nota_col])
    ausentes = obrigatorias - set(df.columns)

    # Um set vazio é considerado False.
    # Se houver qualquer coluna dentro de "ausentes", significa que alguma 
    # coluna obrigatória está faltando.
    if ausentes:
        raise ValueError(
            f"{fonte}: colunas ausentes: {sorted(ausentes)}"
        )

    # isna() verifica cada célula e produz True ou False.
    # O segundo any() pergunta:
    # "Existe pelo menos um True nesse resultado?"
    #
    # Portanto:
    # isna()       -> verifica cada célula
    # 1º any()     -> resume por coluna
    # 2º any()     -> produz um único True ou False
    if df[CHAVES].isna().any().any():
        raise ValueError(
            f"{fonte}: existem chaves nulas"
        )

    # duplicated() detecta duplicidades e devolve uma Series booleana. 
    # Ele NÃO remove nenhuma linha.
    # subset=CHAVES informa que somente estas colunas devem ser usadas para 
    # decidir se existe duplicidade: turma + aluno + disciplina
    # As linhas completas são diferentes por causa da nota, mas a chave é a mesma.
    # keep=False marca TODAS as linhas envolvidas na duplicidade.
    duplicadas = df.duplicated(
        subset=CHAVES,
        keep=False,
    )

    # duplicated() já devolve uma Series de True/False, por isso um único any() é suficiente.
    if duplicadas.any():
        # O loc seleciona apenas as linhas marcadas como True
        # e apenas as colunas turma, aluno e disciplina.
        # "records" significa que cada linha vira um registro.
        # Sem "records", o to_dict() tende a organizar os dados
        # principalmente por colunas.
        amostra = (
            df.loc[duplicadas, CHAVES]
            .head(5)
            .to_dict("records")
        )

        raise ValueError(
            f"{fonte}: chaves duplicadas: {amostra}"
        )

    # df[nota_col] seleciona a coluna cujo nome está armazenado
    # em nota_col. então: df[nota_col] == df["nota_simulado"]
    #pd.to_numeric() tenta transformar os valores em números.
    # errors="coerce" faz valores impossíveis de converter virarem NaN.
    # O NaN será detectado logo na validação seguinte.
    notas = pd.to_numeric(
        df[nota_col],
        errors="coerce",
    )

    # Uma nota será inválida se for NaN ou se estiver fora da faixa permitida.
    #notas.isna()
    # -> True para valores ausentes ou que não puderam ser convertidos em núm.
    # notas.between(minimo, maximo)
    # -> True quando o valor está dentro da faixa.
    # O ~ inverte True e False. Portanto: 
    # ~notas.between(...) significa:
    # "nota NÃO está entre mínimo e máximo".
    invalidas = (notas.isna() | ~notas.between(minimo, maximo))
    # Se existir pelo menos uma nota inválida,
    # interrompemos o processamento.
    if invalidas.any():
    # True  = 1 / False = 0
    #Portanto, sum() conta quantos True existem.
        quantidade_invalidas = int(invalidas.sum())

        raise ValueError(
            f"{fonte}: notas inválidas em "
            f"{quantidade_invalidas} linhas"
        )

    # =====> Se o código chegou até aqui:
    # - todas as colunas obrigatórias existem;
    # - as chaves não têm valores nulos;
    # - não existem chaves duplicadas;
    # - todas as notas são numéricas;
    # - todas estão dentro da faixa permitida.
    #   astype(float) converte as notas para float.
    #
    # assign() devolve o DataFrame com a coluna de nota
    # criada ou substituída.
    # O ** desempacota o dicionário e permite usar
    # o nome armazenado em nota_col como nome da coluna.
    return df.assign( **{nota_col: notas.astype(float)})
