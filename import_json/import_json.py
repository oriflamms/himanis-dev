from pathlib import Path
import argparse
from arkindex import ArkindexClient, options_from_env
from apistar.exceptions import ErrorResponse
import logging
from tqdm import tqdm
import json

# create an arkindex client
ark_client = ArkindexClient()

# The id of the Himanis corpus on Arkindex
CORPUS_ID = "dbf1fc04-d825-4a3a-b3e4-60ff010a9480"

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
                    # now we have to get the page that is in this volume that has the same name as the Folio_start attribute in the json file
                    page = get_page(volume_id, act["Folio_start"])
                    if page:
                        for region in act["Text_Region"]:
                            None
                            # not sure if you want the name of the element to be act["Act_N"] or the name starting with Acte_xx so this is up to you to decide
                            #push_element(page, act["Act_N"], region, act)
                    else:
                        continue
                else:
                    continue


def get_volume_id(volume_name):
    """
    function that gets the volume's arkindex id of the act
    input: volume_name the name of the
    """
    if "JJ" in volume_name:
        volume_name = volume_name.replace("JJ", "JJ ")
        volume_name = "PARIS, Archives nationales, " + volume_name
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
        print(page['zone']['image']['url'])
        if page["name"] == page_name:
            return page
    return None


def push_element(page, act_name, json_act, data):
    # create the element on the page
    # turn text representation of the coordinates into list of coordinates
    polygon = json_act["Graphical_coord"]  # TODO : Gérer les cas avec plusieurs zones par acte
    polygon = polygon.split(" ")
    coordinates = []
    for coor in polygon:
        coor = coor.split(",")
        coor = [int(coor[0]), int(coor[1])]
        dim = [max([t[0] for t in page["zone"]["polygon"]]), max([t[1] for t in page["zone"]["polygon"]])]
        for t in range(0, 1):  # Check that the coordinates do not exceed the page
            if coor[t] > dim[t]:
                coor[t] = dim[t]
        coordinates.append(coor)
    # request to the API using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateElement
    try:
        body = {"type": "act", "name": act_name, "corpus": CORPUS_ID, "parent": page['id'], "image": page["zone"]["image"]["id"], "polygon": coordinates}
        logger.info(f'creating element with body {body}')
        element = ark_client.request("CreateElement", body=body)
    except ErrorResponse as e:
        logger.error('Failed creating element {}: {} - {}'.format(act_name, e.status_code, e.content))
        return
    # if the element was created, add transcription to the element
    text = '\n'.join(json_act["Texte"])

    # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateTranscription
    try:
        logger.info(f'add transcription {text}')
        transcription = ark_client.request("CreateTranscription", id=element['id'], body={"text": text})
    except ErrorResponse as e:
        logger.error('Failed creating transcription on element {}: {} - {}'.format(
            element_id, e.status_code, e.content))
        return
    for e in data:
        if e in ["Folio_start", "Folio_end", "Act_N", "Language", "Date", "Regeste"]:
            # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateMetaData
            try:
                body={"type": "text", "name": e, "value": data[e]}
                logger.info(f'creating metadata {body}')
                metadata = ark_client.request("CreateMetaData", id=element['id'], body=body)
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
