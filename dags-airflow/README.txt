Hard limit, impossible to request after the 40,000th dataset
result = run_query({'page': 40000, 'page_size': 1}, headers={'X-Fields': xfields})

Success
# https://www.data.gouv.fr/api/1/datasets/?page=40000&page_size=1
Fail
# https://www.data.gouv.fr/api/1/datasets/?page=40001&page_size=1