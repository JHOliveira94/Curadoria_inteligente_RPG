#!/usr/bin/env python3
"""
Script para inserir dados da camada Gold no PostgreSQL
Projeto: Curadoria Inteligente de RPG de Mesa
"""

import psycopg2
import json
from pathlib import Path
import logging
import re
from datetime import datetime

# ========================================
# CONFIGURAÇÕES
# ========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração do banco
DB_CONFIG = {
    'host': 'rpg_postgres',  # Nome do container (rodando dentro do Docker)
    'port': 5432,
    'database': 'rpgdados',
    'user': 'rpg_user',
    'password': 'strongpassword'
}

# Diretórios - Fabula Ultima
DIRETORIO_GOLD = "data/gold/fabula_ultima/enriquecido"
DIRETORIO_BRONZE = "data/raw/fabula_ultima/metadata"

# Nome da campanha
NOME_CAMPANHA = "fabula_ultima"

# ========================================
# FUNÇÕES
# ========================================

def conectar_postgres():
    """Conecta ao PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conectado ao PostgreSQL")
        return conn
    except Exception as e:
        logger.error(f"❌ Erro ao conectar: {e}")
        raise

def extrair_info_arquivo(nome_arquivo):
    """
    Extrai informações do nome do arquivo Gold
    Exemplo: ep01_f-tmb-Tcn_k_enriquecido.txt
    Retorna: {'episodio': 'ep01', 'video_id': 'f-tmb-Tcn_k'}
    """
    nome = Path(nome_arquivo).stem
    
    # Remover sufixos conhecidos
    nome = re.sub(r'_(enriquecido|analise_gold)$', '', nome)
    
    # Extrair episódio (ep01, ep02, etc)
    match_ep = re.search(r'(ep\d+)', nome, re.IGNORECASE)
    episodio = match_ep.group(1) if match_ep else None
    
    # Extrair video_id (tudo depois do episódio)
    if episodio:
        video_id = nome.replace(f"{episodio}_", "")
    else:
        video_id = nome
    
    return {
        'episodio': episodio,
        'video_id': video_id
    }

def ler_metadata_bronze(diretorio_bronze, video_id):
    """
    Lê arquivo JSON de metadata da camada Bronze
    Retorna dict com metadata ou None se não encontrar
    """
    # Tentar diferentes padrões de nome
    padroes = [
        f"{video_id}.json",
        f"{video_id}_metadata.json",
        f"metadata_{video_id}.json"
    ]
    
    for padrao in padroes:
        metadata_path = Path(diretorio_bronze) / padrao
        if metadata_path.exists():
            logger.info(f"📄 Metadata encontrado: {metadata_path.name}")
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    logger.warning(f"⚠️  Metadata não encontrado para video_id: {video_id}")
    return None

def inserir_ou_obter_campanha(cursor, nome_campanha):
    """Insere campanha ou retorna ID se já existir"""
    cursor.execute(
        """
        INSERT INTO campanhas (nome)
        VALUES (%s)
        ON CONFLICT (nome) DO NOTHING
        RETURNING id
        """,
        (nome_campanha,)
    )
    
    result = cursor.fetchone()
    if result:
        campanha_id = result[0]
        logger.info(f"📁 Nova campanha criada: {nome_campanha} (ID: {campanha_id})")
    else:
        # Campanha já existe, buscar ID
        cursor.execute("SELECT id FROM campanhas WHERE nome = %s", (nome_campanha,))
        campanha_id = cursor.fetchone()[0]
        logger.info(f"📁 Campanha existente: {nome_campanha} (ID: {campanha_id})")
    
    return campanha_id

def inserir_ou_atualizar_episodio(cursor, campanha_id, episodio_info, metadata):
    """Insere ou atualiza episódio com dados do metadata"""
    
    # Preparar dados do metadata (se existir)
    if metadata:
        titulo = metadata.get('titulo')
        data_extracao = metadata.get('data_extracao')
        data_upload = metadata.get('data_upload')
        canal = metadata.get('canal')
        duracao_segundos = metadata.get('duracao_segundos')
        visualizacoes = metadata.get('visualizacoes')
        likes = metadata.get('likes')
        url_original = metadata.get('url_original')
    else:
        titulo = None
        data_extracao = data_upload = canal = None
        duracao_segundos = visualizacoes = likes = None
        url_original = None
    
    cursor.execute(
        """
        INSERT INTO episodios 
        (campanha_id, numero_episodio, video_id, titulo, data_extracao, 
         data_upload, canal, duracao_segundos, visualizacoes, likes, url_original)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (campanha_id, numero_episodio) 
        DO UPDATE SET
            video_id = EXCLUDED.video_id,
            titulo = EXCLUDED.titulo,
            data_extracao = EXCLUDED.data_extracao,
            data_upload = EXCLUDED.data_upload,
            canal = EXCLUDED.canal,
            duracao_segundos = EXCLUDED.duracao_segundos,
            visualizacoes = EXCLUDED.visualizacoes,
            likes = EXCLUDED.likes,
            url_original = EXCLUDED.url_original
        RETURNING id
        """,
        (campanha_id, episodio_info['episodio'], episodio_info['video_id'],
         titulo, data_extracao, data_upload, canal, duracao_segundos,
         visualizacoes, likes, url_original)
    )
    
    episodio_id = cursor.fetchone()[0]
    logger.info(f"📺 Episódio: {episodio_info['episodio']} (ID: {episodio_id})")
    return episodio_id

def processar_arquivo_gold(arquivo_path):
    """
    Processa arquivo Gold e retorna lista de transcrições
    Formato esperado: NUM|INICIO|FIM|EMOÇÃO|SCORE|TEXTO
    """
    transcricoes = []
    
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    # Detectar cabeçalho automaticamente
    linha_inicio = 0
    for i, linha in enumerate(linhas):
        if linha.strip().startswith('#'):
            linha_inicio = i + 1
        else:
            break
    
    logger.info(f"📊 Processando a partir da linha {linha_inicio + 1}")
    
    # Processar linhas de dados
    for num_linha, linha in enumerate(linhas[linha_inicio:], start=linha_inicio + 1):
        linha = linha.strip()
        if not linha:
            continue
        
        # Parse: NUM|INICIO|FIM|EMOÇÃO|SCORE|TEXTO
        partes = linha.split('|', 5)  # máximo 6 partes
        
        if len(partes) < 6:
            logger.warning(f"⚠️  Linha {num_linha} ignorada (formato inválido): {linha[:50]}...")
            continue
        
        try:
            transcricoes.append({
                'numero': int(partes[0]),
                'inicio': partes[1],
                'fim': partes[2],
                'emocao': partes[3],
                'score': float(partes[4]),
                'texto': partes[5]
            })
        except (ValueError, IndexError) as e:
            logger.warning(f"⚠️  Erro ao processar linha {num_linha}: {e}")
            continue
    
    logger.info(f"✅ {len(transcricoes)} transcrições extraídas")
    return transcricoes

def inserir_transcricoes(cursor, episodio_id, transcricoes):
    """Insere transcrições no banco"""
    
    # Limpar transcrições antigas do episódio (reprocessamento)
    cursor.execute("DELETE FROM transcricoes WHERE episodio_id = %s", (episodio_id,))
    deleted = cursor.rowcount
    if deleted > 0:
        logger.info(f"🗑️  {deleted} transcrições antigas removidas")
    
    # Inserir novas transcrições
    sucesso = 0
    for t in transcricoes:
        try:
            cursor.execute(
                """
                INSERT INTO transcricoes 
                (episodio_id, numero_segmento, timestamp_inicio, timestamp_fim,
                 emocao, score_relevancia, texto)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (episodio_id, t['numero'], t['inicio'], t['fim'],
                 t['emocao'], t['score'], t['texto'])
            )
            sucesso += 1
        except Exception as e:
            logger.error(f"❌ Erro ao inserir segmento {t['numero']}: {e}")
    
    logger.info(f"✅ {sucesso}/{len(transcricoes)} transcrições inseridas")

