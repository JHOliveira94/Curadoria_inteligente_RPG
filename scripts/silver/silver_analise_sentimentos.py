"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Analise de Sentimentos - Classes e Funções
Neste script, estão as classes e funções para realização da análsie de sentimentos a partir das transcrições
presentes na camada bronze.

===== RESULTADOS ESPERADOS =====
    Arquivo de texto .txt com estrutura: NUM|INICIO|FIM|EMOÇÃO|TEXTO
"""

# ===== IMPORTAÇÕES =====
# Bibliotecas necessárias para a etapa silver do pipeline

from pathlib import Path
from feel_it import EmotionClassifier # Modelo de NLP para detecção de emoções (joy, sadness, anger, fear) para análise de momentos marcantes
import torch # Dependência necessária para execução do Feel-it. Framework de deep learning que fornece estruturas matemáticas para modelos de IA 

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


# ===== CONFIGURAÇÕES GERAIS PARA O SCRIPT=====

class Config:
    """
    Configurações centralizadas do projeto.
        - Facilita mudanças no projeto
        - Facilita escalabilidade
        - Facilita correções   
    """

    dir_bronze = Path("data/bronze")
    base_dir_silver = Path("data/silver")
        

class EstruturaSilver:
    """ 
    Estrutura de diretórios para a camada silver 
        - Dá continuidade ao trabalho executado na camada bronze
        - Automatiza a organização dos dados de acordo com a necessidade da camada atual
    """
    def listar_campanhas(self) -> list:
        """
        Detecta as campanhas já trabalhadas na camada bronze.

        Returns:
            list: Lista dos nomes das campanhas
        """
        
        campanhas_trabalhadas = []

        for item in Config.dir_bronze.iterdir():
            if item.is_dir():
                campanhas_trabalhadas.append(item.name)

        return campanhas_trabalhadas
    
    def estruturar_diretorios(self) -> dict:
        """
        Cria estrutura de diretórios para essa etapa do projeto.
        
        Returns:
            dict: Dicionário em que a chave é o nome da campanha e o valor o caminho para o diretório. 
        """

        campanhas = self.listar_campanhas()
        dict_dir_analise_sentimento = {}

        for campanha in campanhas:
            dir_campanha = Config.base_dir_silver / campanha / "analise_sentimento"
            dir_campanha.mkdir(parents=True, exist_ok=True)
            
            dict_dir_analise_sentimento[campanha] = dir_campanha

            print(f"✅ Criado diretório para análise de sentimentos de {campanha} com sucesso!")
        
        return dict_dir_analise_sentimento

class Analisador:
    """
    Classe responsável pela análise das trancições segmentadas dos epsódios.
        - Automatiza a análise dos textos
        - Categoriza trechos de acordo com o sentimento identificado
        - Gera novo arquivo .txt em que há a emoção detectada ao lado da transcrição
    """

    def __init__(self):
        # Carregar modelo feel-it
        
        self.classificador = EmotionClassifier()
   
    def transcricao_por_campanha(self) -> dict:
        """
        Agrupa por campanha todas as transcrições presentes na camada bronze.

        Returns:
            dict: Dicionário em que a chave é o nome da campanha e o valor é uma lista dos arquivos de suas transcrições segmentadas.
        """
        campanhas = EstruturaSilver().listar_campanhas()
        dict_analise_sentimento_campanha = {}
        
        for campanha in campanhas:
            dir_transcricoes = Config.dir_bronze / campanha / "transcricoes"
            lista_analise_sentimento = []

            for arquivo in dir_transcricoes.iterdir():
                if arquivo.name.endswith("_segmentado.txt"):
                    lista_analise_sentimento.append(arquivo)
            
            dict_analise_sentimento_campanha[campanha] = lista_analise_sentimento
        
        return dict_analise_sentimento_campanha

    def analise_de_sentimento(self):
        """
        Execução da análise dos textos e categoriação segundo o modelo NLP feel-it.
        Retorna arquivo .txt com a emoção associada à frase transcrita.
        """
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

                # Nome do arquivo de saída
                nome_base = arquivo_transcricao.stem.replace("_segmentado", "")
                caminho_analise = pasta_destino / f"{nome_base}_analise_sentimento.txt"
                
                # Verificar se já foi processado
                if caminho_analise.exists():
                    print(f"⏭️ Pulando {arquivo_transcricao.name} - já analisado")
                    continue
                
                print(f"📝 Processando: {arquivo_transcricao.name}")


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
                        resultado = self.classificador.predict([texto]) # Aplica 
                        emocao = resultado[0]
                        
                        # Criar nova linha: "001|000.00|003.45|joy|Texto"
                        nova_linha = f"{num}|{inicio}|{fim}|{emocao}|{texto}\n"
                        linhas_analisadas.append(nova_linha)
                

                
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