"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Downloader - Classes e Funções
Neste script estão as classes e funções para download e organização dos dados na camada raw.

===== RESULTADOS ESPERADOS =====
    Vídeo em formato .mp4
    Áudio em formato .wav
    Metadados em arquivo .json
"""


# ===== IMPORTAÇÕES =====
# Bibliotecas necessárias para a etapa raw do pipeline

from yt_dlp import YoutubeDL # Downalod de vídeos, áudio e metadados
from pathlib import Path # Organização dos repositórios
from datetime import datetime # Complementar metadados com datas
import json # Para trabalhar com os metadados
import re # Para padronizar textos


# ===== CONFIGURAÇÕES GERAIS PARA O SCRIPT=====

class Config:
    """Configurações centralizadas do projeto.
        - Facilita mudanças no projeto
        - Facilita escalabilidade
        - Facilita correções   
    """
    
    # Base da estrutura de pastas para a camada raw
    BASE_DIR = Path("data/raw")
    
    # Campanhas conhecidas para identificação automática ao longo do script
    CAMPANHAS_CONHECIDAS = {
        "fabula ultima": "fabula_ultima",
        "#fabulaultima": "fabula_ultima",
        "ordem paranormal": "ordem_paranormal",
        "critical role": "critical_role",
        "jambô": "jambo_editora",
        "cellbit": "ordem_paranormal"
    }
    
    # Configurações de download usadas pelo YoutubeDL
    QUALIDADE_VIDEO = "bestvideo+bestaudio/best"
    QUALIDADE_AUDIO = "bestaudio/best"
    FORMATO_AUDIO = "wav"
    BITRATE_AUDIO = "192"


# ===== CLASSES OPERACIONAIS=====

class CampanhaDetector:
    """Classe responsável por detectar campanhas automaticamente
        - Usa o dicionário CAMPANHAS_CONHECIDAS para determinar de que campanha é o vídeo.
        - Usa a campanha para padronizar o salvamento e a busca de arquivos. 
    """
    
    def __init__(self):
        self.campanhas = Config.CAMPANHAS_CONHECIDAS
    
    def detectar(self, url: str, titulo: str = "") -> str:
        """
        Detecta campanha baseado na URL ou título do vídeo indicado.
        
        Args:
            url (str): URL do vídeo
            titulo (str): Título do vídeo (quando disponível)
        
        Returns:
            str: Nome da campanha detectada
        """
        # Verificar pela URL primeiro
        url_lower = url.lower()
        for palavra_chave, campanha in self.campanhas.items():
            if palavra_chave in url_lower:
                return campanha
        
        # Verificar título se fornecido
        if titulo:
            titulo_lower = titulo.lower()
            for palavra_chave, campanha in self.campanhas.items():
                if palavra_chave in titulo_lower:
                    return campanha
        
        # Se não detectar automaticamente, perguntar ao usuário
        return self._perguntar_usuario()
    
    def _perguntar_usuario(self) -> str:
        """Pergunta ao usuário qual a campanha do vídeo solicitado.
            - Prima pela execução organizada do pipeline, 
            - Garante que os arquivos sejam armazenados no diretório correto.
            - Em caso de não detectar automáticamente, usuário informa a campanha
        """
        print("\n🤔 Não consegui identificar a campanha automaticamente.")
        print("Campanhas disponíveis:")
        
        campanhas_unicas = list(set(self.campanhas.values()))
        for i, campanha in enumerate(campanhas_unicas, 1):
            print(f"  {i}. {campanha}")
        print(f"  {len(campanhas_unicas) + 1}. nova_campanha")
        
        while True:
            escolha = input("Digite o número correspondete ou nome da campanha: ").strip()
            
            # Verificar se é número
            try:
                numero = int(escolha)
                if 1 <= numero <= len(campanhas_unicas):
                    return campanhas_unicas[numero - 1]
                
                elif numero == len(campanhas_unicas) + 1:
                    nome_nova = input("Nome da nova campanha: ").strip()
                    if not nome_nova:  # Verificar se não está vazio
                        print("❌ Nome não pode estar vazio. Tente novamente.")
                        continue
    
                    # Normalizar espaços e converter
                    nome_limpo = re.sub(r'\s+', ' ', nome_nova)
                    return nome_limpo.replace(" ", "_").lower()

            except ValueError:
                pass
            
            # Verificar se foi digitado o nome da campanha
            if escolha.replace(" ", "_").lower():
                return escolha.replace(" ", "_").lower()
            
            print("❌ Opção inválida. Tente novamente.")

class EpisodioManager:
    """Classe responsável por gerenciar numeração de episódios
        - Garante padronização e serialização dos arquivos.
        - Padrão: ep01, ep02, ...
        - Essencial para campanhas longas com várias sessões.
    """
    
    def descobrir_proximo(self, pasta_campanha: Path) -> str:
        """
        Define o próximo número de episódio.
        - Garante a padronização do nome dos arquivos.
        
        Args:
            pasta_campanha (Path): Diretório da campanha
        
        Returns:
            str: Próximo episódio (ex: "ep01")
        """
        pasta_videos = pasta_campanha / "videos"
        
        if not pasta_videos.exists():
            return "ep01"
        
        # Buscar arquivos existentes
        arquivos_existentes = list(pasta_videos.glob("ep*")) # .glob = busca global por arquivos que em seu nome contenha("...")
        
        if not arquivos_existentes:
            return "ep01"
        
        # Extrair números
        numeros_episodios = []
        for arquivo in arquivos_existentes:
            match = re.search(r'ep(\d+)', arquivo.name) # \d+ busca por um ou mais dígitos, () captura o conteúdo encontrado
            if match:
                numeros_episodios.append(int(match.group(1))) # group(1) destaca os dígitos capturados. Ex: em ep01, destaca 01 que foi capturado
        
        if not numeros_episodios:
            return "ep01"
        
        # Próximo número
        proximo = max(numeros_episodios) + 1
        return f"ep{proximo:02d}"

class FileNameGenerator:
    """Classe responsável por gerar nomes padronizados de arquivos
        - Padrão: {epXX}_{video_id}
        - Exemplo: ep01_f-tmb-Tcn_k
    """
    
    def criar_nome(self, episodio: str, video_id: str, extensao: str = "") -> str:
        """
        Cria nome padronizado para arquivo
        
        Args:
            episodio (str): Número do episódio
            video_id (str): ID do vídeo
            extensao (str): Extensão do arquivo
        
        Returns:
            str: Nome do arquivo formatado
        """
        episodio_limpo = self._limpar_texto(episodio)
        video_id_limpo = self._limpar_texto(video_id)
        
        nome = f"{episodio_limpo}_{video_id_limpo}"
        if extensao:
            nome += f".{extensao}"
        
        return nome
    
    def _limpar_texto(self, texto: str) -> str:
        """Remove caracteres especiais do texto"""
        limpo = re.sub(r'[^\w\-]', '', texto)
        return limpo

class VideoInfoExtractor:
    """Classe responsável por extrair os metadados dos vídeos"""
    
    def extrair(self, url: str) -> dict:
        """
        Extrai informações do vídeo sem fazer download
        
        Args:
            url (str): URL do vídeo
        
        Returns:
            dict: Informações do vídeo
        """
        print("🔍 Extraindo informações do vídeo...")
        
        try:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            
            dados = {
                'titulo': info.get('title', ''),
                'video_id': info.get('id', 'unknown'),
                'data_upload': info.get('upload_date', '00000000'),
                'canal': info.get('uploader', ''),
                'duracao': info.get('duration', 0),
                'visualizacoes': info.get('view_count', 0),
                'likes': info.get('like_count', 0),
                'descricao': info.get('description', ''),
                'tags': info.get('tags', [])
            }
            
            print(f"📺 Título: {dados['titulo']}")
            return dados
            
        except Exception as e:
            print(f"❌ Erro ao extrair informações: {e}")
            return self._dados_padrao()
    
    def _dados_padrao(self) -> dict:
        """Retorna dados padrão em caso de erro na busca"""
        return {
            'titulo': 'Título desconhecido',
            'video_id': 'unknown',
            'data_upload': '00000000',
            'canal': 'Desconhecido',
            'duracao': 0,
            'visualizacoes': 0,
            'likes': 0,
            'descricao': '',
            'tags': []
        }

class Downloader:
    """Classe responsável por fazer downloads"""
    
    def baixar_video(self, url: str, pasta_destino: Path, nome_arquivo: str) -> bool:
        """
        Faz download do vídeo
        
        Args:
            url (str): URL do vídeo
            pasta_destino (Path): Pasta de destino
            nome_arquivo (str): Nome base do arquivo
        
        Returns:
            bool: True se sucesso
        """
        print("🔄 Fazendo download do vídeo...")
        
        try:
            caminho = pasta_destino / f"{nome_arquivo}.%(ext)s" # %(ext)s placeholder que o yt-dlp substitui automaticamente pela extenção do vídeo
            
            opcoes = {
                "format": Config.QUALIDADE_VIDEO,
                "outtmpl": str(caminho),
                "writeinfojson": False,
            }
            
            with YoutubeDL(opcoes) as ydl:
                ydl.download([url])
            
            print(f"✅ Vídeo salvo: {nome_arquivo}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download do vídeo: {e}")
            return False
    
    def baixar_audio(self, url: str, pasta_destino: Path, nome_arquivo: str) -> bool:
        """
        Faz download do áudio
        
        Args:
            url (str): URL do vídeo
            pasta_destino (Path): Pasta de destino
            nome_arquivo (str): Nome base do arquivo
        
        Returns:
            bool: True se sucesso
        """
        print("🔄 Fazendo download do áudio...")
        
        try:
            caminho = pasta_destino / f"{nome_arquivo}.%(ext)s"
            
            opcoes = {
                "format": Config.QUALIDADE_AUDIO,
                "outtmpl": str(caminho),
                "postprocessors": [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': Config.FORMATO_AUDIO,
                    'preferredquality': Config.BITRATE_AUDIO,
                }],
                "prefer_ffmpeg": True,
            }
            
            with YoutubeDL(opcoes) as ydl:
                ydl.download([url])
            
            print(f"✅ Áudio salvo: {nome_arquivo}.{Config.FORMATO_AUDIO}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no download do áudio: {e}")
            return False

class MetadataManager:
    """Classe responsável por gerenciar metadados"""
    
    def salvar(self, dados_video: dict, campanha: str, episodio: str, 
              pasta_destino: Path, nome_arquivo: str, url_original: str) -> bool:
        """
        Salva metadados em arquivo JSON
        
        Args:
            dados_video (dict): Informações do vídeo
            campanha (str): Nome da campanha
            episodio (str): Número do episódio
            pasta_destino (Path): Pasta de destino
            nome_arquivo (str): Nome base do arquivo
            url_original (str): URL original do vídeo
        
        Returns:
            bool: True se sucesso
        """
        print("🔄 Salvando metadados...")
        
        try:
            data_extracao = datetime.now().strftime("%Y%m%d")
            
            metadados = {
                "campanha": campanha,
                "episodio": episodio,
                "data_extracao": data_extracao,
                "titulo": dados_video['titulo'],
                "video_id": dados_video['video_id'],
                "data_upload": dados_video['data_upload'],
                "canal": dados_video['canal'],
                "duracao_segundos": dados_video['duracao'],
                "visualizacoes": dados_video['visualizacoes'],
                "likes": dados_video['likes'],
                "url_original": url_original,
                "arquivos_gerados": {
                    "video": f"{nome_arquivo}.mp4",
                    "audio": f"{nome_arquivo}.{Config.FORMATO_AUDIO}",
                    "metadata": f"{nome_arquivo}.json"
                }
            }
            
            caminho = pasta_destino / f"{nome_arquivo}.json"
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(metadados, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Metadados salvos: {nome_arquivo}.json")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar metadados: {e}")
            return False

class RPGDownloader:
    """Classe principal que coordena todo o processo de download"""
    
    def __init__(self):
        self.detector_campanha = CampanhaDetector()
        self.manager_episodio = EpisodioManager()
        self.gerador_nomes = FileNameGenerator()
        self.extrator_info = VideoInfoExtractor()
        self.downloader = Downloader()
        self.manager_metadata = MetadataManager()
    
    def criar_estrutura_pastas(self, campanha: str) -> tuple:
        """
        Cria estrutura de pastas para a campanha na camada raw.
        
        Args:
            campanha (str): Nome da campanha
        
        Returns:
            tuple: (pasta_videos, pasta_audio, pasta_metadata)
        """
        pasta_campanha = Config.BASE_DIR / campanha
        pasta_videos = pasta_campanha / "videos"
        pasta_audio = pasta_campanha / "audio"
        pasta_metadata = pasta_campanha / "metadata"
        
        for pasta in [pasta_videos, pasta_audio, pasta_metadata]:
            pasta.mkdir(parents=True, exist_ok=True)
        
        return pasta_videos, pasta_audio, pasta_metadata
    
    def processar_video(self, url: str) -> dict:
        """
        Processa um vídeo completo (download + metadados)
        
        Args:
            url (str): URL do vídeo
        
        Returns:
            dict: Resultado do processamento
        """
        print("🚀 Iniciando processamento do vídeo...")
        print("="*60)
        
        # 1. Extrair informações
        dados_video = self.extrator_info.extrair(url)
        
        # 2. Detectar campanha
        campanha = self.detector_campanha.detectar(url, dados_video['titulo'])
        print(f"🎯 Campanha: {campanha}")
        
        # 3. Criar estrutura de pastas
        pasta_videos, pasta_audio, pasta_metadata = self.criar_estrutura_pastas(campanha)
        
        # 4. Descobrir próximo episódio
        episodio = self.manager_episodio.descobrir_proximo(Config.BASE_DIR / campanha)
        print(f"📍 Episódio: {episodio}")
        
        # 5. Gerar nome do arquivo
        nome_arquivo = self.gerador_nomes.criar_nome(episodio, dados_video['video_id'])
        print(f"📝 Nome: {nome_arquivo}")
        
        # 6. Fazer downloads
        sucesso_video = self.downloader.baixar_video(url, pasta_videos, nome_arquivo)
        sucesso_audio = self.downloader.baixar_audio(url, pasta_audio, nome_arquivo)
        sucesso_metadata = self.manager_metadata.salvar(
            dados_video, campanha, episodio, pasta_metadata, nome_arquivo, url
        )
        
        # 7. Retornar resultado
        resultado = {
            'sucesso': sucesso_video and sucesso_audio and sucesso_metadata,
            'campanha': campanha,
            'episodio': episodio,
            'nome_arquivo': nome_arquivo,
            'dados_video': dados_video,
            'arquivos_criados': {
                'video': sucesso_video,
                'audio': sucesso_audio,
                'metadata': sucesso_metadata
            }
        }
        
        return resultado
    
    def mostrar_resumo(self, resultado: dict):
        """Mostra resumo do processamento"""
        if resultado['sucesso']:
            print("\n🎉 Processamento concluído com sucesso!")
        else:
            print("\n⚠️ Processamento concluído com alguns erros.")
        
        print(f"\n📊 RESUMO:")
        print(f"   📂 Campanha: {resultado['campanha']}")
        print(f"   📍 Episódio: {resultado['episodio']}")
        print(f"   📝 Nome: {resultado['nome_arquivo']}")
        print(f"   📺 Título: {resultado['dados_video']['titulo']}")
        
        print(f"\n📁 Status dos arquivos:")
        for tipo, sucesso in resultado['arquivos_criados'].items():
            status = "✅" if sucesso else "❌"
            print(f"   {status} {tipo.capitalize()}")
        print("="*60)