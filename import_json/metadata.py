import json
import csv

json_file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr.json"


def metadata(file):
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
                    #if meta == "Language-<class 'str'>":
                    #    meta = acte["Language"]
                    if meta not in metadata:  # Je crée une entrée par type de métadonnée
                        metadata[meta] = 1
                    else:
                        metadata[meta] += 1
    for m in metadata:
        print(m, metadata[m])


metadata(json_file)


'''erreurs = [("Act_N", "Volume + Folio_start", "VOL_FOL_START")]
for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            if acte["VOL_FOL_START"] != acte["Volume"] + "_" + acte["Folio_start"]:
                erreurs.append((acte["Act_N"], acte["Volume"] + "_" + acte["Folio_start"], acte["VOL_FOL_START"]))

with open("/home/reignier/Bureau/Himanis/incoherences.csv", 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow(e)'''

'''erreurs = [("ImageStart_UPVLC_BVMM", "ImageStart_READ")]
for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            if acte["F"] != "":
                erreurs.append((acte["ImageStart_UPVLC_BVMM"]))

with open("/home/reignier/Bureau/Himanis/incoherences_2.csv", 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow(e)'''
