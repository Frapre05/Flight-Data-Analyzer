import streamlit as st
import requests
import folium
import datetime
from streamlit_folium import st_folium

st.title('Flight Data Analizer')

# Primo passo: importo i dati da OpenSky, e li estraggo
url = "https://opensky-network.org/api/states/all"
bbox = {"lamin": 35.5, "lomin": 6.6, "lamax": 47.1, "lomax": 18.6}

# Vado ad estrarre i dati, registrandomi anche sul sito in modo da poter ottenere i dati per più tempo 
def get_access_token():
    token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": st.secrets["OPENSKY_CLIENT_ID"],
        "client_secret": st.secrets["OPENSKY_CLIENT_SECRET"],
    }
    risposta_token = requests.post(token_url, data=payload)
    risposta_token.raise_for_status()
    return risposta_token.json()["access_token"]

# Costruiamo i risultati in modo da dar loro un tempo di vita (ttl) di 30 secondi.
# In questo modo la pagina non deve sempre aggiornarsi, lo farà da sola ogni 30 secondi
# e noi avremo il tempo di analizzare i vari voli 
@st.cache_data(ttl=30)
def carica_voli():
    token = get_access_token()
    headers = {"Authorization": "Bearer " + token}
    risposta = requests.get(url, params=bbox, headers=headers)
    dati = risposta.json()
    orario_richiesta = datetime.datetime.now().strftime("%H:%M:%S")
    return dati["states"], orario_richiesta

voli, orario = carica_voli()
st.write("Ultimo aggiornamento reale dei dati:", orario)


# Prelevo la lista dei voli e verifico quanti voli sono attivi nel territorio
st.write('Numero di voli trovati:',len(voli))

# Creiamo una tabella con i dati importati dal sito web
import pandas as pd

nomi_colonne = ["icao24", "callsign", "paese", "time_position", "last_contact",
                "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
                "true_track", "vertical_rate", "sensors", "geo_altitude",
                "squawk", "spi", "position_source"]

tabella = pd.DataFrame(voli, columns=nomi_colonne)

st.write(tabella)

voli_in_volo=tabella[tabella['on_ground']==False]
st.write('Voli in volo:', len(voli_in_volo))
# Procedo con la creazione di una mappa raffigurante i vari aerei, nella zona geografica italiana
# La mappa distingue aerei a varie quote, e permette di studiare il singolo velivolo
mappa = folium.Map(location=[41.9, 12.5], zoom_start=6)

# Creo uno slider che filtra le varie quote. Quota minima 0, quota massima la massima quota dei velivoli analizzati. 
quota_massima_osservata = int(voli_in_volo["baro_altitude"].max())

quota_max = st.slider("Mostra solo voli con altitudine inferiore a (metri):", 0, quota_massima_osservata, quota_massima_osservata)

voli_filtrati = voli_in_volo[voli_in_volo["baro_altitude"] <= quota_max]

st.write("Voli mostrati:", len(voli_filtrati))

# Filtriamo i voli per altitudine. Colori diversi corrispondono a quote diverse.
def colore_per_altitudine(alt):
    if alt < 3000:
        return "red"
    elif alt < 8000:
        return "orange"
    else:
        return "green"

mappa = folium.Map(location=[41.9, 12.5], zoom_start=6)

for indice, volo in voli_filtrati.iterrows():
    lat = volo["latitude"]
    lon = volo["longitude"]
    alt = volo["baro_altitude"]
    callsign = volo["callsign"]
    velocita = volo["velocity"]

    colore = colore_per_altitudine(alt)

    testo_popup = callsign + " - alt: " + str(alt) + "m - vel: " + str(velocita) + "m/s"

    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color=colore,
        fill=True,
        popup=testo_popup
    ).add_to(mappa)

st_folium(mappa, width=700, height=500)