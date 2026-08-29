from pathlib import Path
import pandas as pd
from src.validacao import validar_tabela_longa

pasta_projeto = Path(__file__).resolve().parent.parent
pasta_provas = pasta_projeto / "dados" / "provas"


def ler_provas():
    arquivos = sorted(pasta_provas.glob("provas_*.xlsx"))
    tabelas = []

    for arquivo in arquivos:
        tabela = pd.read_excel(arquivo, sheet_name="Notas das Provas")
        tabelas.append(tabela)

    if not tabelas:
        raise FileNotFoundError("Nenhum arquivo de provas foi encontrado.")

    return pd.concat(tabelas, ignore_index=True)


def transformar_provas_para_longo(tabela):
    tabela_longa = tabela.melt(
        id_vars=["turma", "aluno"],
        var_name="disciplina",
        value_name="nota_prova",
    )

    return validar_tabela_longa(
        tabela_longa,
        fonte="provas",
        nota_col="nota_prova",
        minimo=0,
        maximo=10,
    )


if __name__ == "__main__":
    provas = ler_provas()
    provas_longas = transformar_provas_para_longo(provas)
    print(provas_longas.head())