def processar_campanha(conn, nome_campanha, diretorio_gold, diretorio_bronze):
    """Processa todos os arquivos Gold de uma campanha"""
    cursor = conn.cursor()
    
    try:
        # 1. Inserir/obter campanha
        campanha_id = inserir_ou_obter_campanha(cursor, nome_campanha)
        
        # 2. Encontrar arquivos Gold
        gold_path = Path(diretorio_gold)
        if not gold_path.exists():
            logger.error(f"❌ Diretório não encontrado: {diretorio_gold}")
            return
        
        # Procurar arquivos com padrões comuns
        padroes = ["*_enriquecido.txt", "*_analise_gold.txt", "*.txt"]
        arquivos = []
        for padrao in padroes:
            arquivos.extend(gold_path.glob(padrao))
        
        # Remover duplicatas
        arquivos = list(set(arquivos))
        
        if not arquivos:
            logger.warning(f"⚠️  Nenhum arquivo encontrado em {diretorio_gold}")
            return
        
        logger.info(f"📂 Encontrados {len(arquivos)} arquivo(s)")
        
        for arquivo in arquivos:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Processando: {arquivo.name}")
            logger.info(f"{'='*60}")
            
            # 3. Extrair info do nome do arquivo
            episodio_info = extrair_info_arquivo(arquivo.name)
            
            if not episodio_info['episodio']:
                logger.warning(f"⚠️  Não foi possível extrair número do episódio de {arquivo.name}")
                logger.warning(f"    Pulando arquivo...")
                continue
            
            logger.info(f"📝 Episódio: {episodio_info['episodio']}")
            logger.info(f"🎬 Video ID: {episodio_info['video_id']}")
            
            # 4. Ler metadata da Bronze
            metadata = ler_metadata_bronze(diretorio_bronze, episodio_info['video_id'])
            
            # 5. Inserir/atualizar episódio
            episodio_id = inserir_ou_atualizar_episodio(
                cursor, campanha_id, episodio_info, metadata
            )
            
            # 6. Processar arquivo Gold
            transcricoes = processar_arquivo_gold(arquivo)
            
            if not transcricoes:
                logger.warning(f"⚠️  Nenhuma transcrição extraída de {arquivo.name}")
                continue
            
            # 7. Inserir transcrições
            inserir_transcricoes(cursor, episodio_id, transcricoes)
            
            # Commit após cada arquivo
            conn.commit()
            logger.info(f"✅ Arquivo {arquivo.name} processado com sucesso!\n")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🎉 Campanha '{nome_campanha}' processada com sucesso!")
        logger.info(f"{'='*60}\n")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Erro durante processamento: {e}")
        raise
    finally:
        cursor.close()

