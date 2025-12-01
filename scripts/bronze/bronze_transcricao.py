"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Transcricao - Classes e Funções
Neste script estão as classes e funções para transcrição dos aúdios e organização dos arquivos relacionados na camada bronze.

===== RESULTADOS ESPERADOS =====
    Transcrição em texto corrido em formato .txt
    Transcrição segmentada em formato .txt
"""

# ===== IMPORTAÇÕES =====
# Bibliotecas necessárias para a etapa bronze do pipeline

from pathlib import Path # Organização dos diretórios no sistema
from faster_whisper import WhisperModel # Modelo para transcrição dos arquivos de aúdio .wav


# ===== CONFIGURAÇÕES GERAIS PARA O SCRIPT=====
class Config:
    """Configurações centralizadas do projeto.
        - Facilita mudanças no projeto
        - Facilita escalabilidade
        - Facilita correções   
    """

    dir_raw = Path("data/raw") # Caminho dos arquivos para transcrição
    base_dir_bronze = Path("data/bronze") # Caminho para novos arquivos gerados neste script
    
    modelo_transcricao = "small" # Modelo usado para transcrição. Opções: tiny, base, small, medium, large, large-v2, large-v3, distil-large-v2, distil-large-v3
    idioma_transcricao = "pt" # Linguagem principal presente no áudio transcrito
    

# ===== CLASSES OPERACIONAIS=====
class EstruturaBronze:
    """
    Cria estrutura de diretórios para essa etapa.
    """

    def listar_campanhas(self) -> list:
        """
        Busca as campanhas já trabalhadas na camada raw.

        Returns:
            list: Lista com os nomes das campanhas já trabalhadas.

        """
        campanhas_trabalhadas = []

        for item in Config.dir_raw.iterdir():
            if item.is_dir():
                campanhas_trabalhadas.append(item.name)

        return campanhas_trabalhadas
    
    def estruturar_diretorios(self) -> dict:
        """
        Estabelece os diretórios necessários para a camada bronze.

        Returns:
            dict: Dicionário cuja chave é o nome da campanha e o valor é o caminho do diretório para as transcrições.
        """


        campanhas = self.listar_campanhas()
        dict_dir_transcricoes = {}

        for campanha in campanhas:
            dir_campanha = Config.base_dir_bronze / campanha / "transcricoes"
            dir_campanha.mkdir(parents=True, exist_ok=True)
            
            dict_dir_transcricoes[campanha] = dir_campanha

            print(f"✅ Criado diretório de transcrições de {campanha} com sucesso!")
        
        return dict_dir_transcricoes


class Transcrever:
    """
    Gerenciamento do processo de transcrição.
    """

    def audios_por_campanha(self) -> dict:
        """
        Busca os áudios disponíveis por campanha para serem transcritos.

        Returns:
            dict: Dicionário cuja chave é o nome da campanha e o valor é uma lista com os arquivos de áudio encontrados.
        """

        campanhas = EstruturaBronze().listar_campanhas()
        dict_audios_campanha = {}
        
        
        for campanha in campanhas:
            dir_audio = Config.dir_raw / campanha / "audio"
            lista_audios = []

            for arquivo in dir_audio.iterdir():
                if arquivo.suffix == ".wav":
                    lista_audios.append(arquivo)
            
            dict_audios_campanha[campanha] = lista_audios
        
        return dict_audios_campanha
    
    def transcrever_audios(self):
        """
        Transcreve áudios e salva em arquivos .txt.
        
        Gera dois arquivos por áudio:
            {nome}_completo.txt: Texto corrido
            {nome}_segmentado.txt: Com segmentado por timestamps
        """

        dict_audios_campanha = self.audios_por_campanha()
        
        # Carregar modelo Whisper
        from faster_whisper import WhisperModel
        modelo = WhisperModel(Config.modelo_transcricao, device="cpu", compute_type="int8")
        
        # Pegar diretórios de destino (bronze)
        estrutura = EstruturaBronze()
        dict_dir_transcricoes = estrutura.estruturar_diretorios()
        
        # Para cada campanha:
        for campanha, lista_audios in dict_audios_campanha.items():
            print(f"🔄 Processando campanha: {campanha}")
            
            # Pasta de destino desta campanha
            pasta_destino = dict_dir_transcricoes[campanha]
            
            # Para cada áudio da campanha:
            for arquivo_audio in lista_audios:
                
                
                # Nomes dos arquivos
                nome_base = arquivo_audio.stem
                caminho_completo = pasta_destino / f"{nome_base}_completo.txt"
                caminho_segmentado = pasta_destino / f"{nome_base}_segmentado.txt"
                
                # Verifica se arquivo já foi processado.
                if caminho_completo.exists() and caminho_segmentado.exists():
                    print(f"⏭️ Pulando {arquivo_audio.name} - já processado")
                    continue

                print(f"🎵 Transcrevendo: {arquivo_audio.name}")
                
                # Transcrever com faster-whisper
                segments, info = modelo.transcribe(str(arquivo_audio), language=Config.idioma_transcricao)
                
                # Converter segments em lista (faster-whisper retorna generator)
                lista_segmentos = list(segments)
                
                # Extrair dados
                texto_transcrito_completo = " ".join([seg.text for seg in lista_segmentos])
                texto_transcrito_segmentado = lista_segmentos
                
                
                
                print(f"🎵 Transcrevendo: {arquivo_audio.name}")

                # 1. Salvar texto completo
                with open(caminho_completo, 'w', encoding='utf-8') as f:
                    f.write(texto_transcrito_completo)
                
                # 2. Salvar segmentos
                with open(caminho_segmentado, 'w', encoding='utf-8') as f:
                    for i, seg in enumerate(texto_transcrito_segmentado, 1):
                        inicio = seg.start     # Atributo, não dicionário
                        fim = seg.end         # Atributo, não dicionário
                        texto = seg.text.strip()  # Atributo, não dicionário
                        f.write(f"{i:03d}|{inicio:06.2f}|{fim:06.2f}|{texto}\n")
            
                print(f"✅ Salvos: {nome_base}_completo.txt e {nome_base}_segmentado.txt")


class RPGTranscricao:
    """Classe principal que coordena todo o processamento da camada Bronze"""
    
    def __init__(self):
        self.estrutura = EstruturaBronze()
        self.transcritor = Transcrever()
    
    def bronze_execução(self):
        """Executa todo o pipeline bronze"""
        print("🚀 Iniciando processamento Bronze...")
        
        # 1. Criar estrutura
        print("📁 Criando estrutura de diretórios...")
        self.estrutura.estruturar_diretorios()
        
        # 2. Transcrever tudo
        print("🎵 Iniciando transcrições...")
        self.transcritor.transcrever_audios()
        
        print("✅ Processamento Bronze concluído!")




