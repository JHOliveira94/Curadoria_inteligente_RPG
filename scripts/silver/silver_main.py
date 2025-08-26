"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Main - Execução Principal
Este arquivo executa as classes definidas em silver_analise_sentimentos.py para gerar análise de 
sentimentos a partir das transcrições presentes na camada bronze.
"""

# ===== IMPORTAÇÕES =====
# Conecta com silver_analise_sentimentos.py

from silver_analise_sentimentos import RPGAnaliseSentimento


def main():
    processador = RPGAnaliseSentimento()
    processador.silver_execução()

if __name__ == "__main__":
    main()