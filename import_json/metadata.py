import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr.json"

with open(file, 'r') as f:
    data = json.load(f)

mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

metadata = {}

for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            for meta in acte:
                meta = meta + "-" + str(type(acte[meta]))  # J'associe chaque méta-donnée à son type
                '''if meta == "Date-<class 'str'>":  # Je traite à part les dates pour en différencier le type
                    f = acte["Date"].split(".")[0]  # Je commence par supprimer les points finaux
                    f = f.split(',')  # Puis je segmente au niveau de la virgile s'il y en a une
                    if len(f) > 1:
                        if " " in f[1]:  # j'élimine l'espace initial
                            f[1:] = f[1].split(" ")[1:]
                        if f[1] in mois:  # J'isole une première forme
                            meta = "aaaa-mm"
                        else: # Je définis quelques formes plus complexes
                            f_bis = f[1:]
                            if len(f_bis) > 1:
                                if f_bis[0] in mois and ("er" in f_bis[1] or f_bis[1].isdigit()):
                                    meta = "aaaa-mm-jj"
                                elif ("er" in f_bis[0] or f_bis[0].isdigit()) and f_bis[1] in mois:
                                    meta = "aaaa-jj-mm"
                            else:
                                meta = "forme complexe"
                                #print(acte["Date"])
                    else:  # Autres formes possibles TODO : Non exhaustive encore, modèle peut-être à améliorer
                        if len(acte["Date"].split("-")) > 1:
                            meta = "incertitude"
                        else:
                            if acte["Date"] in ["Undated", "None", "S.d.", "", " S.d."]:
                                meta = "sans date"
                            else:
                                try:
                                    int(acte["Date"])
                                    meta = "année"
                                except:
                                    meta = "complexe"
                                    #print(acte["Date"])'''
                if meta == "Text_Region-<class 'list'>":
                    for t in acte["Text_Region"]:
                        for a in t:
                            a = "Text_region_" + a + str(type(t[a]))
                            if a == "Text_region_Texte<class 'list'>":
                                nbr = 0
                                for text in t["Texte"]:
                                    if type(text) != str:
                                        print("erreur")
                                a = a + "_str"
                            if a not in metadata:
                                metadata[a] = 1
                            else:
                                metadata[a] += 1
                if meta not in metadata:
                    metadata[meta] = 1
                else:
                    metadata[meta] += 1

print(metadata)