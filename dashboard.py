from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.boletins import selecionar_boletim


PASTA_PROJETO = Path(__file__).resolve().parent

# Arquivo consolidado produzido anteriormente pelo pipeline.
CAMINHO_NOTAS = (
    PASTA_PROJETO / "saidas" / "relatorios" / "notas_consolidadas.csv"
)


# O pipeline prepara, valida e consolida os dados; o dashboard apenas consome
# o resultado já pronto para exibir filtros, métricas, gráficos e tabelas.
# Essa separação reduz acoplamento entre processamento e interface. Também
# evita reprocessar todas as fontes sempre que o Streamlit fizer um rerun.
# Além disso, facilita testes, manutenção e futuras mudanças na origem dos
# dados. Como o Streamlit roda separadamente, ele não compartilha variáveis
# do main.py.


@st.cache_data
def carregar_notas():
    """
    Carrega o arquivo CSV com as notas já consolidadas pelo pipeline.
    O resultado é armazenado em cache pelo Streamlit para evitar que o mesmo
    arquivo seja lido novamente a cada rerun provocado por interações do usuário.
    Returns:
        pd.DataFrame: DataFrame contendo as notas consolidadas.
    """
    return pd.read_csv(
        CAMINHO_NOTAS,
        encoding="utf-8-sig",
    )


# Configurações gerais da página.
st.set_page_config(
    page_title="School Data Pipeline",
    layout="wide"
)

st.title("School Data Pipeline")
st.subheader("Colegio Caminhos do Futuro")
st.caption("Dados ficticios")


# Carrega o DataFrame consolidado.
notas = carregar_notas()


# Obtém as turmas disponíveis no conjunto de dados.
turmas = sorted(
    notas["turma"].dropna().unique()
)

# Widget para selecionar a turma.
turma = st.selectbox(
    "Turma",
    options=turmas,
    key="boletim_turma",
    index=None,
    placeholder="Selecione uma turma"
)

if turma is None:
    st.stop()

# Mantém apenas as linhas da turma selecionada.
dados = notas.loc[
    notas["turma"] == turma
]


# Gera a lista de alunos apenas da turma escolhida.
alunos = sorted(
    dados["aluno"].dropna().unique()
)

# Widget dependente da turma selecionada.
aluno = st.selectbox(
    "Aluno",
    options=alunos,
    key="boletim_aluno",
    index=None,
    placeholder="Selecionar aluno"
)

if turma is None:
    st.stop()

# Seleciona somente as notas do aluno escolhido.
try:
    tabela_aluno = selecionar_boletim(
        notas,
        turma,
        aluno,
    )

except ValueError as erro:
    # Exibe uma mensagem amigável caso nenhum boletim seja encontrado.
    st.warning(str(erro))
    st.stop()


# Exibe o boletim individual.
st.subheader(f"Boletim — {aluno}")
st.caption(turma)

st.dataframe(
    tabela_aluno,
    hide_index=True,
    width=1400,
    column_config={
        "disciplina": st.column_config.TextColumn(
            "Disciplina", width="medium"),
        "nota_simulado": st.column_config.NumberColumn(
            "Simulado", width="medium", format="%.1f"),
        "nota_prova": st.column_config.NumberColumn(
            "Prova", width="medium", format="%.1f"),
        "nota_projeto": st.column_config.NumberColumn(
            "Projeto", width="medium", format="%.1f"),
        "media": st.column_config.NumberColumn(
            "Média", width="medium", format="%.1f"),
        "situacao": st.column_config.TextColumn(
            "Situação", width="medium"),
    }
)


# Indicadores gerais da turma selecionada.
media_geral = dados["media"].mean()
total_alunos = dados["aluno"].nunique()

percentual_recuperacao = (
    dados["situacao"].eq("Recuperacao").mean() * 100
)

percentual_acima = (
    (dados["media"] >= 6).mean() * 100
)

percentual_abaixo = (
    (dados["media"] < 6).mean() * 100
)


# Calcula a média de cada disciplina da turma.
media_disciplina = (
    dados.groupby(
        "disciplina",
        as_index=False
    )[["media"]]
    .mean()
    .sort_values(
        "media",
        ascending=False
    )
)


# Como a tabela está ordenada, a primeira linha é a melhor e a última a pior.
melhor = media_disciplina.iloc[0]
pior = media_disciplina.iloc[-1]


# KPIs principais.
col1, col2, col3 = st.columns(3)

col1.metric(
    "Media geral",
    f"{media_geral:.1f}"
)

col2.metric(
    "Total de alunos",
    total_alunos
)

col3.metric(
    "% em recuperacao",
    f"{percentual_recuperacao:.1f}%"
)


# KPIs complementares.
col4, col5 = st.columns(2)

col4.metric(
    "% acima da media",
    f"{percentual_acima:.1f}%"
)

col5.metric(
    "% abaixo da media",
    f"{percentual_abaixo:.1f}%"
)


# Destaca a melhor e a pior disciplina da turma.
st.caption(
    f"Melhor disciplina: {melhor['disciplina']} ({melhor['media']:.1f}) · "
    f"Pior disciplina: {pior['disciplina']} ({pior['media']:.1f})"
)


# Gráfico com a média da turma por disciplina.
fig = px.bar(
    media_disciplina,
    x="disciplina",
    y="media",
    title="Media por disciplina",
    text_auto=".1f"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# Filtra e exibe apenas os registros em recuperação.
st.subheader("Alunos em recuperacao")

recuperacao = dados[
    dados["situacao"] == "Recuperacao"
]

st.dataframe(
    recuperacao[
        ["aluno", "disciplina", "media"]
    ],
    use_container_width=True
)