from pathlib import Path
import re

pasta_projeto = Path(__file__).resolve().parent.parent
pasta_boletins = pasta_projeto / "saidas" / "boletins"


def limpar_nome_arquivo(texto):
    """
    Converte um texto em um nome mais seguro e padronizado para uso em
    arquivos. A função transforma o texto em letras minúsculas, substitui
    caracteres que não sejam letras ou números por "_" e remove "_" extras
    no início ou no final do nome.
    Essa função é usada na geração dos boletins para transformar informações
    como turma e nome do aluno em um nome de arquivo adequado.
    Exemplo:
        "6º ano Matutino - João da Silva"
        pode se tornar:
        "6_ano_matutino_jo_o_da_silva"
    Argumento:
        texto (str): Texto original que será convertido para um formato
        apropriado para compor o nome do arquivo.
    Returns:
        str: Texto limpo e padronizado para uso como nome de arquivo.
    """
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_")


def gerar_boletins(notas):
    """
    Gera os boletins individuais dos alunos usando as notas consolidadas.
    O DataFrame recebido deve conter os dados necessários para identificar
    cada aluno, sua turma, disciplinas, médias e situação final.
    A função é chamada no módulo main.py, onde a variável `notas` é criada
    a partir do retorno de `consolidar_notas()` e passada como argumento
    para `gerar_boletins(notas)`.
    Argumento:
        notas (pd.DataFrame): DataFrame consolidado com as notas dos alunos,
        recebido a partir da variável `notas` criada no módulo main.py.
    """

    pasta_boletins.mkdir(parents=True, exist_ok=True)

    for (turma, aluno), tabela_aluno in notas.groupby(["turma", "aluno"]):
        nome = limpar_nome_arquivo(f"{turma}_{aluno}") + ".html"
        caminho = pasta_boletins / nome

        linhas = ""
        for _, linha in tabela_aluno.iterrows():
            linhas += f"""
            <tr>
                <td>{linha['disciplina']}</td>
                <td>{linha['nota_simulado']}</td>
                <td>{linha['nota_prova']}</td>
                <td>{linha['nota_projeto']}</td>
                <td>{linha['media']}</td>
                <td>{linha['situacao']}</td>
            </tr>
            """

        html = f"""
        <!doctype html>
        <html lang="pt-br">
        <head>
            <meta charset="utf-8">
            <title>Boletim - {aluno}</title>
        </head>
        <body>
            <h1>Boletim Escolar - 2 Bimestre</h1>
            <p><strong>Aluno:</strong> {aluno}</p>
            <p><strong>Turma:</strong> {turma}</p>
            <table border="1" cellpadding="6">
                <tr>
                    <th>Disciplina</th>
                    <th>Simulado</th>
                    <th>Prova</th>
                    <th>Projeto</th>
                    <th>Media</th>
                    <th>Situacao</th>
                </tr>
                {linhas}
            </table>
        </body>
        </html>
        """

        caminho.write_text(html, encoding="utf-8")

    print(f"Boletins gerados em: {pasta_boletins}")


if __name__ == "__main__":
    gerar_boletins()