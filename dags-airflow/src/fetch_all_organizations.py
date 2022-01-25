import datetime
import io
import json
import csv

import pymongo
import pymongo.errors
import minio
import urllib3

from src.tools import run_query


def push_to_mongo(data, ):
    try:
        client = pymongo.MongoClient(host="localhost", port=27017, connect=False)
        # Triggering db connection
        client.list_database_names()
    except pymongo.errors.ServerSelectionTimeoutError as e:
        #
        # Fallback to wsl2 docker hostnames if connection to 'localhost' fails
        #
        print("Switching to mongodb:27017", e)
        client = pymongo.MongoClient(host="mongodb", port=27017, connect=False)

    database_name = 'datagouv'
    collection_name = 'tops'

    database = client[database_name]
    collection = database[collection_name]
    collection.insert_many(data)


def get_datasets_filtered():
    folder = datetime.datetime.now().strftime("%Y-%m-%d")
    file = f'{folder}/datasets_filtered.csv'
    bucket_name = "datagouv"

    try:
        client = minio.Minio("localhost:9000", "minioadmin", "miniopassword", secure=False)
        client.bucket_exists(bucket_name)
    except urllib3.exceptions.MaxRetryError as e:
        #
        # Fallback to wsl2 docker hostnames if connection to 'localhost' fails
        #
        print("Switching to minio:9000", e)
        client = minio.Minio("minio:9000", "minioadmin", "miniopassword", secure=False)

    try:
        response = client.get_object(bucket_name, file)
        stream = response.read()
        reader = csv.DictReader(io.StringIO(stream.decode('utf-8')))

        data = []
        for row in reader:
            for json_field in ["metrics", "organization", "tags"]:
                if row[json_field]:
                    row[json_field] = json.loads(row[json_field])
            data.append(row)
        return data
    finally:
        response.close()
        response.release_conn()


def fetch_all_push_mongo():
    result = run_query(base_url="https://www.data.gouv.fr/api/1/organizations/", params={'sort': "-followers", 'page_size': 30})
    organizations = result['data']
    print(len(organizations), "items")
    with open(f'data/organizations_by_followers_top_30.json', 'w') as f:
        json.dump(obj=result, fp=f, indent=2)

    datasets_filtered = get_datasets_filtered()
    organizations_dict = {o["id"]: o for o in organizations}

    datasets_filtered_by_top30_organizations = [
        {
            'id': dataset['id'],
            'title': dataset['title'],
            'followers': dataset['metrics']['followers'],
            'organization_name': dataset['organization']['name'],
            'organization_id': dataset['organization']['id'],
            'organization_followers': organizations_dict[dataset['organization']['id']]['metrics']['followers'],
        }
        for dataset in datasets_filtered
        if dataset["organization"] and dataset["organization"]["id"] in organizations_dict
        # Some datasets do not have organizations attached
    ]

    print(len(datasets_filtered_by_top30_organizations))
    push_to_mongo(datasets_filtered_by_top30_organizations)


if __name__ == '__main__':
    fetch_all_push_mongo()
