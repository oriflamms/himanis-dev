from pathlib import Path
import argparse
from arkindex import ArkindexClient, options_from_env
from apistar.exceptions import ErrorResponse
import logging
import tqdm


# create an arkindex client
ark_client = ArkindexClient()

# The id of the Himanis corpus on Arkindex
CORPUS_ID = "ed249464-96c5-4ca6-a717-f99fc9bf4ce6"

# logger configuration
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# TODO: add function that parses the json file and itterates over the acts
def parse_json(json_file):
    # TODO: get the acts in order to itterate over them
    for act in tqdm(acts):
        # get the volume's arkindex id of the act
        volume_id = get_volume_id(act["Volume"])
        if volume_id:
            # now we have to get the page that is in this volume that has the same name as the Folio_start attribute in the json file
            page = get_page(volume_id, act["Folio_start"])
            if page:
                # not sure if you want the name of the element to be act["Act_N"] or the name starting with Acte_xx so this is up to you to decide
                push_element(page, act["Act_N"], act["Text_Region"])
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
        volume_name = "France, Paris, Archives nationales, "+ volume_name
    # try a request to the api to get the volume with the name volume_name
    try:
        # call to the API for this endpoint https://arkindex.teklia.com/api-docs/#operation/ListElements
        volumes = ark_client.paginate("ListElements", corpus=CORPUS_ID, body={"name": volume_name})
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
    try:
        # call to the API for this endpoint https://arkindex.teklia.com/api-docs/#operation/ListElementChildren
        pages = ark_client.paginate("ListElementChildren", id=volume_id, body={"name": page_name})
    except ErrorResponse as e:
        logger.error('Failed getting folder elements {} with name {}: {} - {}'.format(
            volume_id, page_name, e.status_code, e.content))
    for page in pages:
        if page["name"] == page_name:
            return page
    return None

def push_element(page, act_name, json_act):
    # create the element on the page
    # turn text representation of the coordinates into list of coordinates
    polygon = json_act["Graphical_coord"]
    polygon = polygon.split(" ")
    coordinates = []
    for coor in polygon:
        coor = coor.split(",")
        coordinates.append([int(coor[0]), int(coor[1])])
    # request to the API using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateElement
    try:
        element = ark_client("CreateElement", body={"type": "act", "name": act_name, "corpus": CORPUS_ID, "parent": page['id'], "image": page["zone"]["image"]["id"], "polygon": polygon})
    except ErrorResponse as e:
        logger.error('Failed creating element {}: {} - {}'.format(
            act_name, e.status_code, e.content))
    # if the element was created, add transcription to the element
    text = json_act["Texte"].join("\n")
    # request to the api using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateTranscription
    try:
        transcription = ark_client("CreateTranscription", id= element['id'], body={"text": text})
    except ErrorResponse as e:
        logger.error('Failed creating transcription on element {}: {} - {}'.format(
            element_id, e.status_code, e.content))

    # TODO: if you want to add other information like the date or the type of the act you can add them as metadata on the element using this endpoint https://arkindex.teklia.com/api-docs/#operation/CreateMetaData 

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

    




if __name__ == '__main__':
    main()