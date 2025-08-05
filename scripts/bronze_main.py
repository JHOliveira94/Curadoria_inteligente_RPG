"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Main - Execução Principal
Este arquivo executa as classes definidas em bronze_transcricao.py.
"""

# ===== IMPORTAÇÕES =====
# Conecta com bronze_transcricao.py

from bronze_transcricao import RPGTranscricao


# ===== FUNÇÃO PRINCIPAL =====
# Função que coordena e executa os comandos definidos em bronze_transcricao.py.

def main():
    processador = RPGTranscricao()
    processador.bronze_execução()

if __name__ == "__main__":
    main()