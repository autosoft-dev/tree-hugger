import re
from typing import List, Dict
from pathlib import Path

from tree_sitter import Tree, Node, TreeCursor

from tree_hugger.core.code_parser import BaseParser, match_from_span
from tree_hugger.core.queries import Query


class PHPParser(BaseParser):
	
    QUERY_FILE_PATH = Path(__file__).parent / "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(PHPParser, self).__init__('php', 'php_queries', PHPParser.QUERY_FILE_PATH, library_loc)

    def get_all_function_names(self) -> List[str]:
        """
        Gets all function names from a file.

        It excludes all the methods, i.e. functions defined inside a class
        """
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        return list(all_funcs)

    def get_all_class_method_names(self) -> List[str]:
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

    def get_all_class_names(self) -> List[str]:
        """
        Returns a list of all class names present in a file
        """
        captures = self._run_query_and_get_captures('all_class_names', self.root_node)
        return [match_from_span(t[0], self.splitted_code) for t in captures]
        
    def get_all_function_bodies(self) -> Dict[str, str]:
        """
        Returns a dict where function names are the key and the whole function code are the values

        Excludes any methods, i.e., functions defined inside a class.
        """
        function_names = self.get_all_function_names()
        
        captures = self._run_query_and_get_captures('all_function_bodies', self.root_node)
        
        function_bodies = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                function_bodies[func_name] = match_from_span(captures[i+1][0], self.splitted_code)

        return function_bodies
    
    def function_names_with_params(self) -> Dict[str, str]:
        """
        Returns a dictionary with all the function names and their params
        """
        function_names = self.get_all_function_names()
        captures = self._run_query_and_get_captures('all_function_names_and_params', self.root_node)
        ret_struct = {}

        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                params = match_from_span(captures[i+1][0], self.splitted_code)
                ret_struct[func_name] = params
        
        return ret_struct

    def _walk_recursive_documentation(self, cursor: TreeCursor, lines: List, node_type: str, documented: Dict):
        n = cursor.node
        for i in range(len(n.children)):
            if i < len(n.children)-1 and n.children[i].type == "comment" and n.children[i+1].type == node_type:
                name = str(match_from_span(cursor.node.children[i+1].child_by_field_name("name"), lines))
                documented[name] = str(match_from_span(cursor.node.children[i], lines))
            self._walk_recursive_documentation(n.children[i].walk(), lines, node_type, documented)

    def get_all_function_documentation(self) -> Dict[str, str]:
        """
        Returns a dict where function names are the key and the comment docs are the values

        Excludes any methods, i.e., functions defined inside a class.
        """
        documentation = {}
        self._walk_recursive_documentation(self.root_node.walk(), self.splitted_code, "function_definition", documentation)
        return documentation

    def get_all_method_documentation(self) -> Dict[str, str]:
        """
        Returns a dict where method names are the key and the comment docs are the values

        Excludes any functions, i.e., functions defined outside a class.
        """
        documentation = {}
        self._walk_recursive_documentation(self.root_node.walk(), self.splitted_code, "method_declaration", documentation)
        return documentation
   
    def get_all_class_documentation(self) -> Dict[str, str]:
        """
        Returns the comment docs of all classes
        """
        documentation = {}
        self._walk_recursive_documentation(self.root_node.walk(), self.splitted_code, "class_declaration", documentation)
        return documentation
        
        
