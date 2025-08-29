import asyncio
import aiohttp
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup
import regex as re
from time import time
from dataclasses import dataclass, field
import logging
import os
import aiofiles
import unicodedata

# config
URL_INICIAL = "https://pt.wikipedia.org/wiki/Marie_Curie"
LIMITE_PESSOAS = 50
MAX_CONEXOES = 50
PROB_PESSOA = 0.6
TIMEOUT_GERAL = 10
PASTA_HTML = "paginas_html"



@dataclass
class LinkNode:
    url: str
    prob: float
    pai: 'LinkNode' = None
    filhos: list = field(default_factory=list)


fila_processamento = asyncio.Queue()
pessoas_encontradas = []
lock = asyncio.Lock()
inicio_tempo = time()
links_verificados_contador = 0
requisicoes_http_contador = 0
palavras_a_excluir = []


# logs bonitos
class ColorFormatter(logging.Formatter):
    COLORS = {"INFO": "\033[32m", "WARNING": "\033[33m", "ERROR": "\033[31m", "DEBUG": "\033[34m", "RESET": "\033[0m"}

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, self.COLORS['RESET'])}{log_message}{self.COLORS['RESET']}"


handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("[%(levelname)s] (%(asctime)s) %(message)s", "%H:%M:%S"))
logging.basicConfig(level=logging.INFO, handlers=[handler])


def normalizar(texto: str) -> str:
    try:
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    except (TypeError, AttributeError):
        return ""
    return texto.lower()


async def baixar_html(session: aiohttp.ClientSession, url: str) -> str | None:
    if session.closed:
        return None
    global requisicoes_http_contador
    async with lock:
        requisicoes_http_contador += 1
    try:
        timeout = ClientTimeout(total=TIMEOUT_GERAL)
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(url, timeout=timeout, headers=headers) as response:
            if response.status == 200: return await response.text()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Erro ao baixar {url}: {e}")
    return None


async def salvar_html(nome_arquivo: str, html_content: str):
    caminho_completo = os.path.join(PASTA_HTML, f"{nome_arquivo}.html")
    try:
        async with aiofiles.open(caminho_completo, mode='w', encoding='utf-8') as f:
            await f.write(html_content)
    except Exception as e:
        logging.error(f"Falha ao salvar o arquivo {caminho_completo}: {e}")


def eh_pessoa(html: str) -> float:
    if not html: return 0.0
    soup = BeautifulSoup(html, 'lxml')
    infobox = soup.find("table", class_=re.compile("^[iI]nfobox"))
    if not infobox: return 0.0
    infobox_text = infobox.text.lower()
    prob = 0
    if "nascimento" in infobox_text or "morte" in infobox_text: prob += 2
    if "nome completo" in infobox_text: prob += 1
    if "nacionalidade" in infobox_text or "cidadania" in infobox_text: prob += 1
    if "profissão" in infobox_text or "ocupação" in infobox_text: prob += 1
    if "cônjuge" in infobox_text or "assinatura" in infobox_text: prob += 1
    return prob / 5


def extrair_links_validos(html: str, url_base: str) -> set[str]:
    soup = BeautifulSoup(html, 'lxml')
    padrao_artigo = re.compile(r"^/wiki/(?!.*[:()\[\]0-9.])[^:]+$")
    links_brutos = {a['href'] for a in soup.find_all('a', href=padrao_artigo)}
    links_limpos = set()
    for href in links_brutos:
        href_normalizado = normalizar(href)
        if not any(palavra in href_normalizado for palavra in palavras_a_excluir):
            links_limpos.add(f"{url_base}{href}")
    return links_limpos


def print_tree(node: LinkNode, nivel=0, max_niveis=3):
    if nivel > max_niveis:
        if node.filhos: print("  " * nivel + "...")
        return
    print("  " * nivel + f"-> {node.url} (Prob: {node.prob:.2f})")
    for filho in node.filhos:
        print_tree(filho, nivel + 1, max_niveis)



