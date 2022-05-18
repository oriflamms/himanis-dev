# script to push json transcriptions on arkindex pages

## usage
You should run this code in a virtual env.
In order to create it you can use the following command:
`virtualenv -p python3 .env`
and the activate it
`source .env/bin/activate`
and install the requirements
`pip install requirements.txt`
then you should export your arkindex token as environment variables
```
export ARKINDEX_API_TOKEN=<your token>
export ARKINDEX_API_URL=https://arkindex.teklia.com/
```
you can find your API token on this [page](https://arkindex.teklia.com/user/profile) when you're connected on your account on arkindex

To run the script you need to run this command:
`python import_json.py --json <path to your json file>` 

## Things that need to be done:

* parsing the json file
* cases where the act is on multiple pages
* adding other information about the act as metadata

## Extra information

* [arkindex corpus](https://arkindex.teklia.com/browse/ed249464-96c5-4ca6-a717-f99fc9bf4ce6?top_level=true&folder=true&order=name&order_direction=asc)
* [arkindex api](https://arkindex.teklia.com/api-docs/#operation/CreateTranscription)