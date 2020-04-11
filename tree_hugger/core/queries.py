import os
import logging
from pathlib import Path
from collections import UserDict

import yaml

import tree_hugger.setup_logging
from tree_hugger.exceptions import QueryFileNotFoundError


class Query(UserDict):

    data = {}

    def __init__(self, query_file_path: str):
        if not Path(query_file_path).exists() or not Path(query_file_path).is_file():
            raise QueryFileNotFoundError(f"Cound not find {query_file_path}")
        
        with open(query_file_path) as f:
            self.update(yaml.load(f, Loader=yaml.FullLoader))
