from pathlib import Path
import pandas as pd

pasta_projeto = Path(__file__).resolve().parent.parent
pasta_provas = pasta_projeto / "dados" / "provas"


def ler_provas():
    arquivos = list(pasta_provas.glob("provas_*.xlsx"))
    tabelas = []

    for arquivo in arquivos:
        tabela = pd.read_excel(arquivo, sheet_name="Notas das Provas")
        tabelas.append(tabela)

    if not tabelas:
        raise FileNotFoundError("Nenhum arquivo de provas foi encontrado.")

    return pd.concat(tabelas, ignore_index=True)


def transformar_provas_para_longo(tabela):
    return tabela.melt(
        id_vars=["turma", "aluno"],
        var_name="disciplina",
        value_name="nota_prova",
    )


if __name__ == "__main__":
    provas = ler_provas()
    provas_longas = transformar_provas_para_longo(provas)
    print(provas_longas.head())