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

    return pd.concat(lista_simulados)

df_simulados = unir_simulados()
print(df_simulados)







print(df_simulados)


# pasta_notas_csv = Path(__file__).resolve().parent.parent
# pasta_simulados_csv = pasta_notas_csv / "dados" / "simulados"

# arquivos = list(pasta_simulados_csv.glob("simulado_*.csv"))

# df_arquivos = pd.read_csv(arquivos)

# print(df_arquivos)