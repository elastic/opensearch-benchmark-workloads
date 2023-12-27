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


class QueryIteratorParamSource:
    def __init__(self, workload, params, **kwargs):
        self.track = workload
        self._params = params
        self.kwargs = kwargs
        self._batch_size = self._params.get("batch_size", 100000)
        self._random_seed = self._params.get("seed", None)
        self._sample_queries = query_samples(self._batch_size, self._random_seed)
        self._queries_iterator = None

    def size(self):
        return None

    def partition(self, partition_index, total_partitions):
        if self._queries_iterator is None:
            self._queries_iterator = iter(self._sample_queries)
        return self


class QueryParamSource(QueryIteratorParamSource):
    def __init__(self, workload, params, **kwargs):
        super().__init__(workload, params, **kwargs)
        self._index_name = params.get(
            "index", workload.indices[0].name if len(workload.indices) == 1 else "_all"
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
