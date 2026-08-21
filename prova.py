import requests
# Primo passo: importo i dati da OpenSky, e li estraggo
url = "https://opensky-network.org/api/states/all"
bbox = {"lamin": 35.5, "lomin": 6.6, "lamax": 47.1, "lomax": 18.6}

risposta = requests.get(url, params=bbox)
# Verifico che non ci siano errori, controllando lo status code della mia risposta
print(risposta.status_code)
dati = risposta.json()

# Vedo di che tipo sono i dati 
print(type(dati))
print(dati.keys())

# Prelevo la lista dei voli e verifico quanti voli sono attivi nel territorio
voli=dati['states']
print(len(voli))

# Analizziamo i primi 10 voli. Ne studiamo numero, paese di "immatricolazione", quota, GS
for volo in voli[:10]:
    callsign = volo[1]
    paese = volo[2]
    altitudine = volo[7]
    velocita = volo[9]
    print(callsign, "-", paese, "- alt:", altitudine, "- vel:", velocita)

# Ora contiamo su TUTTI i voli, non solo i primi 10, vediamo quali danno un None ingiustificato
none_e_a_terra = 0
none_ma_in_volo = 0

for volo in voli:
    altitudine = volo[7]
    a_terra = volo[8]
    if altitudine is None:
        if a_terra == True:
            none_e_a_terra += 1
        else:
            none_ma_in_volo += 1

print("None con on_ground=True:", none_e_a_terra)
print("None ma in volo (on_ground=False):", none_ma_in_volo)

# Iniziamo a creare una lista di voli puliti
# Base: teniamo solo chi ha posizione valida (lat/lon), requisito minimo per qualsiasi analisi
voli_validi = []
for volo in voli:
    lon = volo[5]
    lat = volo[6]
    if lon is not None and lat is not None:
        voli_validi.append(volo)

# Da qui, due rami paralleli, nessuno dei due "sopra" l'altro
voli_in_volo = []
voli_a_terra = []
for volo in voli_validi:
    a_terra = volo[8]
    if a_terra == False:
        voli_in_volo.append(volo)
    else:
        voli_a_terra.append(volo)

print("Voli totali:", len(voli))
print("Voli validi (con posizione):", len(voli_validi))
print("Di cui in volo:", len(voli_in_volo))
print("Di cui a terra:", len(voli_a_terra))

# Raccogliamo le posizioni dei voli per creare una prima bozza di grafico
latitudini=[]
longitudini=[]
altitudini=[]
for volo in voli_in_volo:
    lon = volo[5]
    lat = volo[6]
    alt = volo[7]
    altitudini.append(alt)
    longitudini.append(lon)
    latitudini.append(lat)

print(len(longitudini), len(latitudini),len(altitudini))

# Importiamo la libreria python per fare i grafici. La importiamo come plt, convenzione usata
# Creiamo un grafico e inseriamo lat-long come coordinate
import matplotlib.pyplot as plt 
plt.scatter(longitudini, latitudini, s=5, c=altitudini, cmap="viridis")
plt.colorbar(label="Altitudine (m)")
plt.xlabel("Longitudine")
plt.ylabel("Latitudine")
plt.axis('equal')
plt.title("Aerei in volo sull'Italia - " + str(len(voli_in_volo)) + " voli")
plt.show()