async def worker(name: str, session: aiohttp.ClientSession):
    while True:
        no_pai: LinkNode = await fila_processamento.get()
        try:
            html_pai = await baixar_html(session, no_pai.url)
            if not html_pai:
                continue

            links_filhos = extrair_links_validos(html_pai, "https://pt.wikipedia.org")
            for link_url in links_filhos:
                html_filho = await baixar_html(session, link_url)
                if not html_filho:
                    continue

                async with lock:
                    global links_verificados_contador
                    links_verificados_contador += 1

                prob = eh_pessoa(html_filho)
                if prob >= PROB_PESSOA:
                    async with lock:
                        if len(pessoas_encontradas) < LIMITE_PESSOAS and not any(
                                p.url == link_url for p in pessoas_encontradas):
                            nome_arquivo = link_url.split('/')[-1]
                            await salvar_html(nome_arquivo, html_filho)

                            novo_no = LinkNode(url=link_url, prob=prob, pai=no_pai)
                            no_pai.filhos.append(novo_no)
                            pessoas_encontradas.append(novo_no)
                            await fila_processamento.put(novo_no)

                            tempo = time() - inicio_tempo
                            logging.info(
                                f"PESSOA: {link_url} | Prob: {prob} | Total: {len(pessoas_encontradas)}/{LIMITE_PESSOAS} | Tempo: {tempo:.1f}s")
        finally:
            fila_processamento.task_done()


async def monitor_de_limite(tasks: list):
    while True:
        async with lock:
            if len(pessoas_encontradas) >= LIMITE_PESSOAS:
                logging.warning("Limite atingido! Cancelando tarefas e finalizando...")
                for task in tasks:
                    task.cancel()
                break
        await asyncio.sleep(0.1)


async def main():
    global palavras_a_excluir, inicio_tempo
    inicio_tempo = time()

    try:
        with open("data/palavras_para_excluir.txt", "r", encoding="utf-8") as f:
            palavras_a_excluir = [normalizar(line.strip()) for line in f if line.strip()]
        logging.info(f"{len(palavras_a_excluir)} palavras de exclusão carregadas.")
    except FileNotFoundError:
        logging.warning("Arquivo 'data/palavras_para_excluir.txt' não encontrado.")

    if not os.path.exists(PASTA_HTML):
        os.makedirs(PASTA_HTML)

    async with aiohttp.ClientSession() as session:
        html_inicial = await baixar_html(session, URL_INICIAL)
        if html_inicial:
            await salvar_html(URL_INICIAL.split('/')[-1], html_inicial)

        raiz = LinkNode(url=URL_INICIAL, prob=1.0)
        pessoas_encontradas.append(raiz)
        await fila_processamento.put(raiz)

        tasks = [asyncio.create_task(worker(f"Worker-{i + 1}", session)) for i in range(MAX_CONEXOES)]
        monitor = asyncio.create_task(monitor_de_limite(tasks))

        await asyncio.gather(*tasks, monitor, return_exceptions=True)

    tempo_total = time() - inicio_tempo
    total_pessoas = len(pessoas_encontradas)
    pessoas_por_segundo = total_pessoas / tempo_total if tempo_total > 0 else 0
    print("\n" + "=" * 50 + "\n" + " " * 17 + "RELATÓRIO FINAL" + "\n" + "=" * 50)
    print(f"{'Métrica':<25} | {'Valor'}")
    print("-" * 50)
    print(f"{'Tempo Total de Execução':<25} | {tempo_total:.2f} segundos")
    print(f"{'Total de Pessoas Encontradas':<25} | {total_pessoas}")
    print(f"{'Total de Links Verificados':<25} | {links_verificados_contador}")
    print(f"{'Total de Requisições HTTP':<25} | {requisicoes_http_contador}")
    print(f"{'Pessoas por Segundo':<25} | {pessoas_por_segundo:.2f}")
    print(f"{'HTMLs Salvos no Diretório':<25} | '{PASTA_HTML}/'")
    print("=" * 50)
    print("\nÁrvore de Pessoas Encontradas:")
    if 'raiz' in locals():
        print_tree(raiz)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("\ninterrompido pelo usuário.")
    except asyncio.CancelledError:
        logging.info("\nExecução cancelada.")
