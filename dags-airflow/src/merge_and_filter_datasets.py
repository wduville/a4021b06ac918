import pathlib
import json
import os

import slugify


def merge_and_filter_datasets():
    print("OSNAME", os.name)
    datasets = []
    for file in pathlib.Path('data').glob('datasets_page_*_size_*.json'):
        print(file)
        with file.open() as f:
            data = json.load(f)
            datasets.extend(data["data"])

    print(len(datasets))

    datasets_filtered = []
    for search_term in ["mobilité", "transport"]:
        data = filter_term(term=search_term, datasets=datasets)
        datasets_filtered.extend(data)
        print(search_term, len(data))

    with open(f'data/datasets_filtered.json', 'w') as f:
        json.dump(data, fp=f, indent=2)


def filter_term(term: str, datasets: list) -> list:
    term = term.lower()
    slug = slugify.slugify(term)
    return [
        dataset
        for dataset in datasets
        if term in dataset["title"].lower()
        or term in dataset["description"].lower()
        or slug in dataset["slug"]
        or slug in slugify.slugify(dataset["description"].lower())
        or slug in dataset["tags"]
        # or unidecode.unidecode(term) in unidecode.unidecode(dataset["description"])
        # or "resources" in dataset and any(term in resource["description"] or term in resource["title"] for resource in dataset["resources"])
    ]


if __name__ == '__main__':
    merge_and_filter_datasets()

