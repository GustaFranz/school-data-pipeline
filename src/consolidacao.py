from pathlib import Path
from src.leitor_projetos import ler_projetos, transformar_projetos_para_longo
from src.leitor_provas import ler_provas, transformar_provas_para_longo
from src.leitor_simulados import ler_simulados, transformar_simulados_para_longo

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_RELATORIOS = PASTA_PROJETO / "saidas" / "relatorios"

CHAVES = ["turma", "aluno", "disciplina"]


def merge_verificado(esquerda, direita, nome_direita):
    '''
    Combina duas tabelas e verifica se todas as chaves possuem correspondência.
    O merge é realizado pelas colunas [turma, aluno, disciplina].
    Cada combinação dessas chaves deve aparecer uma única
    vez em cada tabela. Se alguma chave existir em apenas uma das tabelas,
    a função interrompe o processamento e apresenta até dez divergências.
    Argumentos:
        esquerda (pandas.DataFrame):
            Tabela principal que receberá as colunas da outra tabela.
        direita (pandas.DataFrame):
            Tabela que será combinada com a tabela principal.
        nome_direita (str):
            Nome usado para identificar a tabela da direita na mensagem
            de erro, como ``"provas"`` ou ``"projetos"``.
    Returns:
        pandas.DataFrame:
            Tabela combinada, sem a coluna auxiliar ``_merge``.
    Raises:
        ValueError:
            Se existirem chaves sem correspondência entre as tabelas.
        pandas.errors.MergeError:
            Se uma combinação de turma, aluno e disciplina estiver
            duplicada em alguma das tabelas.
    '''

    auditado = esquerda.merge(
        direita,
        on=CHAVES,
        how="outer",
        indicator=True,
        validate="one_to_one"
    )
    divergencias = auditado[auditado["_merge"] != "both"]

    if not divergencias.empty:
        amostra = divergencias[CHAVES + ["_merge"]].head(10)
        raise ValueError(
            f'Merge com {nome_direita} resultou em divergências: '
            f'{amostra.to_string(index=False)}'
        )
    return auditado.drop(columns="_merge")



def consolidar_notas():
    '''
    Lê, valida e consolida as notas de simulados, provas e projetos.
    As três fontes são transformadas para o formato longo e combinadas
    pelas colunas ``turma``, ``aluno`` e ``disciplina``. A nota de projeto
    é convertida para a mesma escala das demais avaliações.
    A média final utiliza os seguintes pesos:
    - simulado: 40%;
    - prova: 40%;
    - projeto: 20%.
    O aluno recebe a situação ``"Aprovado"`` quando a média é maior ou
    igual a 6. Caso contrário, recebe ``"Recuperacao"``.
    Returns:
        pandas.DataFrame:
            Tabela consolidada contendo as chaves de identificação, as
            notas, a nota de projeto convertida, a média final arredondada
            para uma casa decimal e a situação do aluno.
    Raises:
        ValueError:
            Se os dados de entrada forem inválidos ou se alguma das fontes
            não possuir correspondência completa com as demais.
        pandas.errors.MergeError:
            Se houver chaves duplicadas durante a consolidação.
    '''
    simulados = transformar_simulados_para_longo(ler_simulados())
    provas = transformar_provas_para_longo(ler_provas())
    projetos = transformar_projetos_para_longo(ler_projetos())

    tabela = merge_verificado(simulados, provas, "provas")
    tabela = merge_verificado(tabela, projetos, "projetos")

    tabela["nota_simulado"] = tabela["nota_simulado"].astype(float)
    tabela["nota_prova"] = tabela["nota_prova"].astype(float)
    tabela["nota_projeto"] = tabela["nota_projeto"].astype(float)

    tabela["nota_projeto_convertida"] = tabela["nota_projeto"] * 2

    tabela["media"] = (
        tabela["nota_simulado"] * 10
        + tabela["nota_prova"] * 10
        + tabela["nota_projeto_convertida"] * 5
    ) / 25

    tabela["media"] = tabela["media"].round(1)
    tabela["situacao"] = tabela["media"].apply(
        lambda media: "Aprovado" if media >= 6 else "Recuperacao"
    )

    return tabela


def salvar_relatorio_final(tabela):
    """
    Salva a tabela consolidada no relatório CSV definitivo.
    O arquivo é gravado como ``saidas/relatorios/notas_consolidadas.csv``,
    sem o índice do DataFrame e com codificação UTF-8 com BOM, adequada
    para abertura no Excel. O diretório é criado automaticamente quando
    não existe. Um arquivo anterior com o mesmo nome é sobrescrito.
    Argumentos:
        tabela (pandas.DataFrame):
            Tabela consolidada que será gravada no relatório.
    Returns:
        pathlib.Path:
            Caminho completo do arquivo CSV criado.
    Raises:
        OSError:
            Se o diretório ou o arquivo não puder ser criado ou gravado.
    """
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_RELATORIOS / "notas_consolidadas.csv"
    tabela.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
        )
    return caminho


if __name__ == "__main__":
    notas = consolidar_notas()
    caminho = salvar_relatorio_final(notas)
    print(notas.head())
    print(f"Relatorio salvo em: {caminho}")