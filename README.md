_Dit zien de_
# Kaajd hèl Fekts
## Hoe dan?
### Direct op de command line:
Eerst:
``` bash
python3 wa-stats.py /pad/naar/de/whatsapp/chat_data.txt
```
Daarna:
``` bash
python3 wa-graphs.py /pad/naar/de/whatsapp/chat_data.txt
```
### Draai een server via web applicatie:
Op de command line:
``` bash
python3 wa-flask.py
```
Dit start een server op poort 5000 (kun je aanpassen in wa-flask.py) op je huidige computer. Dus, open hierna je browser op:
```
localhost:5000
```
of op:
```
127.0.0.1:5000
```
en go nuts!
## Wat werkt er (sort of)
### Command line:
Hieronder beschrijving van twee scripts. Allebei kunnen ze met een command line argument naar een bestand gewezen worden. Bijvoorbeeld:
``` bash
python3 wa-stats.py /pad/naar/de/whatsapp/chat_data.txt
```
Als er geen pad gegeven wordt dan wordt aangenomen dat het txt bestand in  /data staat (maar dat ga ik nog aanpassen denk ik).
##### wa-stats.py
Neemt een WhatsApp chat export (txt) en maakt het volgende:
1. CSV met de WhatsApp data netjes gesplitst in kolommen
2. HTML met tabel van basis stats
3. JSON met tabel van basis stats
De console output (stdout) is ook de json, want ik gebruik het nu samen met n8n zodat ik voor nu makkelijker via Google Drive kan.
##### wa-graphs.py
Kan uitgevoerd worden pas nadat wa-stats.py is uitgevoerd, want gebruikt output van dat script (de CSV met raw data). Als 'ie die heeft dan maakt dit script een aantal grafiekjes op basis van die data.
### Lokaal een eigen web app draaien:
Dat gebruikt wa-flask.py voor de server en interface, en roept wa-stats-flask.py (ipv wa-stats.py b/c I couldn't be arsed om die twee te integreren) en wa-graphs.py (want die had ik toevallig flexibel genoeg geschreven), zet alle output netjes in een directory, en laat je een pagina met output zien. Met fancy(-ish) graphs waar je op kunt klikken om te vergroten.

## Road map
- [ ] LLM / openai integratie voor snarky comments
- [ ] Ontvang resultaten optioneel per mail (zou nu wel kunnen, maar dan via Google)
- [x] Web interface
- [ ] Web interface ergens hosten
- [ ] MOAR GRAPHS!!!
- [ ] Chatten met je chat data, voor maximale zinloosheid
- [ ] Exporteren LLaMA trainingsdata?
- [ ] Beautifyen layout enzo
- [ ] Directe integratie met WhatsApp zelf, bv automatische periodieke updates, of altijd als Nardy op 25/26 dec een foto stuurt
- [ ] Of automatisch statistieken over alle foto's die als toetje worden herkent?
- [ ] Image generation voor bepaalde dingen? Bv. van bepaalde soorten berichten, top emoji, of weet ik veel wat.
