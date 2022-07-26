import json
import csv

json_file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_language_index.json"
result = "/home/reignier/Bureau/Himanis/erreurs_alignement_arkindex.csv"

erreurs = []

# Use a table to associate image to page name on Arkindex
table = "/home/reignier/Bureau/Himanis/table_concordance_images_folio.csv"
with open(table, 'r', encoding="utf8") as f:
    spamreader = csv.reader(f, delimiter='\t')
    files = {}
    for row in spamreader:
        files[row[0]] = row[1]

with open(json_file, 'r') as f:
    data = json.load(f)
    for registres in data:
        for registre in data[registres]:
            for serie in registre:
                acte = registre[serie]
                zones = acte["Text_Region"]
                for zone in zones:
                    address = zone["Address_bvmm"]
                    if "iiif" in address:
                        address = address.split(",")[0]  # Je sectionne l'url au niveau des coordonnées
                        while address[-1] != "/":  # J'enlève tout ce qui précède le dernier slash
                            address = address[:-1]
                        address = address[:-1]  # J'enlève aussi le dernier slash
                        if address not in files:
                            erreurs.append((address, "Provisory_index_3: " + str(acte["Provisory_index_3"])))

with open(result, 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow([e[0]])