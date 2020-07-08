import re
from typing import List, Dict
from pathlib import Path
import pkg_resources

from tree_sitter import Tree, Node

from tree_hugger.core.code_parser import BaseParser, match_from_span
from tree_hugger.core.queries import Query


class PHPParser(BaseParser):
	
    QUERY_FILE_PATH = "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        query_file_content = pkg_resources.resource_string(__name__, PHPParser.QUERY_FILE_PATH)\
                                          .decode("utf-8")
        query = Query.fromString(query_file_content)
        super(PHPParser, self).__init__('python', 'python_queries', query, library_loc)

    def get_all_class_method_names(self) -> List:
        """
        Gets all the method names from a file. 

        A method is a function defined inside a class
        """
        captures = self._run_query_and_get_captures('all_class_methods', self.root_node)
        ret_struct = {}
        current_key = ""
        for tpl in captures:
            if tpl[1] == "class.name":
                current_key = match_from_span(tpl[0], self.splitted_code)
                ret_struct[current_key] = []
                continue
            else:
                ret_struct[current_key].append(match_from_span(tpl[0], self.splitted_code))
        return ret_struct

    def get_all_function_names(self) -> List:
        """
        Gets all function names from a file.

        It excludes all the methods, i.e. functions defined inside a class
        """
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        methods = self.get_all_class_method_names()
        all_methods = set([method_name  for key, value in methods.items() for method_name in value])

        return list(all_funcs - all_methods)
    
