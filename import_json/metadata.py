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
                meta = meta + "-" + str(type(acte[meta]))
                if meta not in metadata:
                    metadata[meta] = 1
                else:
                    metadata[meta] +=1

print(metadata)