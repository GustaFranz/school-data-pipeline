from src.automacao_portal import executar_automacao
from src.boletins import gerar_boletins
from src.consolidacao import consolidar_notas, salvar_relatorio_final


def main():
    print("School Data Pipeline — iniciando coleta no portal...")
    executar_automacao()

    print("Consolidando notas...")
    notas = consolidar_notas()
    salvar_relatorio_final(notas)

    print("Gerando boletins...")
    gerar_boletins(notas)

    print("Projeto finalizado.")


if __name__ == "__main__":
    main()