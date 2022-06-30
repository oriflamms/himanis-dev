from pathlib import Path
import argparse
from arkindex import ArkindexClient, options_from_env
from apistar.exceptions import ErrorResponse
import logging
from tqdm import tqdm
import json, csv

# create an arkindex client
ark_client = ArkindexClient()

# The id of the Himanis corpus on Arkindex
#CORPUS_ID = "ed249464-96c5-4ca6-a717-f99fc9bf4ce6" #Corpus Himanis
CORPUS_ID = "dbf1fc04-d825-4a3a-b3e4-60ff010a9480" #Corpus d'essai avant import sur Himanis

# Use a table to associate image to page name on Arkindex
table = "/home/reignier/Bureau/Himanis/table_concordance_images_folio.csv"
with open(table, 'r', encoding="utf8") as f:
    spamreader = csv.reader(f, delimiter='\t')
    files = {}
    for row in spamreader:
        files[row[0]] = row[1]

# logger configuration
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def parse_json(json_file):
    logger.info(f'parsing {json_file}')
    with open(json_file, 'r') as f:
        data = json.load(f)
    for registre in data:
        acts = data[registre]
        for dict in tqdm(acts):
            for acte in dict:
                act = dict[acte]
                # get the volume's arkindex id of the act
                logger.info(f'looking for act {act["Volume"]}')
                volume_id = get_volume_id(act["Volume"])
                logger.info(f'found id {volume_id}')
                if volume_id:
                    push_act(volume_id, act["Act_N"], act)  # D'abord je crée les actes
                    for region in act["Text_Region"]:  # Puis je crée les zones d'images correspondant
                        folio = get_folio(region["Address_bvmm"])
                        page = get_page(volume_id, folio)
                        act_parent = get_act(volume_id, act["Act_N"])
                        if page and act_parent:
                            push_zone(page, act["Act_N"], region, act_parent['id'])
                        else:
                            continue
                else:
                    continue


def get_folio(address_bvmm):
    """
    function that gives name of the folio on Arkindex with an url address
    """
    address = address_bvmm.split(",")[0]  # Je sectionne l'url au niveau des coordonnées
    while address[-1] != "/":  # J'enlève tout ce qui précède le dernier slash
        address = address[:-1]
    address = address[:-1]  # J'enlève aussi le dernier slash
    folio = files[address]
    return folio


def get_volume_id(volume_name):
    """
    function that gets the volume's arkindex id of the act
    input: volume_name the name of the
    """
    if "JJ" in volume_name:
        volume_name = volume_name.replace("JJ", "JJ ")
        volume_name = "France, Paris, Archives nationales, " + volume_name
    # try a request to the api to get the volume with the name volume_name
    logger.info(f'complete name is {volume_name}')
    try:
        # call to the API for this endpoint https://arkindex.teklia.com/api-docs/#operation/ListElements
        volumes = ark_client.paginate("ListElements", corpus=CORPUS_ID, name=volume_name)
    except ErrorResponse as e:
        logger.error('Failed getting corpus elements {} with name {}: {} - {}'.format(
            CORPUS_ID, volume_name, e.status_code, e.content))
    for volume in volumes:
        if volume["name"] == volume_name:
            return volume['id']
    return None


def get_page(volume_id, page_name):
    """
    function that gets the page with the name page_name from volume with volume_id
    """
    # try a request to the api to get the page with the name page_name
    while len(page_name) != 4:
        page_name = "0" + page_name
    try:
        # call to the API for this endpoint https://arkindex.teklia.com/api-docs/#operation/ListElementChildren
        pages = ark_client.paginate("ListElementChildren", id=volume_id, name=page_name)
    except ErrorResponse as e:
        logger.error('Failed getting folder elements {} with name {}: {} - {}'.format(
            volume_id, page_name, e.status_code, e.content))
    for page in pages:
        if page["name"] == page_name:
            return page
    return None


def get_act(volume_id, act_name):
    """
    function that gets the act with the name act_name from page with page_id
    """
    # try a request to the api to get the act with the name act_name
    try:
        # call to the API for this endpoint https://arkindex.teklia.com/api-docs/#operation/ListElementChildren
        acts = ark_client.paginate("ListElementChildren", id=volume_id, name=act_name)
    except ErrorResponse as e:
        logger.error('Failed getting folder elements {} with name {}: {} - {}'.format(
            volume_id, act_name, e.status_code, e.content))
    for act in acts:
        if act["name"] == act_name:
            return act
    return None


