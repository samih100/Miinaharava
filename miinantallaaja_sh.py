'''Lopputehtävä, Miinantallaaja. Tekijänä Sami Hiltunen

Toiminnot ja vaatimukset:
- Käyttäjä antaa ruudukon koon.
- Käyttäjä antaa miinojen määrän.
- Käyttäjä klikkaa hiirella ruudun auki.
    -> Näytetään ruudun sisältö
    -> Jos miina, peli päättyy
    -> Jos ympärillä tyhjä, mutta sen vieressä miina, on ruutu numeroruutu,
        jossa näytetään ympäröitävien miinojen lukumäärä
    -> Jos ympärillä tyhjä, ja sen vieressä on tyhjä, niin aukaistaan ruutu ja
        tutkitaan sen ympärillä olevat ruudut niin pitkään kunnes vastaan tulee
        kentän raja tai ensimmäinen numeroruutu
- Tilastot tallennetaan tiedostoon
    -> Kysytään käyttäjältä minne tiedosto tallennetaan
    -> Tallennetaan: pelin ajankohta (päivämäärä + kellonaika),
        keston minuuteissa, keston vuoroissa ja
        lopputuloksen (voitto tai häviö, kentän koko ja miinojen lukumäärä)
- Valikko jossa voi valita
    -> Uusi peli, lopeta peli, katso tilastoja.

Ominaisuudet:
- Kenttä voi olla suorakulmio tai neliö.
- Ruututyypit: miinaruutu (x), numeroruutu (1-8), tyhjäruutu (" ")
- Peli päättyy kun osuu miinaan tai kun kaikki ei miinoietut ruudut on auki.

Tiedossa olevat defectit tai puutteet:
- Resoluution ja kenttäkoon tarkastus olisi hyvä olla olemassa.
    Nyt se puuttuu. Esim. 1378x768 resoluutiolla pystyyn mahtuu vain 17 ruutua.
    Vaakaan 50 ruutua. Virhettä ei tule, mutta pelamaan ei pysty.
- Pelin loppuessa Linux (lubuntu 22.04 LTS) ikkunan OK ei reagoi.
- Peli loppuessa peliruutu jää auki, jotta pelaaja voi tutkia pelikenttä.
    Pelin jatkopelmaaminen pitäisi kuitenkin estää.
'''

# Alustukset alkavat
import random
import time
from datetime import datetime
import ikkunasto
import haravasto

# Globaali koordinaatistolista johon merkitään realiaikainen pelitilanne.
pelitila = []

# Globaali parametri ja pelinaikainen tilannetaulu johon muut funktiot pääsevät kiinni.
PARAMETRIT = {
    "pelaaja": {
        "nimesi": '',
        "leveys": 0,
        "korkeus": 0,
        "miinojenlkm": 0,
        "x": 0,
        "y": 0,
        "siirrot": 0,
        "aloitusaika": 0.0,
        "lopetusaika": 0.0,
        "tulos": '',
        "pelipäivä": '',
        "tulostettu": 0,
        "autotallennus": False
    }
}

# Funktiot alkavat

def luo_pelikentta(korkeus, leveys):
    '''
    Miinaharavan kenttä. Korkeus ja leveys tulee käyttäjältä.
    '''
    pelikentta = []
    for rivi in range(korkeus):
        pelikentta.append([])
        for sarake in range(leveys):
            pelikentta[-1].append(" ")
    return pelikentta

def luo_vapaat_ruudut(korkeus, leveys):
    '''
    Funkio joka luo pelin alussa listan vapaista ruudista.
    '''
    # Väliaikainen lista, jotta saadaan miinat sijoitettua ruudulle.
    jaljella = []
    for x in range(leveys):
        for y in range(korkeus):
            jaljella.append((x, y))
    return jaljella

def miinoita(miina_kentta, vapaat_ruudut, miinojen_lkm):
    '''
    Asettaa kentälle N kpl miinoja satunnaisiin paikkoihin.
    '''
    for i in range(0, (miinojen_lkm)): # Tuotetaan tarvittava määrä miinoja.
        miina = random.choice(vapaat_ruudut) # Arvotaan vapaalta listalta yksi alkio.
        vapaat_ruudut.remove(miina) # Poistetaan arvottu miina vapaalta listalta.
        miinastr = str(miina)
        ei_sulkuja = miinastr.replace('(', '').replace(')', '')
        y, x = ei_sulkuja.split(',')
        miina_kentta[int(x)][int(y)] = "m" # Asetetaan miinakentälle miina merkki

