from pathlib import Path
import whisper

class Config:

    dir_raw = Path("data/raw")
    base_dir_bronze = Path("data/bronze")
    
    modelo_transcricao = "small"
    idioma_transcricao = "pt"
    

class EstruturaBronze:
    
    def listar_campanhas(self) -> list:
        
        campanhas_trabalhadas = []

        for item in Config.dir_raw.iterdir():
            if item.is_dir():
                campanhas_trabalhadas.append(item.name)

        return campanhas_trabalhadas
    
    def estruturar_diretorios(self) -> dict:
        campanhas = self.listar_campanhas()
        dict_dir_transcricoes = {}

        for campanha in campanhas:
            dir_campanha = Config.base_dir_bronze / campanha / "transcricoes"
            dir_campanha.mkdir(parents=True, exist_ok=True)
            
            dict_dir_transcricoes[campanha] = dir_campanha

            print(f"✅ Criado diretório de transcrições de {campanha} com sucesso!")
        
        return dict_dir_transcricoes


class Transcrever:

    def audios_por_campanha(self) -> dict:
    
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
        dict_audios_campanha = self.audios_por_campanha()
        
        # Carregar modelo Whisper
        modelo = whisper.load_model(Config.modelo_transcricao)
        
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
                print(f"🎵 Transcrevendo: {arquivo_audio.name}")
                
                # Transcrever
                resultado = modelo.transcribe(str(arquivo_audio), language=Config.idioma_transcricao)
                
                # Extrair dados
                texto_transcrito_completo = resultado["text"]
                texto_transcrito_segmentado = resultado["segments"]
                
                # Nomes dos arquivos
                nome_base = arquivo_audio.stem
                caminho_completo = pasta_destino / f"{nome_base}_completo.txt"
                caminho_segmentado = pasta_destino / f"{nome_base}_segmentado.txt"
                
                # 1. Salvar texto completo
                with open(caminho_completo, 'w', encoding='utf-8') as f:
                    f.write(texto_transcrito_completo)
                
                # 2. Salvar segmentos
                with open(caminho_segmentado, 'w', encoding='utf-8') as f:
                    for i, seg in enumerate(texto_transcrito_segmentado, 1):
                        inicio = seg['start']
                        fim = seg['end']
                        texto = seg['text'].strip()
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




