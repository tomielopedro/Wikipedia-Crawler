def eh_pessoa(html: str) -> float:
    if not html:
        return 0.0
    soup = BeautifulSoup(html, 'lxml')
    infobox = soup.find("table", class_=re.compile("^[iI]nfobox"))
    if not infobox:
        eh_pessoa_tags(soup)
    infobox_text = infobox.text.lower()
    prob = 0
    if "nascimento" in infobox_text or "morte" in infobox_text: prob += 2
    if "nome completo" in infobox_text: prob += 1
    if "nacionalidade" in infobox_text or "cidadania" in infobox_text: prob += 1
    if "profissão" in infobox_text or "ocupação" in infobox_text: prob += 1
    if "cônjuge" in infobox_text or "assinatura" in infobox_text: prob += 1
    return prob / 6

def eh_pessoa_tags(soup) -> float:
    catlinks = soup.find("div", id="mw-normal-catlinks")
    if not catlinks:
        return 0.0
    infobox_text = catlinks.text.lower()
    prob = 0
    
    print(infobox_text)
    if "pessoas" in infobox_text or "vivas" in infobox_text: prob += 2
    if "mortos" in infobox_text: prob += 2
    if "naturais" in infobox_text or "nascidos" in infobox_text: prob += 2

    prob = prob/6
    print(prob)
    return prob / 6
