import requests
import json
import pandas as pd
import os
from datetime import datetime

# Prelevo le credenziali di OpenSky dal pc
client_id = os.environ.get("OPENSKY_CLIENT_ID")
client_secret = os.environ.get("OPENSKY_CLIENT_SECRET")

if not client_id or not client_secret:
    # Non trovate come variabili d'ambiente: siamo in locale, leggi dal file
    cartella_script = os.path.dirname(os.path.abspath(__file__))
    percorso_credenziali = os.path.join(cartella_script, "credentials.json")
    with open(percorso_credenziali) as file:
        credenziali = json.load(file)
    client_id = credenziali["clientId"]
    client_secret = credenziali["clientSecret"]
# Prendo il token di accesso al sito
def get_access_token():
    token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    risposta_token = requests.post(token_url, data=payload)
    risposta_token.raise_for_status()
    return risposta_token.json()["access_token"]

token = get_access_token()

# Entro nel sito e calcolo il numero di voli attivi nel rettangolo "Italia"
url = "https://opensky-network.org/api/states/all"
bbox = {"lamin": 35.5, "lomin": 6.6, "lamax": 47.1, "lomax": 18.6}
headers = {"Authorization": "Bearer " + token}

risposta = requests.get(url, params=bbox, headers=headers)
risposta.raise_for_status()
dati = risposta.json()
voli = dati["states"]

# Trasformo i voli e le rispettive informazioni in una tabella pandas
nomi_colonne = ["icao24", "callsign", "paese", "time_position", "last_contact",
                "longitude", "latitude", "baro_altitude", "on_ground", "velocity",
                "true_track", "vertical_rate", "sensors", "geo_altitude",
                "squawk", "spi", "position_source"]

tabella = pd.DataFrame(voli, columns=nomi_colonne)

# Associo ad ogni tabella l'orario in cui è stata generata
tabella["timestamp_raccolta"] = datetime.now()

# Creo un file csv che raccoglie i dati, e li salva e accumula
cartella_script = os.path.dirname(os.path.abspath(__file__))
nome_file = os.path.join(cartella_script, "storico_voli.csv")

tabella.to_csv(nome_file, mode="a", header=not os.path.exists(nome_file), index=False)

print(f"Salvati {len(tabella)} voli alle {datetime.now()}")