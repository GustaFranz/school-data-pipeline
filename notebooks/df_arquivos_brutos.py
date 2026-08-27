import pandas as pd
from pathlib import Path


##OBSERVAÇÃO: O código abaixo é apenas um teste para ler o arquivo simulado_6ano.csv, que está na pasta dados/simulados. Ele não faz parte do código final do projeto.
##Para ler o data frame de outras séries como 7º e 8º anos, basta alterar o nome do arquivo no caminho da variável pasta_simulados_csv.
pasta_notas_csv = Path(__file__).resolve().parent.parent.parent
pasta_simulados_csv = pasta_notas_csv / "dados" / "simulados" / "simulado_6ano.csv"

df_arquivos = pd.read_csv(pasta_simulados_csv)

print(df_arquivos)

# pasta_notas_csv = Path(__file__).resolve().parent.parent
# pasta_simulados_csv = pasta_notas_csv / "dados" / "simulados"

# arquivos = list(pasta_simulados_csv.glob("simulado_*.csv"))

# df_arquivos = pd.read_csv(arquivos)

# print(df_arquivos)