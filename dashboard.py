from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.boletins import selecionar_boletim

PASTA_PROJETO = Path(__file__).resolve().parent
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
    """Carrega o arquivo consolidado de notas e mantém o resultado em cache."""
    return pd.read_csv(
        CAMINHO_NOTAS,
        encoding="utf-8-sig",
    )


st.set_page_config(
    page_title="School Data Pipeline",
    layout="wide")

st.title("School Data Pipeline")
st.subheader("Colegio Caminhos do Futuro")
st.caption("Dados ficticios")


notas = carregar_notas()

turmas = sorted(notas["turma"].dropna().unique())
turma = st.selectbox("Turma",
                     options=turmas,
                     key="boletim_turma")

dados = notas.loc[notas["turma"] == turma]

alunos = sorted(dados["aluno"].dropna().unique())

aluno = st.selectbox("Aluno",
                     options=alunos,
                     key="boletim_aluno")

media_geral = dados["media"].mean()
total_alunos = dados["aluno"].nunique()
percentual_recuperacao = dados["situacao"].eq("Recuperacao").mean() * 100
percentual_acima = (dados["media"] >= 6).mean() * 100
percentual_abaixo = (dados["media"] < 6).mean() * 100

media_disciplina = (
    dados.groupby("disciplina", as_index=False)[["media"]]
    .mean()
    .sort_values("media", ascending=False)
)
melhor = media_disciplina.iloc[0]
pior = media_disciplina.iloc[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Media geral", f"{media_geral:.1f}")
col2.metric("Total de alunos", total_alunos)
col3.metric("% em recuperacao", f"{percentual_recuperacao:.1f}%")

col4, col5 = st.columns(2)
col4.metric("% acima da media", f"{percentual_acima:.1f}%")
col5.metric("% abaixo da media", f"{percentual_abaixo:.1f}%")

st.caption(
    f"Melhor disciplina: {melhor['disciplina']} ({melhor['media']:.1f}) · "
    f"Pior disciplina: {pior['disciplina']} ({pior['media']:.1f})"
)

fig = px.bar(
    media_disciplina,
    x="disciplina",
    y="media",
    title="Media por disciplina",
    text_auto=".1f"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Alunos em recuperacao")
recuperacao = dados[dados["situacao"] == "Recuperacao"]
st.dataframe(recuperacao[["aluno", "disciplina", "media"]],
             use_container_width=True)
