import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_and_language_final.json"
result = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_language_index.json"

with open(file, 'r') as f:
    data = json.load(f)

i = 1
for registre in data:
    contenu_registre = data[registre]
    for serie in contenu_registre:
        for acte in serie:
            data_acte = serie[acte]
            data_acte["Provisory_index_3"] = i
            i += 1

with open(result, 'w') as f:
    json.dump(data, f)

from metadata import metadata
metadata(file)
metadata(result)
