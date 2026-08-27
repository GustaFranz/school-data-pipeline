import pandas as pd
from pathlib import Path


pasta_notas_csv = Path(__file__).resolve().parent.parent.parent
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


df_simulados = unir_simulados()
print(df_simulados)