import io
import csv
import json
import pathlib
import datetime

import minio
import urllib3


def export_to_csv():
    bucket_name = "datagouv"

    try:
        client = minio.Minio("localhost:9000", "minioadmin", "miniopassword", secure=False)
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except urllib3.exceptions.MaxRetryError as e:
        print("Minio Connection failed", e)
        return

    file = pathlib.Path('data/datasets_filtered.json')
    with pathlib.Path('data/datasets_filtered.json').open() as f:
        datasets = json.load(f)
    print(len(datasets))

    fields = "id,title,slug,metrics,organization,page,description,tags".split(',')
    with open(file.with_suffix('.csv'), 'w', encoding='UTF8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for entry in datasets:
            for json_field in ["metrics", "organization", "tags"]:
                if entry[json_field]:
                    entry[json_field] = json.dumps(entry[json_field])
            writer.writerow(entry)

    folder = datetime.datetime.now().strftime("%Y-%m-%d")

    with open(file.with_suffix('.csv'), "rb") as f:
        result = client.put_object(
            bucket_name,
            f"{folder}/{file.with_suffix('.csv').name}",
            data=io.BytesIO(f.read()),
            length=file.with_suffix('.csv').stat().st_size,
        )
        print(
            "created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id,
            ),
        )


if __name__ == '__main__':
    export_to_csv()
