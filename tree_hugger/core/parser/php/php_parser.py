import re
from typing import List, Dict
from pathlib import Path

from tree_sitter import Tree, Node

from tree_hugger.core.code_parser import BaseParser, match_from_span
from tree_hugger.core.queries import Query


class PHPParser(BaseParser):
	
    QUERY_FILE_PATH = Path(__file__).parent / "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(PHPParser, self).__init__('php', 'php_queries', PHPParser.QUERY_FILE_PATH, library_loc)

    def get_all_function_names(self) -> List:
        """
        Gets all function names from a file.

        It excludes all the methods, i.e. functions defined inside a class
        """
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)
        print(captures)
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        methods = self.get_all_class_method_names()
        all_methods = set([method_name  for key, value in methods.items() for method_name in value])

        return list(all_funcs - all_methods)
    
    