def laske_miinat(lista, y, x):
    """
    Funktio tutkii alkion ympärillä olevat kentät ja laskee
    ympärillä olevien miinojen määrät ja palauttaa luvun.
    """
    miinat = 0
    miinakentan_korkeus = len(pelitila)
    miinakentan_leveys = len(pelitila[0])

    for rivi in range(-1, 2): # Käydään annetun vapaan ruutupisteen  ylä- ja alapuolet.
        for sarake in range(-1, 2): # Käydään annetun vapaan ruutupisteen vasen ja oikea puoli.
            if (rivi != 0 or sarake != 0) and \
                (x + rivi) > -1 and \
                (y + sarake) > -1 and \
                (x + rivi) < miinakentan_korkeus and \
                (y + sarake) < miinakentan_leveys: # Tarkastetaan lähtöpiste sekä reunat.
                    if lista[x + rivi][y + sarake] == "m": # Lasketaan miinat
                        miinat = miinat + 1

    #lista[x][y] = str(miinat) # Kirjoiteaan miinan määrä pelitilanne tauluun
    #return miinat
    return str(miinat)

def time_convert(sec): # https://www.codespeedy.com/how-to-create-a-stopwatch-in-python/
    '''
    Funktiota käytetään pelatun ajan esitysmuodon muotoiluun.
    '''
    mins = sec // 60
    sec = sec % 60
    hours = mins // 60
    mins = mins % 60
    return "{0:02d}:{1:02d}".format(int(mins), int(sec))
    #print("Time Lapsed = {0}:{1}:{2}".format(int(hours),int(mins),sec))

def kasittele_hiiri(x, y, painike, nappain):
    '''
    Tätä funktiota kutsutaan kun käyttäjä klikkaa sovellusikkunaa hiirellä.
    '''
    miinakentan_korkeus = len(pelitila) * 40 # Koordinaatiston korkeus pixeleinä.
    miinakentan_leveys = len(pelitila[0]) * 40 # Koordinaatiston leveys.
    x_ruutu = x // 40 # Muutetaan pixelit koordinaatti ruuduksi
    # Pyglit y-origo alkaa alhaalta ja tällä saadaan pixelikoordinaatti ruuduksi.
    y_ruutu = (miinakentan_korkeus - y) // 40
    PARAMETRIT["pelaaja"]["leveys"] = x_ruutu # Tallennetaan hiiren x-piste globaaliin muuttujaan.
    PARAMETRIT["pelaaja"]["korkeus"] = y_ruutu # Tallennetaan hiiren y-piste globaaliin muuttujaan.
    PARAMETRIT["pelaaja"]["siirrot"] += 1 # Lisätään siirtomäärä globaaliin muuttujaan.
    tulvataytto(pelitila, x_ruutu, y_ruutu) # Viedään ruudut funktioon joak tutkii ja avaa ruudut.

