import re
from typing import List, Dict
from pathlib import Path

from tree_sitter import Tree, Node, TreeCursor

from tree_hugger.core.code_parser import BaseParser, match_from_span
from tree_hugger.core.queries import Query


class CPPParser(BaseParser):
	
    QUERY_FILE_PATH = Path(__file__).parent / "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(CPPParser, self).__init__('cpp', 'cpp_queries', CPPParser.QUERY_FILE_PATH, library_loc)

    def get_all_function_names(self) -> List[str]:
        """
        Gets all function names from a file.

        It excludes all the methods, i.e. functions defined inside a class
        """
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        return list(all_funcs)

    def _walk_recursive_methods(self, cursor: TreeCursor, lines: List):
        n = cursor.node
        methods = []
        for c in n.children:
            if c.type == "function_definition":
                method_name = str(match_from_span(c.child_by_field_name("declarator").child_by_field_name("declarator"), lines))
                methods.append(method_name)
            else:
                methods.extend(self._walk_recursive_methods(c.walk(), lines))
        return methods

    def get_all_class_method_names(self) -> List[str]:
        """
        Gets all the method names from a file. 

        A method is a function defined inside a class
        """
        captures = self._run_query_and_get_captures('all_class_methods', self.root_node)

        return {
            str(match_from_span(node.child_by_field_name("name"), self.splitted_code)):
            self._walk_recursive_methods(node.walk(), self.splitted_code)
            for (node,_) in captures
        }
        
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
    
    def get_all_function_names_with_params(self) -> Dict[str, str]:
        """
        Returns a dictionary with all the function names and their params
        """
        captures = self._run_query_and_get_captures('all_function_names_and_params', self.root_node)
        ret_struct = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            ret_struct[func_name] = []
            for param in captures[i+1][0].children:
                if param.type == "parameter_declaration":
                    name = match_from_span(
                        param.child_by_field_name("declarator"),
                        self.splitted_code
                    )
                    typ = match_from_span(
                        param.child_by_field_name("type"),
                        self.splitted_code
                    )
                    value = None
                elif param.type == "optional_parameter_declaration":
                    name = match_from_span(
                        param.child_by_field_name("declarator"),
                        self.splitted_code
                    )
                    typ = match_from_span(
                        param.child_by_field_name("type"),
                        self.splitted_code
                    )
                    value = match_from_span(
                        param.child_by_field_name("default_value"),
                        self.splitted_code
                    )
                else:
                    continue
                ret_struct[func_name].append((name,typ,value))
            
        
        return ret_struct

    def _walk_recursive_classdoc(self, cursor: TreeCursor, lines: List, documented: Dict):
        n = cursor.node
        for i in range(len(n.children)):
            if i < len(n.children)-1 and n.children[i].type == "comment" and n.children[i+1].type == "class_specifier":
                name = str(match_from_span(cursor.node.children[i+1].child_by_field_name("name"), lines))
                documented[name] = str(match_from_span(cursor.node.children[i], lines))
            self._walk_recursive_classdoc(n.children[i].walk(), lines, node_type, documented)
    
    def _walk_recursive_functiondoc(self, cursor: TreeCursor, lines: List, documented: Dict):
        n = cursor.node
        for i in range(len(n.children)):
            if i < len(n.children)-1 and n.children[i].type == "comment" and n.children[i+1].type == "function_definition":
                name = str(match_from_span(cursor.node.children[i+1].child_by_field_name("declarator").child_by_field_name("declarator"), lines))
                documented[name] = str(match_from_span(cursor.node.children[i], lines))
            self._walk_recursive_functiondoc(n.children[i].walk(), lines, node_type, documented)

    def get_all_function_commentdocs(self) -> Dict[str, str]:
        """
        Returns a dict where function names are the key and the comment docs are the values

        Excludes any methods, i.e., functions defined inside a class.
        """
        documentation = {}
        # TODO correct error : the comment of methods are also extracted
        self._walk_recursive_functiondoc(self.root_node.walk(), self.splitted_code, documentation)
        return documentation
        
    def get_all_function_documentations(self) -> Dict[str, str]:
        """
        Returns a dict where function names are the key and the comment docs are the values

        Excludes any methods, i.e., functions defined inside a class.
        """
        # TODO correct error : the comment of methods are also extracted
        return self.get_all_function_commentdocs()
   
    def get_all_class_documentations(self) -> Dict[str, str]:
        """
        Returns the comment docs of all classes
        """
        return self.get_all_class_commentdocs()

        
