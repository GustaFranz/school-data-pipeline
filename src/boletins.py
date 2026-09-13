import re
import unicodedata
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


# Essa constante ajuda a impedir que outras colunas existentes no
# DataFrame consolidado sejam enviadas por engano para o boletim.
COLUNAS_BOLETIM = [
    "disciplina",
    "nota_simulado",
    "nota_prova",
    "nota_projeto",
    "media",
    "situacao",
]


def limpar_nome_arquivo(texto):
    """
    Converte um texto em um nome seguro para ser utilizado em arquivos.
    Exemplo: "6º ano Matutino - João da Silva"
    pode se transformar aproximadamente em:
    "6_ano_matutino_joao_da_silva"

    Etapas realizadas
    1. Converte o valor recebido para string.
    2. Usa ``unicodedata.normalize()`` para decompor caracteres acentuados.
    3. Remove as marcas de acentuação usando
       ``unicodedata.combining()``.
    4. Usa ``re.sub()`` para substituir caracteres inadequados por "_".
    5. Remove underscores das extremidades.
    6. Converte o resultado para letras minúsculas.

    Argumento --> texto:
        Texto que será usado para formar o nome do arquivo.
        Pode ser, por exemplo, o nome de um aluno ou uma combinação
        de turma e aluno.
    Retorno(str):
        Nome normalizado e seguro para ser utilizado em arquivos.

    Observação
    Esta função apenas prepara o NOME do arquivo. Ela não grava nada
    no disco e não define onde o usuário salvará o arquivo.
    """
    # normalize("NFKD", ...) decompõe vários caracteres acentuados.
    # De forma simplificada:
    # "ã" -> "a" + marca de acento
    # "é" -> "e" + marca de acento
    # str(texto) garante que o valor recebido seja tratado como texto.
    normalizado = unicodedata.normalize(
        "NFKD",
        str(texto),
    )

    # unicodedata.combining(caractere) identifica caracteres que são
    # marcas combinantes, como acentos separados após a normalização.
    #
    # O generator expression percorre todos os caracteres.
    #
    # O "not" faz com que sejam mantidos apenas os caracteres
    # que NÃO são marcas de acentuação.
    #
    # Depois, "".join(...) reúne novamente os caracteres.
    sem_acentos = "".join(
        caractere
        for caractere in normalizado
        if not unicodedata.combining(caractere)
    )
    # re.sub(padrao, substituto, texto)
    # "qualquer sequência de caracteres que NÃO seja letra,
    # número, underscore ou hífen será substituída por '_'".
    seguro = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        sem_acentos,
    ).strip("_")

    # Se, por algum motivo, o texto resultar em string vazia,
    # 'sem_nome' fornece um nome de segurança.
    return seguro.lower() or "sem_nome"


def selecionar_boletim(notas, turma, aluno):
    """
    Seleciona no DataFrame consolidado apenas as notas de um aluno.
    Esta função recebe o DataFrame completo produzido pela consolidação
    e faz um recorte com base em duas informações:
    - turma escolhida;
    - aluno escolhido.
    Dessa forma, a função não precisa chamar ``consolidar_notas()``
    novamente. O DataFrame já pronto é recebido como argumento,
    seguindo a ideia da M3 de passagem explícita de dependências.

    Parâmetros
    notas : pandas.DataFrame
        DataFrame consolidado contendo todas as turmas, alunos,
        disciplinas e notas.
    turma : str
        Nome da turma que deve ser selecionada.
    aluno : str
        Nome do aluno que deve ser selecionado.

    Retorno
    pandas.DataFrame
        Novo DataFrame contendo somente as linhas do aluno escolhido
        e apenas as colunas definidas em ``COLUNAS_BOLETIM``.

    Exceções
    ValueError
        É gerado se nenhuma linha correspondente à combinação
        de turma e aluno for encontrada.

    Observação
    O ``.copy()`` cria explicitamente um novo DataFrame a partir
    do recorte. Assim, futuras alterações feitas especificamente
    para apresentação do boletim não precisam afetar o DataFrame
    consolidado original.
    """

    # .eq(turma) compara cada valor da coluna "turma"
    # com a turma recebida.
    # O resultado é uma Series booleana:True, False, True ...
    # O mesmo acontece para a coluna "aluno".
    # O operador & combina as duas condições elemento a elemento.
    mascara = (
        notas["turma"].eq(turma)
        & notas["aluno"].eq(aluno)
    )

    # .loc recebe:
    # antes da vírgula -> quais LINHAS queremos;
    # depois da vírgula -> quais COLUNAS queremos.
    # Portanto:
    # mascara - seleciona apenas as linhas do aluno/turma;
    # COLUNAS_BOLETIM - limita a saída às colunas oficiais do boletim.
    tabela = notas.loc[
        mascara,
        COLUNAS_BOLETIM,
    ].copy()

    # .empty verifica se o DataFrame ficou sem linhas.
    # Se ficou vazio, significa que a combinação
    # turma + aluno não foi encontrada.
    if tabela.empty:
        raise ValueError(
            "Nenhuma nota encontrada "
            f"para {aluno!r} "
            f"na turma {turma!r}."
        )

    # O DataFrame já filtrado retorna para quem chamou a função.
    return tabela