def tulvataytto(lista, taytto_y, taytto_x):
    '''
    Merkitsee pelitilassa olevat tuntemattomat alueet turvalliseksi siten, että
    täyttö aloitetaan annetusta x, y -pisteestä. Jos vapaita ruutuja ei ole enää,
    niin tehdään lopetustoimet.
    '''
    # Lista jolla seurataan ruutuja jotka käydään läpi loopin aikana.
    parilista = []
    parilista.append("{x}, {y}".format(x=taytto_x, y=taytto_y)) # Lisätään annettu koordinaatti käsittelylistaan.
    if lista[taytto_x][taytto_y] == "m":
        pelin_tulos = "Tappio"
        peli_paattyy(pelin_tulos) # Viedään tilanne funktioon, joka tekee päättymistoimet.
    else:
        while len(parilista) > 0 and lista[taytto_x][taytto_y] != "m":
            strpari = (parilista[0]) # Uusi pari käsittelyyn.
            parin_x, parin_y = strpari.split(',') # x ja y omaksi muuttujaksi.
            parin_x = int(parin_x)
            parin_y = int(parin_y)

            # Kierrokselle oleva ruutu merkataan turvalliseksi.
            lista[parin_x][parin_y] = "0"
            parilista.pop(0) # Poistetaan pari, että ei tule uudestaan käsittelyyn.          
            numero = laske_miinat(pelitila, parin_y, parin_x) # Palautetaan funktiolla ruudun miinamäärä.
            if int(numero) > 0: # Merkitään numeroruutu ja jatketaan loop alusta.
                lista[parin_x][parin_y] = numero
                continue
            korkeus = len(lista) # Koordinaatiston korkeus.
            leveys = len(lista[0]) # Koordinaatiston leveys.
            for rivi in range(-1, 2): # Käydään läpi deltapisteen ylä- ja alapuolet.
                for sarake in range(-1, 2): # Käydään läpi deltapisteen vasen ja oikea puoli.
                    if (rivi != 0 or sarake != 0) and \
                        (parin_x + rivi) > -1 and \
                        (parin_y + sarake) > -1 and \
                        (parin_x + rivi) < korkeus and \
                        (parin_y + sarake) < leveys: # Tarkastetaan lähtöpiste sekä reunat.
                        # Jos ympärillä oleva ruutu on tyhjä ja se ei ole parilistalla, niin lisätään se,
                        # jotta se käsitellään seuraavilla kierroksilla.
                        if lista[parin_x + rivi][parin_y + sarake] == " " and "{rivi}, {sarake}".format(rivi=parin_x + rivi, sarake=parin_y + sarake) not in parilista:
                            parilista.append("{rivi}, {sarake}".format(rivi=parin_x + rivi, sarake=parin_y + sarake))

    # Tutkitaan kenttän tilanne ja avointen ruutujen määrä.
    avoimien_ruutujen_maara = sum(x.count(' ') for x in pelitila)
    print("Avoimet ruudut", avoimien_ruutujen_maara)

    if avoimien_ruutujen_maara == 0:
        pelin_tulos = "Voitto"
        peli_paattyy(pelin_tulos) # Viedään tilanne funktioon, joka tekee päättymistoimet.

