import csv
import math
import random
import re
from os import getcwd
from os.path import dirname
from typing import Iterator, List

QUERIES_DIRNAME: str = dirname(__file__)
QUERIES_FILENAME: str = f"{QUERIES_DIRNAME}/queries.csv"

SEARCH_APPLICATION_ROOT_ENDPOINT: str = "/_application/search_application"

QUERY_CLEAN_REXEXP = regexp = re.compile("[^0-9a-zA-Z]+")


def query_samples(k: int, random_seed: int = None) -> List[str]:
    with open(QUERIES_FILENAME) as queries_file:
        csv_reader = csv.reader(queries_file)
        next(csv_reader)
        queries_with_probabilities = list(tuple(line) for line in csv_reader)

        queries = [
            QUERY_CLEAN_REXEXP.sub(" ", query).lower()
            for query, _ in queries_with_probabilities
        ]
        probabilities = [
            float(probability) for _, probability in queries_with_probabilities
        ]
        random.seed(random_seed)

        return random.choices(queries, weights=probabilities, k=k)


class QueryParamSource:
    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def __init__(self, workload, params, **kwargs):
        self._params = params
        self.infinite = True
        cwd = os.path.dirname(__file__)
        # The terms.txt file has been generated with:
        # sed -n '13~250p' [path_to_benchmark_data]/geonames/documents.json | shuf | sed -e "s/.*name\": \"//;s/\",.*$//" > terms.txt
        with open(os.path.join(cwd, "terms.txt"), "r") as ins:
            self.terms = [line.strip() for line in ins.readlines()]

    # We need to stick to the param source API
    # noinspection PyUnusedLocal
    def partition(self, partition_index, total_partitions):
        return self

    def __init__(self, track, params, **kwargs):
        super().__init__(track, params, **kwargs)
        self._index_name = params.get(
            "index", track.indices[0].name if len(track.indices) == 1 else "_all"
        )
        self._cache = params.get("cache", True)

    def params(self):
        try:
            result = {
                "body": {
                    "query": {
                        "query_string": {
                            "query": next(self._queries_iterator),
                            "default_field": self._params["search-fields"],
                        }
                    }
                },
                "size": self._params["size"],
                "index": self._index_name,
                "cache": self._cache,
            }

            return result
        except StopIteration:
            self._queries_iterator = iter(self._sample_queries)
            return self.params()


def register(registry):
    registry.register_param_source("query-string-search", QueryParamSource)
