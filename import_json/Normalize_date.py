import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr.json"
result = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date.json"

with open(file, 'r') as f:
    data = json.load(f)

mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
        "décembre"]

for registre in data:
    contenu_registre = data[registre]
    for serie in contenu_registre:
        for acte in serie:
            data_acte = serie[acte]
            date_normalisee = {"annee": None, "mois": None, "jour": None, "date à traiter manuellement": None}
            taq, tpq = None, None
            date = data_acte["Date"].lower()
            date = date.replace(".", "").replace(",", "").replace("\"&gt;", "").replace("(cancellé)",
                                                                                        "").replace("sic", "").replace(
                "/", "")  # J'élimine les éléments gênants
            date = date.replace("decembre", "décembre").replace("fevrier", "février").replace("1er", "01") \
                .replace("1 er", "01").replace("aôut", "août")  # Je normalise les formes courantes
            date = date.split()
            if len(date) > 1 and date[0] == "sd":
                # J'élimine les éléments sans date quand elle est devinée
                date = date[1:]
            if not date:  # Si la valeur est vide, je laisse le champs vides
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
            elif len(date) > 1:  # Si la forme contient plus d'un élément
                if date[0].isdigit() and len(date[0]) == 4:  # Formes qui commencent par l'année
                    date_normalisee["annee"] = int(date[0])
                    if date[1] in mois:  # Puis par un second élément mois
                        date_normalisee["mois"] = mois.index(date[1]) + 1
                        if len(date) > 2:  # Et un troisième jour
                            if date[2].isdigit() and len(date[2]) == 2:
                                date_normalisee["jour"] = int(date[2])
                            elif date[2] == "(ns)" or date[2:] == ['(n', 'st)']:  # Récupération du style
                                date_normalisee["jour"] = None
                                date_normalisee["style"] = "nouveau"
                            elif date[2] == "(as)":
                                date_normalisee["jour"] = None
                                date_normalisee["style"] = "ancien"
                                date_normalisee["date à traiter manuellement"] = "OOOO"
                            else:
                                date_normalisee["date à traiter manuellement"] = "OOOO"
                        else:
                            date_normalisee["jour"] = None
                    elif len(date) > 2 and date[1].isdigit() and len(date[1]) < 3:  # Ou par un second élément jour
                        date_normalisee["jour"] = int(date[1])
                        if date[2] in mois:  # Et un troisième mois
                            date_normalisee["mois"] = mois.index(date[2]) + 1
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                    elif date[1] == "(ns)" or date[1:] == ['(n', 'st)']:
                        date_normalisee["style"] = "nouveau"
                        date_normalisee["jour"], date_normalisee["mois"] = None, None
                    elif date[1] == "(as)":
                        date_normalisee["style"] = "ancien"
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                        date_normalisee["jour"], date_normalisee["mois"] = None, None
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                elif date[0] in mois:  # Formes qui commencent par le mois
                    date_normalisee["mois"], date_normalisee["jour"] = mois.index(date[0]) + 1, None
                    if date[1].isdigit() and len(date[1]) == 4:  # Puis l'année
                        date_normalisee["annee"] = int(date[1])
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                    if len(date) > 2:  # Et éventuellement le style
                        if date[2] == "(ns)" or date[2:] == ['(n', 'st)']:
                            date_normalisee["style"] = "nouveau"
                        elif date[2] == "(as)":
                            date_normalisee["style"] = "ancien"
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                elif date[0].isdigit() and len(date[0]) < 3 and date[1] in mois:
                    # Formes qui commencent par le jour et le mois
                    date_normalisee["jour"], date_normalisee["mois"] = int(date[0]), mois.index(date[1]) + 1
                    if len(date) > 2:  # Puis l'année
                        if date[2].isdigit() and len(date[2]) == 4:
                            date_normalisee["annee"] = int(date[2])
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                elif date == ['s', 'd']:  # Formes sans date
                    date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
                else:
                    date_normalisee["date à traiter manuellement"] = "OOOO"
            elif date[0].isdigit():  # Si la valeur est juste une année
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = int(date[0]), None, None
            elif date[0] in ["undated", "none", "sd"]:  # Si c'est un champ signifiant qu'elle est vide
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
            else:
                date = date[0].split("-")
                if len(date) > 1:  # Si c'est une intervalle
                    tpq, taq = int(date[0]), int(date[1])
                else:  # Sinon c'est un truc compliqué
                    date_normalisee["date à traiter manuellement"] = "OOOO"
            if taq and tpq:
                data_acte["Date-normalisee"] = [{"type": "notBefore", "year": tpq, "month": None, "day": None},
                                                {"type": "notAfter", "year": taq, "month": None, "day": None}]
            else:
                data_acte["Date-normalisee"] = [{"type": "when", "year": date_normalisee["annee"],
                                                 "month": date_normalisee["mois"], "day": date_normalisee["jour"]}]
            if date_normalisee["date à traiter manuellement"] == "OOOO":
                data_acte["Date à traiter manuellement"] = True

with open(result, 'w') as f:
    json.dump(data, f)
