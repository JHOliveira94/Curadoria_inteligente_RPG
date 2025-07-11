"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Main - Execução Principal
Este arquivo executa as classes definidas em raw_downloader.py para efetuar o download de vídeos de RPG na camada raw.
"""

# ===== IMPORTAÇÕES =====
# Conecta com raw_downloader.py

from raw_downloader import RPGDownloader

# ===== CONFIGURAÇÕES =====

URL = "https://www.youtube.com/watch?v=f-tmb-Tcn_k"

# ===== FUNÇÃO PRINCIPAL =====
# Função que coordena e executa os comandos definidos em raw_downloader.py

def main():
    """
    Função principal que executa o download
    """
    print("🎮 Curadoria Inteligente de RPG - Download Automático")
    print("="*60)
    
    # Criar instância do downloader
    rpg_downloader = RPGDownloader()
    
    # Processar o vídeo
    resultado = rpg_downloader.processar_video(URL)
    
    # Mostrar resumo
    rpg_downloader.mostrar_resumo(resultado)
    
    return resultado

# ===== EXECUÇÃO =====
if __name__ == "__main__":
    main()