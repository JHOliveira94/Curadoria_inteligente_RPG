from pathlib import Path
from feel_it import EmotionClassifier
import torch

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class Config:

    dir_bronze = Path("data/bronze")
    base_dir_silver = Path("data/silver")
        

class EstruturaSilver:
    
    def listar_campanhas(self) -> list:
        
        campanhas_trabalhadas = []

        for item in Config.dir_bronze.iterdir():
            if item.is_dir():
                campanhas_trabalhadas.append(item.name)

        return campanhas_trabalhadas
    
    def estruturar_diretorios(self) -> dict:
        campanhas = self.listar_campanhas()
        dict_dir_analise_sentimento = {}

        for campanha in campanhas:
            dir_campanha = Config.base_dir_silver / campanha / "analise_sentimento"
            dir_campanha.mkdir(parents=True, exist_ok=True)
            
            dict_dir_analise_sentimento[campanha] = dir_campanha

            print(f"✅ Criado diretório para análise de sentimentos de {campanha} com sucesso!")
        
        return dict_dir_analise_sentimento

class Analisador:

    def __init__(self):
        # Carregar modelo feel-it
        
        self.classificador = EmotionClassifier()

    def transcricao_por_campanha(self) -> dict:
    
        campanhas = EstruturaSilver().listar_campanhas()
        dict_transcricoes_campanha = {}
        
        
        for campanha in campanhas:
            dir_transcricoes = Config.dir_bronze / campanha / "transcricoes"
            lista_transcricoes = []

            for arquivo in dir_transcricoes.iterdir():
                if arquivo.name.endswith("completo.txt"):
                    lista_transcricoes.append(arquivo)
            
            dict_transcricoes_campanha[campanha] = lista_transcricoes
        
        return dict_transcricoes_campanha
    
    def transcricao_por_campanha(self) -> dict:
        campanhas = EstruturaSilver().listar_campanhas()
        dict_analise_sentimento_campanha = {}
        
        for campanha in campanhas:
            dir_transcricoes = Config.dir_bronze / campanha / "transcricoes"
            lista_analise_sentimento = []

            for arquivo in dir_transcricoes.iterdir():
                if arquivo.name.endswith("_segmentado.txt"):  # ← Mudança aqui
                    lista_analise_sentimento.append(arquivo)
            
            dict_analise_sentimento_campanha[campanha] = lista_analise_sentimento
        
        return dict_analise_sentimento_campanha

    def analise_de_sentimento(self):
        dict_transcricoes_campanha = self.transcricao_por_campanha()
        dict_dir_analise_sentimento = EstruturaSilver().estruturar_diretorios()

        # Para cada campanha:
        for campanha, lista_transcricoes in dict_transcricoes_campanha.items():
            print(f"🔄 Analisando sentimentos: {campanha}")
            
            pasta_destino = dict_dir_analise_sentimento[campanha]

            # Para cada arquivo de transcrição segmentado:
            for arquivo_transcricao in lista_transcricoes:
                print(f"📝 Processando: {arquivo_transcricao.name}")
                
                # Ler linhas do arquivo segmentado
                with open(arquivo_transcricao, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                
                # Processar cada linha (segmento)
                linhas_analisadas = []
                total_segmentos = len(linhas)
                
                for i, linha in enumerate(linhas, 1):
                    # Mostrar progresso a cada 100 segmentos
                    if i % 100 == 0 or i == total_segmentos:
                        print(f"   📊 Processando segmento {i}/{total_segmentos}")
                    
                    # Dividir linha: "001|000.00|003.45|Texto do segmento"
                    partes = linha.strip().split('|')
                    
                    if len(partes) >= 4:
                        num = partes[0]
                        inicio = partes[1]
                        fim = partes[2]
                        texto = partes[3]
                        
                        # Analisar sentimento
                        resultado = self.classificador.predict([texto])
                        emocao = resultado[0]
                        
                        # Criar nova linha: "001|000.00|003.45|joy|Texto"
                        nova_linha = f"{num}|{inicio}|{fim}|{emocao}|{texto}\n"
                        linhas_analisadas.append(nova_linha)
                
                # Nome do arquivo de saída
                nome_base = arquivo_transcricao.stem.replace("_segmentado", "")
                caminho_analise = pasta_destino / f"{nome_base}_analise_sentimento.txt"
                
                # Salvar arquivo com análises
                with open(caminho_analise, 'w', encoding='utf-8') as f:
                    f.writelines(linhas_analisadas)
                
                print(f"✅ Análise concluída: {len(linhas_analisadas)} segmentos processados")
                print(f"💾 Salvo: {caminho_analise.name}")

class RPGAnaliseSentimento:
    """Classe principal que coordena todo o processamento da camada Silver"""
    
    def __init__(self):
        self.estrutura = EstruturaSilver()
        self.analisador_sentimento = Analisador()
    
    def silver_execução(self):
        """Executa todo o pipeline bronze"""
        print("🚀 Iniciando processamento Silver...")
        
        # 1. Criar estrutura
        print("📁 Criando estrutura de diretórios...")
        self.estrutura.estruturar_diretorios()
        
        # 2. Transcrever tudo
        print("🎵 Iniciando análise de sentimentos...")
        self.analisador_sentimento.analise_de_sentimento()
        
        print("✅ Processamento Silver concluído!")