from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import threading
import queue
import regex as re
from time import sleep, time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] (%(threadName)s) %(message)s"
)

# Filas
link_queue = queue.Queue()
coletar_queue = queue.Queue()

# Listas finais
pessoas_url = []
nao_pessoas_url = []

# Regex dos links válidos
padrao_regex = re.compile(r"^/wiki/(?!.*[:()\[\]0-9.!])(.*_.*)$")
wikipedia_base_url = 'https://pt.wikipedia.org'

# Limite de pessoas a coletar
LIMITE_PESSOAS = 120

# Probabilidade de ser pessoa
PROB_PESSOA = 0.6

# Lock para manipulação segura de threads
pessoas_lock = threading.Lock()
def baixar_html(url, tentativas=3, delay=1.5):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }

    for i in range(tentativas):
        try:
            sleep(delay)
            req = Request(url, headers=headers)   # define o User-Agent
            with urlopen(req) as resp:
                return resp.read()
        except Exception as e:
            logging.warning(f"[Erro ao requisitar] {url} (tentativa {i+1}/{tentativas}): {e}")
            sleep(delay * 2)
    return None


def eh_pessoa(url):
    """Verifica se a URL corresponde a uma pessoa"""
    site = baixar_html(url, delay=1)  # espera 1.5s entre cada request
    if not site:
        return False

    soup = BeautifulSoup(site, 'html.parser')

    infobox = soup.find("table", class_=re.compile("^[iI]nfobox"))
    if not infobox:
        return False

    # atributos = infobox.find_all('td', {'scope': "row"})
    atributos = infobox.text.lower().split('\n')
    atributos = list(filter(lambda x: x != '', atributos))
    prob = 0
    for at in atributos:
        if re.search(r"[Nn]ome\b", at):
            prob += 1
        if re.search(r"[Nn]ascimento\b|[Dd]ata de [Nn]ascimento\b|[Mm]orte\b", at):
            prob += 1
        if re.search(r"[Nn]acionalidade\b|[Cc]idadania\b", at):
            prob += 1
        if re.search(r"[Aa]ssinatura\b", at):
            prob += 1
        if re.search(r"[Pp]rofissão\b|[Oo]cupação\b", at):
            prob += 1
        if re.search(r"[Ee]sposa\b|[Cc]ônjugue\b", at):
            prob += 1

    # prob_ajustada = (prob - 0) / (6 - 0)
    prob_ajustada = prob / 5

    return prob_ajustada


def find_url(url):

    site = baixar_html(url, delay=1)
    if not site:
        return

    soup = BeautifulSoup(site, "html.parser")

    todos_os_links_tags = soup.find_all('a', href=re.compile(r'^/wiki/'))
    todos_os_hrefs = {tag['href'] for tag in todos_os_links_tags}

    links_mantidos_hrefs = {href for href in todos_os_hrefs if padrao_regex.match(href)}
    links_to_search = [f'{wikipedia_base_url}{link}' for link in links_mantidos_hrefs]

    for link in links_to_search:
        logging.debug(f"[Produtor] Link coletado: {link}")
        link_queue.put(link)


def classificador():
    """Classificador: classifica links como pessoa ou não pessoa"""
    global pessoas_url

    while True:
        try:
            link = link_queue.get(timeout=20)
        except queue.Empty:
            logging.info("[Classificador] Terminou")
            break


        with pessoas_lock:
            if len(pessoas_url) >= LIMITE_PESSOAS:
                logging.info("[Classificador] Limite atingido")
                link_queue.task_done()
                break

        # Print para acompanhar quantas pessoas já foram classificadas
        print(f">> QUANTIDADE DE PESSOAS CLASSIFICADAS: {len(pessoas_url)}")

        prob_pessoa = eh_pessoa(link)  
        if  prob_pessoa >= PROB_PESSOA:
            with pessoas_lock:
                pessoas_url.append(link)
                logging.info(f"Classificado como PESSOA: {link}, {prob_pessoa}")

                # Salva em arquivo
                with open("pessoas_encontradas.txt", "a", encoding="utf-8") as f:
                    f.write(link + "\n")

        else:
            logging.warning(f"[Classificador]--> NÃO PESSOA: {link}, {prob_pessoa}")
            nao_pessoas_url.append(link)
            coletar_queue.put(link)

        link_queue.task_done()


def coletor():
    """Coleta os links de páginas não pessoa para coletar mais links"""
    while True:
        try:
            link = coletar_queue.get(timeout=30)
            with pessoas_lock:
                if len(pessoas_url) >= LIMITE_PESSOAS:
                    logging.info("[Coletor] Limite atingido")
                    link.task_done()
                    break

        except queue.Empty:
            logging.info("[Coletor] Terminou")
            break

        logging.info(f"[Coletor] Coletando: {link}")
        find_url(link)
        coletar_queue.task_done()


if __name__ == "__main__":
    inicio = time()
    url_inicial = "https://pt.wikipedia.org/"

    # coloca a url inicial na fila de exploração
    coletar_queue.put(url_inicial)

    # Threads consumidoras (classificação)
    classificadores = [threading.Thread(target=classificador, name=f"Classificador-{i}") for i in range(3)]
    for t in classificadores:
        t.start()

    # coletor busca links novos em não pessoas
    explorador_thread = threading.Thread(target=coletor, name="Coletor")
    explorador_thread.start()


    for c in classificadores:
        c.join()
    explorador_thread.join()

    final = time()

    logging.info("\n=== Resultados finais ===")
    logging.info(f"Pessoas encontradas: {len(pessoas_url)}")
    logging.info(f"Não pessoas: {len(nao_pessoas_url)}")
    logging.info(f"Tempo total: {final - inicio}")