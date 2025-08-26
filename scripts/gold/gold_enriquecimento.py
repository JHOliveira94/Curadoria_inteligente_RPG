"""
PROJETO: CURADORIA DE SESSÕES DE RPG DE MESA

Analise de Sentimentos - Classes e Funções
Neste script, estão as classes e funções para realização da análsie de sentimentos a partir das transcrições
presentes na camada bronze.

===== RESULTADOS ESPERADOS =====
    Arquivo de texto .txt com estrutura NUM|INICIO|FIM|EMOÇÃO|SCORE|TEXTO
"""

# ===== IMPORTAÇÕES =====
# Bibliotecas necessárias para a etapa gold do pipeline

from pathlib import Path

# ===== CONFIGURAÇÕES GERAIS PARA O SCRIPT=====

class Config:
    """
    Configurações centralizadas do projeto.
        - Facilita mudanças no projeto
        - Facilita escalabilidade
        - Facilita correções   
    """
    dir_silver = Path("data/silver")
    base_dir_gold = Path("data/gold")
    
    # Palavras-chave para análise contextual e composição do cálculo do score de relevância
    PALAVRAS_CHAVE_RPG = {
        'combate': {
            'palavras': ['ataque', 'atacar', 'dano', 'vida', 'morrer', 'morte', 'batalha', 
                        'luta', 'lutar', 'briga', 'combate', 'golpe', 'acerto', 'crítico', 
                        'boss', 'chefe', 'inimigo', 'dragão', 'monstro'],
            'peso': 1.0
        },
        'drama': {
            'palavras': ['chorar', 'lágrimas', 'despedida', 'partir', 'adeus', 'triste', 
                        'tristeza', 'perda', 'lamento', 'sofrer', 'dor', 'angústia', 'saudade'],
            'peso': 1.0  
        },
        'revelacao': {
            'palavras': ['descobrir', 'segredo', 'verdade', 'revelar', 'mistério', 'oculto', 
                        'escondido', 'surpresa', 'inesperado', 'plot', 'twist'],
            'peso': 1.0
        },
        'vitoria': {
            'palavras': ['venceu', 'ganhou', 'sucesso', 'conseguiu', 'vitória', 'triunfo', 
                        'derrotou', 'superou', 'alcançou'],
            'peso': 1.0
        },
        'fracasso': {
            'palavras': ['falhou', 'errou', 'perdeu', 'fracasso', 'derrota', 'falha', 
                        'não conseguiu'],
            'peso': 1.0
        },
        'roleplay': {
            'palavras': ['personagem', 'interpretar', 'sentir', 'pensar', 'lembrar', 
                        'decidir', 'escolher'],
            'peso': 1.0
        },
        'mecanica': {
            'palavras': ['dado', 'dados', 'rolar', 'teste', 'rolagem', 'natural', 
                        'crítico', 'falha crítica'],
            'peso': 1.0
        }
    }

class EstruturaGold:
    """ 
    Estrutura de diretórios para a camada gold
        - Dá continuidade ao trabalho executado na camada silver
        - Automatiza a organização dos dados de acordo com a necessidade da camada atual
    """
    
    def listar_campanhas(self) -> list:
        """
        Detecta as campanhas já trabalhadas na camada silver.

        Returns:
            list: Lista dos nomes das campanhas
        """
        campanhas_trabalhadas = []
        
        for item in Config.dir_silver.iterdir():
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
        dict_dir_gold = {}
        
        for campanha in campanhas:
            dir_campanha = Config.base_dir_gold / campanha / "enriquecido"
            dir_campanha.mkdir(parents=True, exist_ok=True)
            
            dict_dir_gold[campanha] = dir_campanha
            print(f"✅ Criado diretório Gold para {campanha} com sucesso!")
        
        return dict_dir_gold

