import pandas as pd
from pathlib import Path

pd.set_option("display.max_rows", None)
'''
Possibilita verificar quantidade linhas quase ilimitadas no hear()
'''

pasta_notas_csv = Path(__file__).resolve().parent.parent
pasta_simulados_csv = pasta_notas_csv / "dados" / "simulados"

def unir_simulados():
    simulados = list(pasta_simulados_csv.glob("simulado_*.csv"))
    lista_simulados = []

    for simulado in simulados:
        df_simulado = pd.read_csv(simulado)
        lista_simulados.append(df_simulado)
    # Quando você concatena DataFrames com pd.concat(), o ignore_index=True faz o Pandas ignorar os índices originais de cada DataFrame e criar um novo índice contínuo, 
    # começando em 0.    return pd.concat(lista_simulados, ignore_index=True)
    return pd.concat(lista_simulados, ignore_index=True)


def transformar_simulado_para_longo(simulados):
    """
Transforma a tabela do formato largo para o formato longo usando melt.
As colunas "turma" e "aluno" são mantidas fixas por meio de id_vars.
Todas as demais colunas são convertidas em linhas:
os nomes dessas colunas passam a ser armazenados em "disciplina", definido por var_name;
os valores contidos nelas passam a ser armazenados em "nota_simulado", definido por value_name.
Exemplo conceitual:
Antes:
    turma | aluno | matematica | portugues
    
Depois:
    turma | aluno | disciplina | nota_simulado
"""
    return simulados.melt(
        # var_name: nomeia a nova coluna que identificará o que eram as colunas originais, 
        # já que elas serão transformadas em linhas.
        id_vars=["turma", "aluno"],
        # value_name: nomeia a nova coluna que armazenará os valores que antes estavam 
        # distribuídos nessas colunas originais.
        var_name="disciplina",
        value_name="nota_simulado"
    )


simulados = unir_simulados()
simulados_longos = transformar_simulado_para_longo(simulados)
print(simulados_longos.head(75))
#Coloquei head(145) para verificar que:
#os primeiros alunos: Ana e Bruno aparecem no começo da lista do 6º ano para a disciplina  Lingua Portuguesa
#os mesmos alunos aparecem no começo da lisra para a disciplina Matemática (nos índice 71 e 72)
#lembrar que normalmente o .head() não suporta numero alto como 70, então usei:
#pd.set_option("display.max_rows", None) que permite isso -> no topo do aqruivo
