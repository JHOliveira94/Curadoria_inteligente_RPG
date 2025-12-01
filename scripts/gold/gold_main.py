"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Main - Execução Principal
Este arquivo executa as classes definidas em gold_enriquecimento.py para efetuar cálculo de score de relevância por segmento de transcrição.
"""

# ===== IMPORTAÇÕES =====
# Conecta com gold_enriquecimento.py

from gold_enriquecimento import RPGGold

def main():
    processador = RPGGold()
    processador.gold_execução()

if __name__ == "__main__":
    main()