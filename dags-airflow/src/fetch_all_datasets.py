import json
import pathlib

from src.tools import Timer, run_query


def fetch_all_datasets():
    #
    # Note
    #
    # On 25-01-2022 Issue: 500 - "Internal Server Error"
    # Hard limit, impossible to request above the 40,000th dataset
    # Success
    # https://www.data.gouv.fr/api/1/datasets/?page=40000&page_size=1
    # Fail
    # https://www.data.gouv.fr/api/1/datasets/?page=40001&page_size=1
    #

    page_size = 4000
    x_fields = 'total,page,next_page,previous_page,uri,page_size,data{id,title,slug,metrics,organization,page,description,tags}'

    result = run_query({'page': 0, 'page_size': 0}, headers={'X-Fields': 'total'})
    print("Total:", result['total'])

    with Timer("main"):
        for page in range(1, (result['total'] // page_size) + 1):
            with Timer(f"Page {page}"):
                result = run_query({'page': page, 'page_size': page_size}, headers={'X-Fields': x_fields})
                datasets = result['data']
                print(len(datasets), "items")

            filename = pathlib.Path(f'data/datasets_page_{page:02d}_size_{page_size}.json')
            filename.parent.mkdir(exist_ok=True)
            with filename.open('w') as f:
                json.dump(obj=result, fp=f, indent=2)

        print(len(datasets))


if __name__ == '__main__':
    fetch_all_datasets()