class CalculadorScore:
    """
    Classe com as configurações necessárias para cálculo do score de relevância.
        - Calcula diferentes parâmetros que compõem o score:
            - Densidade emocional
            - Transcrições dramáticas
            - Duração das emoções
            - Palavras-chave
    """
    
    def __init__(self):
        self.segmentos = []
        self.emocoes_unicas_arquivo = set()
    
    def carregar_dados_silver(self, arquivo_silver):
        """
        Carrega os dados da análise de sentimentos  da camada silver. 
        """
        self.segmentos = []
        
        with open(arquivo_silver, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        for linha in linhas:
            partes = linha.strip().split('|')
            if len(partes) >= 5:
                segmento = {
                    'numero': partes[0],
                    'inicio': float(partes[1]),
                    'fim': float(partes[2]),
                    'emocao': partes[3],
                    'texto': partes[4],
                    'score_densidade': 0.0,
                    'score_transicao': 0.0,
                    'score_duracao': 0.0,
                    'score_palavras': 0.0,
                    'score_final': 0.0
                }
                self.segmentos.append(segmento)
        
        # Descobrir emoções únicas do arquivo
        self.emocoes_unicas_arquivo = set(seg['emocao'] for seg in self.segmentos)
        print(f"📊 Carregados {len(self.segmentos)} segmentos com {len(self.emocoes_unicas_arquivo)} emoções únicas")
    
    def calcular_densidade_emocional(self):
        """
        Calcula score de densidade emocional para cada segmento:
            - Define uma janela de análise em torno de cada segmento com base no número de emoções únicas em todo o arquivo.
            - Score: (quantidade de emoções únicas na janela analisada) / (total de emoções encontradas no arquivo)
            - Valor máximo possível: 1
        """
        tamanho_janela = len(self.emocoes_unicas_arquivo)
        total_emocoes = len(self.emocoes_unicas_arquivo)
        
        for i, segmento in enumerate(self.segmentos):
            # Definir janela ao redor do segmento atual
            inicio = max(0, i - tamanho_janela//2)
            fim = min(len(self.segmentos), i + tamanho_janela//2)
            
            # Emoções na janela
            emocoes_janela = set(seg['emocao'] for seg in self.segmentos[inicio:fim])
            
            # Score: quantas das emoções possíveis aparecem na janela
            score = len(emocoes_janela) / total_emocoes
            segmento['score_densidade'] = score
    
    def calcular_transicoes_dramaticas(self):
        """
        Calcula score binário bidirecional para transições emocionais em relação ao segmento analisado.
            - Valoriza mudanças emocionais
            - Binário pois ou pontua ou não pontua
            - Bidirecional pois analisa os segmentos anterior e o posterior ao que está em estudo
            - Score: +0.5 para cada transição emocinal
            - Score máximo possível: 1
        """
        for i, segmento in enumerate(self.segmentos):
            score = 0.0
            
            # Verificar mudança com anterior
            if i > 0 and self.segmentos[i-1]['emocao'] != segmento['emocao']:
                score += 0.5
            
            # Verificar mudança com próximo
            if i < len(self.segmentos)-1 and segmento['emocao'] != self.segmentos[i+1]['emocao']:
                score += 0.5
            
            segmento['score_transicao'] = score
    
    def calcular_duracao_emocoes(self):
        """
        Calcula score baseado na duração de sequências emocionais.
            - Valoriza constância das emoções
            - Os segmentos que mantêm a sequência das emoções recebem o mesmo score
            - Score máximo possível e teto definido: 1
                - Para o cálculo gerar esse valor, o número de segmentos considerados deve ser igual a 10
                - Fórmula: (duração -1) / 9
                    - duração => quantidade de segmentos com emoções repetidas em sequência
                    - -1 => Quando uma emoção aparece apenas em um segmento, não é relevante e deve ter score igual a zero
                    - 9 => pois é o maior valor relevante para o cálculo do score.
            - Exemplos:
                    1 segmento:  (1-1)/9  = 0/9  = 0.00  # Sem duração
                    2 segmentos: (2-1)/9  = 1/9  = 0.11  # Duração mínima
                    3 segmentos: (3-1)/9  = 2/9  = 0.22
                    4 segmentos: (4-1)/9  = 3/9  = 0.33
                    5 segmentos: (5-1)/9  = 4/9  = 0.44
                    6 segmentos: (6-1)/9  = 5/9  = 0.56  ← Seu exemplo
                    7 segmentos: (7-1)/9  = 6/9  = 0.67
                    8 segmentos: (8-1)/9  = 7/9  = 0.78
                    9 segmentos: (9-1)/9  = 8/9  = 0.89
                    10 segmentos: (10-1)/9 = 9/9  = 1.00  ← Score máximo
                    15 segmentos: (15-1)/9 = 14/9 = 1.56 → limitado a 1.0
        """
        i = 0
        while i < len(self.segmentos):
            emocao_atual = self.segmentos[i]['emocao']
            inicio_sequencia = i
            
            # Contar segmentos seguidos com a mesma emoção
            while i < len(self.segmentos) and self.segmentos[i]['emocao'] == emocao_atual:
                i += 1
            
            # Calcular duração da sequência
            duracao = i - inicio_sequencia
            
            # Score baseado na duração (linear com teto)
            if duracao == 1:
                score_duracao = 0.0
            else:
                score_duracao = min(1.0, (duracao - 1) / 9)
            
            # Aplicar score a todos os segmentos da sequência
            for j in range(inicio_sequencia, i):
                self.segmentos[j]['score_duracao'] = score_duracao
    
    def calcular_palavras_chave(self):
        """
        Calcula score baseado em palavras-chave relevantes presentes no segmento analisado.
            - Cada palavra definida em PALAVRAS_CHAVE_RPG pontuará +0.25
            - Considerando o tamanho dos segmentos transcritos, espera-se encontrar neles no máximo 4 palavras da lista PALAVRAS_CHAVE_RPG
            - Score: valor mínimo entre 1 e 0.25 por palavra
            - Score máximo possivel e teto: 1
        """
        for segmento in self.segmentos:
            texto = segmento['texto'].lower()
            score_total = 0.0
            
            for categoria, dados in Config.PALAVRAS_CHAVE_RPG.items():
                palavras = dados['palavras']
                peso = dados['peso']
                
                # Contar palavras encontradas
                palavras_encontradas = 0
                for palavra in palavras:
                    if palavra in texto:
                        palavras_encontradas += 1
                
                # Score da categoria
                if palavras_encontradas > 0:
                    score_categoria = min(1.0, palavras_encontradas * 0.25) * peso
                    score_total += score_categoria
            
            # Limitar score final a 1.0
            segmento['score_palavras'] = min(1.0, score_total)
    
    def calcular_score_final(self):
        """Combina todos os scores com os pesos definidos"""
        for segmento in self.segmentos:
            score_final = (
                segmento['score_densidade'] * 0.3 +
                segmento['score_transicao'] * 0.3 + 
                segmento['score_duracao'] * 0.3 +
                segmento['score_palavras'] * 0.1
            )
            segmento['score_final'] = round(score_final, 3)
    
    def processar_scores_completo(self):
        """Executa todos os cálculos de score"""
        print("🧮 Calculando densidade emocional...")
        self.calcular_densidade_emocional()
        
        print("🎭 Calculando transições dramáticas...")
        self.calcular_transicoes_dramaticas()
        
        print("⏳ Calculando duração de emoções...")
        self.calcular_duracao_emocoes()
        
        print("🔑 Calculando relevância por palavras-chave...")
        self.calcular_palavras_chave()
        
        print("🏆 Calculando scores finais...")
        self.calcular_score_final()

class ProcessadorGold:
    """
    Executa os cálculos definidos em CalculadoraScore.
    """
    def analises_por_campanha(self) -> dict:
        """
        Agrupa por campanha todas as análises das emoções feitas na camada silver.

        Returns:
            dict: Dicionário em que a chave é o nome da campanha e o valor é uma lista dos arquivos de suas transcrições analisadas.
        """
        campanhas = EstruturaGold().listar_campanhas()
        dict_analises_campanha = {}
        
        for campanha in campanhas:
            dir_analises = Config.dir_silver / campanha / "analise_sentimento"
            lista_analises = []
            
            for arquivo in dir_analises.iterdir():
                if arquivo.name.endswith("_analise_sentimento.txt"):
                    lista_analises.append(arquivo)
            
            dict_analises_campanha[campanha] = lista_analises
        
        return dict_analises_campanha
    
    def converter_timestamp_legivel(self, segundos):
        """Converte segundos para formato mm:ss ou h:mm:ss"""
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos_rest = int(segundos % 60)
        
        
        return f"{horas}:{minutos:02d}:{segundos_rest:02d}"
    
    def gerar_momentos_marcantes(self):
        """
        Gera novo arquivo com o score por relevância associado à cada segmento transcrito.
            - Estrutura do arquivo: NUM|INICIO|FIM|EMOÇÃO|SCORE|TEXTO
        """
        dict_analises_campanha = self.analises_por_campanha()
        dict_dir_gold = EstruturaGold().estruturar_diretorios()
        
        calculadora = CalculadorScore()
        
        # Para cada campanha
        for campanha, lista_analises in dict_analises_campanha.items():
            print(f"🏆 Processando momentos marcantes: {campanha}")
            
            pasta_destino = dict_dir_gold[campanha]
            
            # Para cada arquivo de análise
            for arquivo_analise in lista_analises:
                nome_base = arquivo_analise.stem.replace("_analise_sentimento", "")
                caminho_gold = pasta_destino / f"{nome_base}_enriquecido.txt"
                
                # Verificar se já foi processado
                if caminho_gold.exists():
                    print(f"⏭️ Pulando {arquivo_analise.name} - já processado")
                    continue
                
                print(f"🔄 Processando: {arquivo_analise.name}")
                
                # Carregar dados e calcular scores
                calculadora.carregar_dados_silver(arquivo_analise)
                calculadora.processar_scores_completo()
                
                # Salvar na ordem original (cronológica)
                with open(caminho_gold, 'w', encoding='utf-8') as f:
                    # Cabeçalho
                    f.write("# ANÁLISE GOLD - ORDEM CRONOLÓGICA\n")
                    f.write("# Formato: NUM|INICIO|FIM|EMOÇÃO|SCORE|TEXTO\n\n")
                    
                    for segmento in calculadora.segmentos:
                        inicio_legivel = self.converter_timestamp_legivel(segmento['inicio'])
                        fim_legivel = self.converter_timestamp_legivel(segmento['fim'])
                        
                        linha = (f"{segmento['numero']}|{inicio_legivel}|{fim_legivel}|"
                                f"{segmento['emocao']}|{segmento['score_final']}|{segmento['texto']}\n")
                        f.write(linha)
                
                print(f"✅ Gerado: {caminho_gold.name}")
    

class RPGGold:
    """Classe principal que coordena todo o processamento da camada Gold"""
    
    def __init__(self):
        self.estrutura = EstruturaGold()
        self.processador = ProcessadorGold()
    
    def gold_execução(self):
        """Executa todo o pipeline Gold"""
        print("🏆 Iniciando processamento Gold...")
        
        # 1. Criar estrutura
        print("📁 Criando estrutura de diretórios...")
        self.estrutura.estruturar_diretorios()
        
        # 2. Gerar momentos marcantes
        print("⭐ Gerando momentos marcantes...")
        self.processador.gerar_momentos_marcantes()
        
        print("✅ Processamento Gold concluído!")
        print("🎯 Scores de relevância calculados e mantidos em ordem cronológica!")