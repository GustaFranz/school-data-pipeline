from src.automacao_portal import executar_automacao
from src.consolidacao import consolidar_notas, salvar_relatorio_final


def main():
    print("School Data Pipeline — iniciando coleta no portal...")
    executar_automacao()

    print("Consolidando notas...")
    notas = consolidar_notas()
    caminho_csv = salvar_relatorio_final(notas)

    print(f'Relatório: {caminho_csv}')


if __name__ == "__main__":
    main()