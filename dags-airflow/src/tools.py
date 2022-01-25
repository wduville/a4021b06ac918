__author__ = 'wduville'

import time
import requests


def run_query(params: dict = None, headers: dict = None, base_url: str = "https://www.data.gouv.fr/api/1/datasets/"):
    request = requests.get(url=base_url, params=params, headers=headers)
    if request.status_code == 200:
        return request.json()
    raise Exception(f"Query failed to run by returning code of {request.status_code}: {request.reason}. {params}")


class Timer:
    def __init__(self, tag="", text=""):
        self.text = text
        self.tag = tag
        self.original_func_name = ""

    def __enter__(self):
        self.start = time.perf_counter()
        self.start2 = time.process_time()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.interval = self.end - self.start
        print(f"[{self.tag}.{self.original_func_name}] {self.text} : done in {self.interval:.3f} sec "
              f"| CPU time: {time.process_time() - self.start2:.3f}")

    def __call__(self, func):
        self.original_func_name = func.__name__

        def wrapper( *args, **kwargs):
            self.__enter__()
            data = func(*args, **kwargs)
            self.__exit__()
            return data
        return wrapper