def exibir_estatisticas(conn, nome_campanha):
    """Exibe estatísticas da campanha processada"""
    cursor = conn.cursor()
    
    logger.info("\n" + "="*60)
    logger.info("📊 ESTATÍSTICAS DA IMPORTAÇÃO")
    logger.info("="*60)
    
    # Total de episódios
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM episodios e
        JOIN campanhas c ON e.campanha_id = c.id
        WHERE c.nome = %s
        """,
        (nome_campanha,)
    )
    total_episodios = cursor.fetchone()[0]
    logger.info(f"📺 Total de episódios: {total_episodios}")
    
    # Total de transcrições
    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM transcricoes t
        JOIN episodios e ON t.episodio_id = e.id
        JOIN campanhas c ON e.campanha_id = c.id
        WHERE c.nome = %s
        """,
        (nome_campanha,)
    )
    total_transcricoes = cursor.fetchone()[0]
    logger.info(f"📝 Total de transcrições: {total_transcricoes}")
    
    # Score médio
    cursor.execute(
        """
        SELECT ROUND(AVG(t.score_relevancia)::numeric, 3)
        FROM transcricoes t
        JOIN episodios e ON t.episodio_id = e.id
        JOIN campanhas c ON e.campanha_id = c.id
        WHERE c.nome = %s
        """,
        (nome_campanha,)
    )
    score_medio = cursor.fetchone()[0]
    logger.info(f"⭐ Score médio: {score_medio}")
    
    # Top 5 emoções
    cursor.execute(
        """
        SELECT t.emocao, COUNT(*) as qtd
        FROM transcricoes t
        JOIN episodios e ON t.episodio_id = e.id
        JOIN campanhas c ON e.campanha_id = c.id
        WHERE c.nome = %s
        GROUP BY t.emocao
        ORDER BY qtd DESC
        LIMIT 5
        """,
        (nome_campanha,)
    )
    emocoes = cursor.fetchall()
    logger.info("\n🎭 Top 5 emoções:")
    for emocao, qtd in emocoes:
        logger.info(f"   {emocao}: {qtd}")
    
    logger.info("="*60 + "\n")
    
    cursor.close()

# ========================================
# MAIN
# ========================================

def main():
    """Função principal"""
    
    logger.info("\n" + "="*60)
    logger.info("🚀 INICIANDO IMPORTAÇÃO GOLD → POSTGRESQL")
    logger.info("="*60 + "\n")
    
    logger.info(f"📁 Campanha: {NOME_CAMPANHA}")
    logger.info(f"📂 Diretório Gold: {DIRETORIO_GOLD}")
    logger.info(f"📂 Diretório Bronze: {DIRETORIO_BRONZE}\n")
    
    # Conectar ao banco
    conn = conectar_postgres()
    
    # Processar campanha
    processar_campanha(conn, NOME_CAMPANHA, DIRETORIO_GOLD, DIRETORIO_BRONZE)
    
    # Exibir estatísticas
    exibir_estatisticas(conn, NOME_CAMPANHA)
    
    # Fechar conexão
    conn.close()
    
    logger.info("✅ Processo concluído com sucesso!")
    logger.info("="*60 + "\n")

if __name__ == "__main__":
    main()