def push_act(volume_id, act_name, data):
    # request to the API using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateElement
    try:
        body = {"type": "act", "name": act_name, "corpus": CORPUS_ID, "parent": volume_id}
        logger.info(f'creating element with body {body}')
        element = ark_client.request("CreateElement", body=body)
    except ErrorResponse as e:
        logger.error('Failed creating element {}: {} - {}'.format(act_name, e.status_code, e.content))
        return

    for date in data["Date-normalisee"]:
        if data["Date-normalisee"][0]["type"] == "when":
            if date["year"]:  # Fonction pour construire ma forme iso
                date["forme normalisee"] = str(date["year"])
                if date["month"]:
                    if len(str(date["month"])) == 1:
                        date["month"] = "0" + str(date["month"])
                    date["forme normalisee"] = date["forme normalisee"] + "-" + \
                                               str(date["month"])
                    if date["day"]:
                        if len(str(date["day"])) == 1:
                            date["day"] = "0" + str(date["day"])
                        date["forme normalisee"] = date["forme normalisee"] + "-" + \
                                                   str(date["day"])
            else:
                date["forme normalisee"] = None
            data["Date_Arkindex"] = data["Date-normalisee"][0]["forme normalisee"]
        else:
            for extreme in data["Date-normalisee"]:
                if extreme["type"] == "notBefore":
                    debut = extreme["year"]
                elif extreme["type"] == "notAfter":
                    fin = extreme["year"]
            data["Date_Arkindex"] = str(debut) + "-" + str(fin)
    if data["Inventory_Name"] and data["Inventory_Nr"]:
        data["Inventory_Reference"] = data["Inventory_Name"] + "_" + data["Inventory_Nr"]
    else:
        data["Inventory_Reference"] = ""
    data["languages"] = data["normalized_language"]["language"]

    for e in data:
        # TODO : est-ce que language est une métadonnée répétable ?
        metadata = [["Act_N", "Languages", "Inventory_Reference", "Date_Arkindex", "Regeste"],
        ["himanisId", "language", "inventoryReference", "date", "abstract"]]
        if data[e] and e in metadata[0]:
            # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateMetaData
            if e == "Date_Arkindex":
                type_data = "date"
            else:
                type_data = "text"
            if type(data[e]) != list:  # Pour que toutes les données soient sous forme d'une liste itérable
                data[e] = [data[e]]
            for contenu in data[e]:
                print(type(e), e)
                try:
                    body = {"type": type_data, "name": metadata[1][metadata[0].index(e)], "value": contenu}
                    logger.info(f'creating metadata {body}')
                    print("beginning")
                    ark_client.request("CreateMetaData", id=element['id'], body=body)
                    print("end")
                except ErrorResponse as e:
                    logger.error('Failed creating metadata on element {}: {} - {}'.format(
                        element['id'], e.status_code, e.content))


def push_zone(page, name, region, act_id):
    # create the element on the page
    # turn text representation of the coordinates into list of coordinates
    polygon = region["Graphical_coord"]
    polygon = polygon.split(" ")
    coordinates = []
    for coor in polygon:
        coor = coor.split(",")
        coor = [int(coor[0]), int(coor[1])]
        dim = [max([t[0] for t in page["zone"]["polygon"]]), max([t[1] for t in page["zone"]["polygon"]])]
        for t in range(0, 2):  # Check that the coordinates do not exceed the page
            if coor[t] > dim[t]:
                coor[t] = dim[t]
        coordinates.append(coor)

    # request to the API using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateElement
    try:
        body = {"type": "text_zone", "name": "Acte " + name, "corpus": CORPUS_ID, "parent": page["id"],
                "image": page["zone"]["image"]["id"], "polygon": coordinates}
        logger.info(f'creating element with body {body}')
        element = ark_client.request("CreateElement", body=body)
    except ErrorResponse as e:
        logger.error('Failed creating element {}: {} - {}'.format(name, e.status_code, e.content))
        return

    # request to this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateElementParent to link with act
    try:
        logger.info(f'add new parent {act_id}')
        ark_client.request("CreateElementParent", child=element['id'], parent=act_id)
    except ErrorResponse as e:
        logger.error('Failed creating parent on element {}: {}{} - {} - {}'.format(
            element['id'], "with ", act_id, e.status_code, e.content))
        return

    # if the element was created, add transcription to the element
    text = '\n'.join(region["Texte"])
    # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateTranscription
    try:
        logger.info(f'add transcription {text}')
        ark_client.request("CreateTranscription", id=element['id'], body={"text": text})
    except ErrorResponse as e:
        logger.error('Failed creating transcription on element {}: {} - {}'.format(
            element['id'], e.status_code, e.content))
        return

    # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateMetaData
    if region["type_act"] == "AI":
        place = "initial"
    elif region["type_act"] == "AF":
        place = "final"
    elif region["type_act"] == "AM":
        place = "middle"
    elif region["type_act"] == "AS":
        place = "supplemental"
    elif region["type_act"] == "AC":
        place = "complete"
    try:
        body = {"type": "text", "name": "Part", "value": place}
        logger.info(f'creating metadata {body}')
        ark_client.request("CreateMetaData", id=element['id'], body=body)
    except ErrorResponse as e:
        logger.error('Failed creating metadata on element {}: {} - {}'.format(
            element['id'], e.status_code, e.content))

def main():
    """Collect arguments and run."""
    parser = argparse.ArgumentParser(
        description='import act polygons and information from json file',
    )
    parser.add_argument(
        '--json',
        help="path to the json file containing the acts' information",
        type=Path,
        required=True
    )
    args = vars(parser.parse_args())
    # log in on arkindex with your credentials
    ark_client.configure(**options_from_env())
    parse_json(args['json'])


if __name__ == '__main__':
    main()
