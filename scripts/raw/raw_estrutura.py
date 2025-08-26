"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Estrutura- Classes e Funções
Neste script estão as classes e funções para estruturar a organização geral para o projeto.

"""

# ===== IMPORTAÇÕES =====

from pathlib import Path
     
def criar_estrutura_pastas() -> tuple:
    """
    Cria estrutura de pastas para o projeto.
      
    Returns:
        tupla: diretórios importantes para o projeto
    """
    dir_base = Path(__file__).parent.parent
    
    dir_config = dir_base / "config"
    dir_dash = dir_base / "dashboard"
    dir_db = dir_base / "db"
    dir_vol = dir_base / "volumes"
    dir_doc = dir_base / "docs"
    dir_data = dir_base / "data"

    print("🔄 Criando a estrutura de diretórios...")

    
    for pasta in [dir_dash, dir_config, dir_data, dir_db, dir_doc, dir_vol]:
        pasta.mkdir(parents=True, exist_ok=True)
    
    print("\n✅ Estrutura criada com sucesso!")


    return dir_dash, dir_config, dir_data, dir_db, dir_doc, dir_vol

if __name__ == "__main__":
    pastas_criadas = criar_estrutura_pastas()