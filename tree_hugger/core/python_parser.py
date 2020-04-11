import re
from typing import List, Dict

from tree_sitter import Tree, Node

from tree_hugger.core.code_parser import BaseParser, match_from_span


class PythonParser(BaseParser):

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(PythonParser, self).__init__('python', library_loc, query_file_path)
    
    def _strip_py_doc_string(self, dt: str):
        try:
            if dt.startswith('"""'):
                regex = r"\"{3}[\s\S]*?\"{3}"
            elif dt.startswith("'''"):
                regex = r"\'{3}[\s\S]*?\'{3}"
            elif dt.startswith('r"""'):  # For Spinhx (numpy) style docstring with \ escapes
                # Check this - https://stackoverflow.com/questions/46543194/does-r-stand-for-something-in-sphinx
                regex = r"r\"{3}[\s\S]*?\"{3}"
            elif dt.startswith("r'''"):  # For Spinhx (numpy) style docstring with \ escapes
                regex = r"r\'{3}[\s\S]*?\'{3}"
            if regex is None:
                print(dt)
            matches = re.search(regex, dt)
            return matches.group()
        except UnboundLocalError:
            return ""
    
    def get_all_class_method_names(self) -> Dict:
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

    def get_all_function_names(self):
        captures = self._run_query_and_get_captures('all_function_names', self.root_node)
        all_funcs = set([match_from_span(n[0], self.splitted_code) for n in captures])

        methods = self.get_all_class_method_names()
        all_methods = set([method_name  for key, value in methods.items() for method_name in value])

        return list(all_funcs - all_methods)
    
    def get_all_function_docstrings(self) -> Dict:
        function_names = self.get_all_function_names()
        captures = self._run_query_and_get_captures('all_function_doctrings', self.root_node)
        ret_struct = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                ret_struct[func_name] = self._strip_py_doc_string(match_from_span(
                                                                  captures[i+1][0], self.splitted_code
                                                                  ))
        return ret_struct
    
    def get_all_method_docstrings(self):
        captures = self._run_query_and_get_captures('all_class_method_docstrings', self.root_node)
        ret_struct = {}
        current_class = ""
        current_method = ""
        for tpl in captures:
            if tpl[1] == "class.name":
                current_class = match_from_span(tpl[0], self.splitted_code)
                ret_struct[current_class] = {}
                continue
            elif tpl[1] == "method.name":
                current_method = match_from_span(tpl[0], self.splitted_code)
                ret_struct[current_class][current_method] = ""
                continue
            elif tpl[1] == "method.docstr":
                ret_struct[current_class][current_method] = self._strip_py_doc_string(match_from_span(
                                                                                      tpl[0], self.splitted_code
                                                                                      ))
        return ret_struct