def boletim_para_csv(tabela):
    """
    Converte o DataFrame de um boletim em conteúdo CSV binário.
    Esta função NÃO salva o arquivo CSV em uma pasta do projeto.
    Em vez disso, ela transforma o DataFrame em texto CSV e,
    logo depois, converte esse texto para ``bytes``.
    Esses bytes poderão ser:
    - entregues ao ``st.download_button`` para download individual;
    - inseridos dentro de um arquivo ZIP criado em memória.

    Parâmetros
    tabela : pandas.DataFrame
        DataFrame contendo os dados de um boletim.

    Retorno
    bytes
        Conteúdo do CSV em formato binário, pronto para ser usado
        em downloads ou inserido dentro de um ZIP.

    Observação sobre o local do download
    ------------------------------------
    Esta função não escolhe onde o arquivo será salvo no computador
    (como na versão anterior em que o caminho da pasta era declarada).
    Quando esses bytes forem enviados ao ``st.download_button()``,
    o navegador do usuário será responsável pelo download.
    Dependendo da configuração do navegador, o arquivo poderá:
    - ser salvo automaticamente na pasta Downloads;
    - ou abrir uma janela "Salvar como..." para o usuário escolher
      a pasta de destino.
    """

    # to_csv(index=False)
    # Como nenhum caminho de arquivo foi fornecido,
    # pandas NÃO grava o CSV no disco.
    # Em vez disso, to_csv() retorna uma string contendo
    # todo o conteúdo CSV.
    csv_texto = tabela.to_csv(
        index=False
    )

    # encode("utf-8-sig") transforma a string em bytes.
    # O uso de utf-8-sig inclui a marca BOM, que costuma ajudar
    # programas como Excel a reconhecerem corretamente caracteres
    # acentuados em arquivos CSV.
    csv_bytes = csv_texto.encode(
        "utf-8-sig"
    )

    return csv_bytes


def gerar_zip_turma(
    notas,
    turma,
):
    """
    Cria em memória um arquivo ZIP contendo os boletins de uma turma.
    Cada aluno da turma recebe um arquivo CSV próprio dentro do ZIP.
    O ponto principal desta função é que nenhum desses arquivos precisa
    ser criado fisicamente em ``saidas/boletins`` antes da compactação.
    Todo o processo acontece em memória RAM:
        DataFrame
            ↓
        separação por aluno
            ↓
        CSV em bytes
            ↓
        arquivos inseridos no ZIP
            ↓
        ZIP armazenado em BytesIO
            ↓
        bytes do ZIP

    Esses bytes podem depois ser enviados diretamente ao
    ``st.download_button()``.

    Parâmetros
    notas : pandas.DataFrame
        DataFrame consolidado contendo todos os alunos e turmas.

    turma : str
        Turma cujos boletins serão incluídos no ZIP.

    Retorno
    bytes
        Conteúdo completo do arquivo ZIP em formato binário.

    Exceções
    ValueError
        É gerado quando nenhuma linha correspondente à turma
        informada é encontrada.

    Observação sobre o local do arquivo
    O ZIP criado aqui NÃO recebe um caminho como:
        C:/projeto/saidas/boletins/boletins_6ano.zip
    Ele existe apenas temporariamente na memória RAM.
    Quando o conteúdo retornado por esta função for usado em um
    ``st.download_button()``, o navegador fará o download.
    O local final será definido pelas configurações do navegador
    ou pelo próprio usuário, por exemplo:
    - pasta Downloads;
    - Área de Trabalho;
    - Documentos;
    - qualquer outra pasta escolhida na janela "Salvar como...".
    """

    dados_turma = notas.loc[
        notas["turma"].eq(turma)
    ]

    # Se nenhuma linha foi encontrada,
    # a função interrompe o processamento com um erro explícito.
    if dados_turma.empty:
        raise ValueError(
            f"Turma não encontrada: {turma!r}"
        )

    # BytesIO vem do módulo io.
    # Ele cria um buffer binário em memória RAM que se comporta
    # de forma semelhante a um arquivo aberto em modo binário.
    # nenhum arquivo físico é criado no disco.
    memoria = BytesIO()

    # Estamos criando/escrevendo um novo arquivo ZIP.
    # ZIP_DEFLATED informa ao ZipFile que os arquivos inseridos
    # devem usar o algoritmo de compressão DEFLATE.
    with ZipFile(
        memoria,
        mode="w",
        compression=ZIP_DEFLATED,

    ) as arquivo_zip:

        for aluno, tabela_aluno in (
            dados_turma.groupby("aluno")
        ):

            # Mantém apenas as colunas oficiais do boletim.
            tabela = tabela_aluno[
                COLUNAS_BOLETIM
            ]

            nome = limpar_nome_arquivo(
                aluno
            )

    # writestr() é um método de ZipFile.
    # Ele permite criar um arquivo DENTRO do ZIP
    # usando diretamente um conteúdo que já está na memória.
    # Primeiro argumento:
    #     f"boletim_{nome}.csv"
    # é o nome que o arquivo terá dentro do ZIP.
    # Segundo argumento:
    #     boletim_para_csv(tabela)
    # são os bytes do CSV.
    # Isso significa que NÃO precisamos fazer:
    # 1. criar boletim_ana.csv no disco;
    # 2. salvar esse CSV;
    # 3. abrir novamente;
    # 4. colocar dentro do ZIP;
    # 5. apagar o arquivo temporário.
    # O CSV vai diretamente:
    # DataFrame -> bytes -> ZIP em memória.
            arquivo_zip.writestr(
                f"boletim_{nome}.csv",
                boletim_para_csv(tabela),
            )

    # Ao terminar o bloco "with", o ZipFile é fechado corretamente.
    # Isso é importante porque um ZIP precisa finalizar sua
    # estrutura interna antes de ser utilizado.
    # memoria.getvalue() devolve todo o conteúdo armazenado
    # dentro do BytesIO como bytes.
    # Portanto, o retorno desta função é algo conceitualmente assim:
    # bytes
    # └── ZIP
    #     ├── boletim_ana.csv
    #     ├── boletim_bruno.csv
    #     ├── boletim_carla.csv
    #     └── ...
    # Esses bytes serão posteriormente fornecidos ao Streamlit.
    return memoria.getvalue()