def piirra_kentta():
    '''
    Käsittelijäfunktio, joka piirtää kaksiulotteisena listana kuvatun miinakentän
    ruudut näkyviin peli-ikkunaan. Funktiota kutsutaan aina kun pelimoottori pyytää
    ruudun näkymän päivitystä.
    '''
    miinakentan_korkeus = len(pelitila)
    miinakentan_leveys = len(pelitila[0])
    haravasto.tyhjaa_ikkuna()
    haravasto.piirra_tausta()
    haravasto.aloita_ruutujen_piirto()

    for sarake in range(len(pelitila[0])):
        for rivi in range(len(pelitila)):
            if pelitila[rivi][sarake] == " ":
                haravasto.lisaa_piirrettava_ruutu(" ", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "m":
                haravasto.lisaa_piirrettava_ruutu(" ", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "0":
                haravasto.lisaa_piirrettava_ruutu("0", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "1":
                haravasto.lisaa_piirrettava_ruutu("1", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "2":
                haravasto.lisaa_piirrettava_ruutu("2", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "3":
                haravasto.lisaa_piirrettava_ruutu("3", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "4":
                haravasto.lisaa_piirrettava_ruutu("4", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "5":
                haravasto.lisaa_piirrettava_ruutu("5", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "6":
                haravasto.lisaa_piirrettava_ruutu("6", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "7":
                haravasto.lisaa_piirrettava_ruutu("7", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "8":
                haravasto.lisaa_piirrettava_ruutu("8", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
            elif pelitila[rivi][sarake] == "x":
                haravasto.lisaa_piirrettava_ruutu("x", (sarake * 40), (miinakentan_korkeus * 40 - 40) + (-1 * rivi) * 40)
    haravasto.piirra_ruudut()

def main(kentta_lista):
    '''
    Kutsutaan tätä funktiota, kun kun kaikki
    käsittelijät on asennettu ja ollaan valmiita aloittamaan.
    '''
    aloitusaika = time.time() # Aloiettaan aikalaskuri
    PARAMETRIT["pelaaja"]["aloitusaika"] = aloitusaika # Tallennetaan aloitusaika
    haravasto.aloita()

def tulosta_tilastot():
    """
    Tulostaa tilastot lomakkeen tekstilaatikko kenttään.
    """
    # OTSIKOT
    otsikko_head = "TILASTOT:\t\n"
    otsikko_nimi = "PELAAJAN NIMI"
    otsikko_tulos = "TULOS"
    otsikko_rivit = "RIVEJÄ"
    otsikko_sarak = "SARAKKEITA"
    otsikko_miin = "MIINAT"
    otsikko_siir = "SIIRROT"
    otsikko_paika = "PELIAIKA"
    otsikko_ppaiva = "PELIPÄIVÄ"
    # Otsikoiden muotoilut.
    rivin_otsikot = "{:<14}\t{:<7}\t{:<7}\t{:<11}\t{:<7}\t{:<8}\t{:<9}\t{:<10}\n".format\
        (otsikko_nimi, otsikko_tulos, otsikko_rivit, otsikko_sarak, \
            otsikko_miin, otsikko_siir, otsikko_paika, otsikko_ppaiva)
    # Yksittäiset tietokentät
    data_nimi = ikkunasto.lue_kentan_sisalto(k_nimikentta)
    data_tulos = PARAMETRIT["pelaaja"]["tulos"]
    data_sarak = ikkunasto.lue_kentan_sisalto(k_sarakkeidenlkm)
    data_rivit = ikkunasto.lue_kentan_sisalto(k_rivienlkm)
    data_miinat = ikkunasto.lue_kentan_sisalto(k_miinojenlkm)
    data_siirrot = PARAMETRIT["pelaaja"]["siirrot"]
    data_peliaika = PARAMETRIT["pelaaja"]["lopetusaika"] - PARAMETRIT["pelaaja"]["aloitusaika"]
    data_peliaika2 = time_convert(data_peliaika)
    data_pelipaiva = PARAMETRIT["pelaaja"]["pelipaiva"]
    # Datakenttien muotoilut.
    datakentat = "{:<14}\t{:<7}\t{:<7}\t{:<11}\t{:<7}\t{:<8}\t{:<9}\t{:<10}".format\
        (data_nimi, data_tulos, data_rivit, data_sarak, \
            data_miinat, data_siirrot, data_peliaika2, data_pelipaiva)
    # Tuloste elementtien niputus. Tehdään lisäys jos tekstiä on jo olemassa (tulostettu !=0).
    # Lisäksi tarkastetaan onko tulostettu tai onko ladattu tiedostoa aikaisemmin.
    onko_uusi = PARAMETRIT["pelaaja"]["tulostettu"]
    if onko_uusi == 0:
        viesti = otsikko_head + rivin_otsikot + datakentat
        ikkunasto.kirjoita_tekstilaatikkoon(tekstilaatikko, \
        viesti.replace("(","").replace(")","").replace("'",""), tyhjaa=True) # Korvataan ()' merkit
    else:
        viesti = datakentat
        ikkunasto.kirjoita_tekstilaatikkoon(tekstilaatikko, \
        viesti.replace("(","").replace(")","").replace("'",""))# Korvataan ()' merkit
         
def lataa_tilastot():
    """
    Funktio lataa tilastotiedosto ja sen tiedot.
    """
    polku = ikkunasto.avaa_tiedostoikkuna('Lataa tilastotiedosto')
    ikkunasto.kirjoita_tekstikenttaan(k_lataatieodosto, polku)
    viesti = ''
    try:
        with open(polku, "r") as kohde:
            sisalto = kohde.read()[:-1]
            viesti = str(sisalto)
            ikkunasto.kirjoita_tekstilaatikkoon(tekstilaatikko, viesti, tyhjaa=True)
            # Onnustunut lataus merkitään tulostetuksi, jotta seuraavat tulostusrivit menevät edellisen perään.
            PARAMETRIT["pelaaja"]["tulostettu"] += 1
            # Kirjoitetaan ladattu polku myös tallennukselle.
            ikkunasto.tyhjaa_kentan_sisalto(k_tallennatiedosto)
            ikkunasto.kirjoita_tekstikenttaan(k_tallennatiedosto, polku)
    except IOError:
        print("Kohdetiedostoa ei voitu avata. Luku epäonnistui")

def tallenna_tilastot():
    """
    Tallenna tilastotiedosto ja sen tiedot. Jos tiedostopolku on jo olemassa,
    tehdään pelitilastotallennus automaattisesti pelin päättyessä.
    """
    polku = ikkunasto.lue_kentan_sisalto(k_tallennatiedosto).rstrip()
    if PARAMETRIT["pelaaja"]["autotallennus"] == False: # Tiedoston voi vaihtaa, kun arvo on False.
        polku = ikkunasto.avaa_tallennusikkuna('Tallenna tilastotiedosto')
        ikkunasto.tyhjaa_kentan_sisalto(k_tallennatiedosto)
        ikkunasto.kirjoita_tekstikenttaan(k_tallennatiedosto, polku)
        try:
            with open(polku, "w") as kohde:
                kohde.write(tekstilaatikko.get(1.0, "end-1c")) # Kirjoitetaan koko tekstilaatikon sisältö.
        except IOError:
            print("Kohdetiedostoa ei voitu avata. Tallennus epäonnistui")
    elif PARAMETRIT["pelaaja"]["autotallennus"] == True: # Pelin päättyessä sallitaan automaattinen tallennus.
        with open(polku, "w") as kohde:
            kohde.write(tekstilaatikko.get(1.0, "end-1c"))
            PARAMETRIT["pelaaja"]["autotallennus"] = False # Poistetaan automaattinen tallennus, jotta tiedostoa voi vaihtaa.

def aloita_peli():
    try:
        PARAMETRIT["pelaaja"]["nimesi"] = ikkunasto.lue_kentan_sisalto(k_nimikentta)
        PARAMETRIT["pelaaja"]["leveys"] = int(ikkunasto.lue_kentan_sisalto(k_sarakkeidenlkm))
        PARAMETRIT["pelaaja"]["korkeus"] = int(ikkunasto.lue_kentan_sisalto(k_rivienlkm))
        PARAMETRIT["pelaaja"]["miinojenlkm"] = int(ikkunasto.lue_kentan_sisalto(k_miinojenlkm))

        # Luo pelikenttä ja miinoita se saaduilla parametreillä.
        pelikentta = luo_pelikentta(int(PARAMETRIT["pelaaja"]["korkeus"]), int(PARAMETRIT["pelaaja"]["leveys"]))
        pelitila[:] = pelikentta # Käytetään globaalia pelitila sanakirjaa pelin seuraamiseen.
        vapaat_ruudut = luo_vapaat_ruudut(int(PARAMETRIT["pelaaja"]["korkeus"]), int(PARAMETRIT["pelaaja"]["leveys"]))
        miinojen_lkm = int(PARAMETRIT["pelaaja"]["miinojenlkm"])
        miinoita(pelitila, vapaat_ruudut, miinojen_lkm)

        # Piirrä käyttöliittymä ja aseta hiiri
        haravasto.lataa_kuvat("spritet")
        #haravasto.lataa_kuvat("E:\Oulu\spritet") # Preview esikatselua varten
        miinakentan_korkeus = PARAMETRIT["pelaaja"]["korkeus"]
        miinakentan_leveys = PARAMETRIT["pelaaja"]["leveys"]
        haravasto.luo_ikkuna((40 * miinakentan_leveys), (40 * miinakentan_korkeus))
        haravasto.aseta_piirto_kasittelija(piirra_kentta)
        haravasto.aseta_hiiri_kasittelija(kasittele_hiiri)

        # Nollataan tarvittavat parametrit, kun aloitetaan uusi peli.
        PARAMETRIT["pelaaja"]["pelipaiva"] = ''
        PARAMETRIT["pelaaja"]["siirrot"] = 0
        PARAMETRIT["pelaaja"]["tulos"] = 0
        paivita_siirtojen_maara() # Päiviteään pääikkunan siirtojenmäärä.

        # Siirrytään aloittamaan
        main(pelitila)
    except ValueError:
        if ikkunasto.lue_kentan_sisalto(k_rivienlkm) == '':
            ikkunasto.avaa_viesti_ikkuna("Tietoja puuttuu", "Anna pelialueelle rivien määrä.", virhe=False)
        elif ikkunasto.lue_kentan_sisalto(k_sarakkeidenlkm) == '':
            ikkunasto.avaa_viesti_ikkuna("Tietoja puuttuu", "Anna pelialueelle sarakkeiden määrä.", virhe=False)
        elif ikkunasto.lue_kentan_sisalto(k_miinojenlkm) == '':
            ikkunasto.avaa_viesti_ikkuna("Tietoja puuttuu", "Anna miinojen määrä.", virhe=False)            
        else:
            ikkunasto.avaa_viesti_ikkuna("Odottomaton virhe", "Tapahtui virhe. Jos tilanne toistuu, niin ole hyvä ja ole yhteydessä ylläpitoon", virhe=False)
    except IndexError:
        ikkunasto.avaa_viesti_ikkuna("Ei mahdu kentälle", "Miinamäärä on liian suuri suhteessa kentän kokoon.", virhe=False)

def lopeta_peli():
    '''
    Funktio lopetusnapille.
    '''
    ikkunasto.lopeta()

def peli_paattyy(lopputulos):
    '''
    Kun osutaan miinaan tai vapaita ruutuja ei ole, niin kutsutaan tätä funktiota
    Funktio tekee ehdolliset lopetustoimet.
    '''
    # Muutetaan miinat "näkyväksi".
    for i in range(len(pelitila[0])):
        for k in range(len(pelitila)):
            if pelitila[k][i] == 'm':
                pelitila[k][i] = 'x'
    piirra_kentta()

    PARAMETRIT["pelaaja"]["tulos"] = lopputulos # Päivitetään globaaliin tauluun lopputulos.
    paivita_siirtojen_maara() # Päiviteään pääikkunan siirtojenmäärä.
    lopetusaika = time.time()
    PARAMETRIT["pelaaja"]["lopetusaika"] = lopetusaika # Pävitetään lopetusaika.
    paivita_aika() # Päiviteään pääikkunan käytetyt sekunnit.
    paivita_pelipaiva() # Päiviteään parametriin pelipäivä.
    tulosta_tilastot() # Päivitetään lomakkeen tekstiruutu ja tilastot.
    PARAMETRIT["pelaaja"]["tulostettu"] += 1
    if ikkunasto.lue_kentan_sisalto(k_tallennatiedosto) != '': # Jos tallennustiedosto on olemassa, niin tehdään tallennus.
        PARAMETRIT["pelaaja"]["autotallennus"] = True # Annetaan tehdä tallennus.
        tallenna_tilastot() # Tallennetaan tekstiruudussa olevat tilasto.
    else:
        pass

    if lopputulos == "Voitto":
        ikkunasto.avaa_viesti_ikkuna(lopputulos, "Voitto tuli. Onneksi olkoon, olet mestari. Sulje peliruutu ja kokeile uudestaan.", virhe=False)
    elif lopputulos == "Tappio":
        ikkunasto.avaa_viesti_ikkuna(lopputulos, "Tappio tuli. Harmin paikka :-) Sulje peliruutu ja kokeile uudestaan.", virhe=False)
    main(pelitila)

def paivita_siirtojen_maara():
    '''
    Funktio lomakkeen siirtomäärän päivitykselle.
    '''
    ikkunasto.paivita_tekstirivi(t_siirrotdata, PARAMETRIT["pelaaja"]["siirrot"])

def paivita_aika():
    '''
    Funktio lomakkeen peliajan päivitykselle.
    '''
    peliaika = PARAMETRIT["pelaaja"]["lopetusaika"] - PARAMETRIT["pelaaja"]["aloitusaika"] # Kulutettu aika sekunneissa
    peliaika2 = time_convert(peliaika) # Kulutettu aika minuuteissa
    ikkunasto.paivita_tekstirivi(t_aikadata, peliaika2)

def paivita_pelipaiva():
    '''
    Funktio lomakkeen pelipäivän päivitykselle.
    '''
    nyt = datetime.now()
    muotoiltu_paiva = nyt.strftime("%d.%m.%Y")
    PARAMETRIT["pelaaja"]["pelipaiva"] = muotoiltu_paiva

# Pääohjelma alkaa
if __name__ == "__main__":

    # Luodaan pelin pääikkuna sekä kaikki elementit.
    paa_ikkuna = ikkunasto.luo_ikkuna("Miinaharava 1.0")

    ylakehys = ikkunasto.luo_kehys(paa_ikkuna, ikkunasto.VASEN)
    tilastokehys = ikkunasto.luo_kehys(paa_ikkuna, ikkunasto.VASEN)
    tiedostokehys = ikkunasto.luo_kehys(paa_ikkuna, ikkunasto.VASEN)

    ylasyotekehys = ikkunasto.luo_kehys(ylakehys, ikkunasto.YLA)
    yladatakehys = ikkunasto.luo_kehys(ylakehys, ikkunasto.OIKEA)
    ylanappikehys = ikkunasto.luo_kehys(ylakehys, ikkunasto.ALA)

    t_aloitustiedot = ikkunasto.luo_tekstirivi(ylasyotekehys, "Aloitustiedot")
    t_nimi = ikkunasto.luo_tekstirivi(ylasyotekehys, "Nimesi:")
    k_nimikentta = ikkunasto.luo_tekstikentta(ylasyotekehys)
    t_rivienlkm = ikkunasto.luo_tekstirivi(ylasyotekehys, "Syötä rivien määrä:")
    k_rivienlkm = ikkunasto.luo_tekstikentta(ylasyotekehys)
    t_sarakkeidenlkm = ikkunasto.luo_tekstirivi(ylasyotekehys, "Syötä sarakkeiden määrä:")
    k_sarakkeidenlkm = ikkunasto.luo_tekstikentta(ylasyotekehys)
    t_miinojenlkm = ikkunasto.luo_tekstirivi(ylasyotekehys, "Syötä miinojen määrä:")
    k_miinojenlkm = ikkunasto.luo_tekstikentta(ylasyotekehys)

    aloitanappi = ikkunasto.luo_nappi(tilastokehys, "ALOITA PELI", aloita_peli)
    lopetanappi = ikkunasto.luo_nappi(tilastokehys, "LOPETA PELI", lopeta_peli)
    t_siirrot = ikkunasto.luo_tekstirivi(tilastokehys, "Siirrot")
    t_siirrotdata = ikkunasto.luo_tekstirivi(tilastokehys, "000")
    t_aika = ikkunasto.luo_tekstirivi(tilastokehys, "Kulunut aika(m:s)")
    t_aikadata = ikkunasto.luo_tekstirivi(tilastokehys, "0:00")

    tekstilaatikko = ikkunasto.luo_tekstilaatikko(tilastokehys, 90, 15)
    aloitusinfo = \
    "Tervetuloa pelaamaan miinaharavaa.\n\nVoit itse määritellä pelialueen koon syöttämällä haluamasi määrän rivejä ja sarakkeita.\nValitse lisäksi miinojen määrä. Halutessasi voi syöttää nimesi.\n\nSovelluksessa on mahdollista tallentaa tilastot tiedostoon. Voit myös tarvittaessa ladata tilastotiedoston omalta tietokoneelta. Ladatava tiedosto pitää olla samassa muodossa, kuin tallennettava tiedosto."
    ikkunasto.kirjoita_tekstilaatikkoon(tekstilaatikko, aloitusinfo)

    tiedostosyotekehys = ikkunasto.luo_kehys(ylakehys, ikkunasto.YLA)
    t_tiedostonlataus = ikkunasto.luo_tekstirivi(tiedostosyotekehys, "Tilaston lataus ja tallennus")
    t_lataatiedosto = ikkunasto.luo_tekstirivi(tiedostosyotekehys, "Lataa tilastot:")
    k_lataatieodosto = ikkunasto.luo_tekstikentta(tiedostosyotekehys)
    n_hae_tiedosto_nappi = ikkunasto.luo_nappi(tiedostosyotekehys, "HAE LATAUSTIEDOSTO", lataa_tilastot)
    t_tallennatiedosto = ikkunasto.luo_tekstirivi(tiedostosyotekehys, "Tallenna tilastot:")
    k_tallennatiedosto = ikkunasto.luo_tekstikentta(tiedostosyotekehys)
    n_tallenna_tiedosto_nappi = ikkunasto.luo_nappi(tiedostosyotekehys, "HAE TALLENNUSTIEDOSTO", tallenna_tilastot)

    ikkunasto.kaynnista()
# EOF
