import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr.json"

with open(file, 'r') as f:
    data = json.load(f)

metadata = {}

for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            for meta in acte:
                meta = meta + "-" + str(type(acte[meta]))  # J'associe chaque méta-donnée à son type
                if meta == "Text_Region-<class 'list'>":  # Je récupère les métadonnées contenues dan les text_region
                    for t in acte["Text_Region"]:
                        for a in t:
                            a = "Text_region_" + a + str(type(t[a]))
                            if a == "Text_region_Texte<class 'list'>":  # Je vérifie que ces éléments sont des chaînes
                                nbr = 0
                                for text in t["Texte"]:
                                    if type(text) != str:
                                        print("erreur")
                                a = a + "_str"
                            if a not in metadata:  # Je crée aussi une entrée pour ces variables
                                metadata[a] = 1
                            else:
                                metadata[a] += 1
                if meta not in metadata:  # Je crée une entrée par type de métadonnée
                    metadata[meta] = 1
                else:
                    metadata[meta] += 1

print(metadata)