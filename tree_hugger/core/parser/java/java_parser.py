import re
from typing import List, Dict
from pathlib import Path

from tree_sitter import Tree, Node, TreeCursor

from tree_hugger.core.code_parser import BaseParser, match_from_span
from tree_hugger.core.queries import Query


class JavaParser(BaseParser):
	
    QUERY_FILE_PATH = Path(__file__).parent / "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(JavaParser, self).__init__('java', 'java_queries', JavaParser.QUERY_FILE_PATH, library_loc)

    
    def get_all_class_names(self) -> List[str]:
        """
        Returns a list of all class names present in a file
        """
        captures = self._run_query_and_get_captures('all_class_names', self.root_node)
        return [match_from_span(t[0], self.splitted_code) for t in captures]

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
        
    def get_all_method_bodies(self) -> Dict[str, str]:
        """
        Returns a dict where methods names are the key and the whole function code are the values
        """
        captures = self._run_query_and_get_captures('all_method_bodies', self.root_node)
        
        method_bodies = {}
        for i in range(0, len(captures), 2):
            method_name = match_from_span(captures[i][0], self.splitted_code)
            method_bodies[method_name] = match_from_span(captures[i+1][0], self.splitted_code)

        return method_bodies
    
    def get_all_method_names_with_params(self) -> Dict[str, str]:
        """
        Returns a dictionary with all the function names and their params
        """
        captures = self._run_query_and_get_captures('all_method_names_and_params', self.root_node)
        ret_struct = {}
        i = 0
        while i < len(captures):
            if captures[i][1] == "class.name":
                current_class = match_from_span(captures[i][0], self.splitted_code)
                ret_struct[current_class] = {}
                i += 1
            elif captures[i][1] == "method.name":
                method_name = match_from_span(captures[i][0], self.splitted_code)
                ret_struct[current_class][method_name] = []
                for param in captures[i+1][0].children:
                    if param.type == "formal_parameter":
                        name = match_from_span(
                            param.child_by_field_name("name"),
                            self.splitted_code
                        )
                        typ = match_from_span(
                            param.child_by_field_name("type"),
                            self.splitted_code
                        )
                    elif param.type == "spread_parameter":
                        name = match_from_span(
                            param.children[2],
                            self.splitted_code
                        )
                        typ = match_from_span(
                            param.children[0],
                            self.splitted_code
                        )
                    else:
                        continue
                    ret_struct[current_class][method_name].append((name,typ))
                i += 2
        
        return ret_struct

    def _walk_recursive_javadoc(self, cursor: TreeCursor, lines: List, node_type: str, documented: Dict):
        n = cursor.node
        for i in range(len(n.children)):
            if i < len(n.children)-1 and n.children[i].type == "comment" and n.children[i+1].type == node_type:
                name = str(match_from_span(cursor.node.children[i+1].child_by_field_name("name"), lines))
                documented[name] = str(match_from_span(cursor.node.children[i], lines))
            self._walk_recursive_javadoc(n.children[i].walk(), lines, node_type, documented)

    def get_all_method_javadocs(self) -> Dict[str, str]:
        """
        Returns a dict where method names are the key and the comment docs are the values

        Excludes any functions, i.e., functions defined outside a class.
        """
        documentation = {}
        self._walk_recursive_javadoc(self.root_node.walk(), self.splitted_code, "method_declaration", documentation)
        return documentation
        
    def get_all_method_documentations(self) -> Dict[str, str]:
        """
        Returns a dict where method names are the key and the comment docs are the values

        Excludes any functions, i.e., functions defined outside a class.
        """
        return self.get_all_method_javadocs()
   
    def get_all_class_javadocs(self) -> Dict[str, str]:
        """
        Returns the comment docs of all classes
        """
        documentation = {}
        self._walk_recursive_javadoc(self.root_node.walk(), self.splitted_code, "class_declaration", documentation)
        return documentation
   
    def get_all_class_documentations(self) -> Dict[str, str]:
        """
        Returns the comment docs of all classes
        """
        return self.get_all_class_javadocs()

        
