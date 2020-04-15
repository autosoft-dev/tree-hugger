import re
from typing import List, Dict
import logging

from tree_sitter import Tree, Node

from tree_hugger.core.code_parser import BaseParser, match_from_span
import tree_hugger.setup_logging

TRIPPLE_QUOTE = '"""'
TRIPPLE_SINGLE_QUOTE = "'''"
TRIPPLE_QUOTE_NUMPY_STYLE = 'r"""'
TRIPPLE_SINGLE_QUOTE_NUMPY_STYLE = "r'''"

starts_with_tripple_quote = lambda x: x.startswith(TRIPPLE_QUOTE)
starts_with_tripple_single_quote = lambda x: x.startswith(TRIPPLE_SINGLE_QUOTE)
starts_with_numpy_style_tripple_quote = lambda x: x.startswith(TRIPPLE_QUOTE_NUMPY_STYLE)
starts_with_numpy_style_tripple_single_quote = lambda x: x.startswith(TRIPPLE_SINGLE_QUOTE_NUMPY_STYLE)


class PythonParser(BaseParser):
    """
    The PythonParser class, extending the BaseParser and supplying some easy-to-use API s for mining code files
    """

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(PythonParser, self).__init__('python', library_loc, query_file_path)
    
    def _strip_py_doc_string(self, dt: str, strip_quotes: bool) -> str:
        try:
            if starts_with_tripple_quote(dt):
                regex = r"\"{3}[\s\S]*?\"{3}"
            elif starts_with_tripple_single_quote(dt):
                regex = r"\'{3}[\s\S]*?\'{3}"
            elif starts_with_numpy_style_tripple_quote(dt):  # For Spinhx (numpy) style docstring with \ escapes
                # Check this - https://stackoverflow.com/questions/46543194/does-r-stand-for-something-in-sphinx
                regex = r"r\"{3}[\s\S]*?\"{3}"
            elif starts_with_numpy_style_tripple_single_quote(dt):  # For Spinhx (numpy) style docstring with \ escapes
                regex = r"r\'{3}[\s\S]*?\'{3}"
            if regex is None:
                logging.info(f"not a docstring {dt}")
            matches = re.search(regex, dt)
            return_dt = matches.group()
            if not strip_quotes:
                return return_dt.lstrip().rstrip()
            else:
                return return_dt.replace('"""', "").rstrip().lstrip() if return_dt.find('"""') != -1 else return_dt.replace("'''", "").rstrip().lstrip()
        except UnboundLocalError:
            return ""
    
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
    
    def get_all_function_docstrings(self, strip_quotes: bool=False) -> Dict:
        """
        Returns a dict where function names are the key and the docstrings are the values

        Excludes any methods, i.e., functions defined inside a class.

        Optional argugmet "strip_quotes" gives the choice whether the docstring returned 
        will be strippted out of tripple quotes or not. Default: False
        """
        function_names = self.get_all_function_names()
        captures = self._run_query_and_get_captures('all_function_doctrings', self.root_node)
        ret_struct = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                ret_struct[func_name] = self._strip_py_doc_string(match_from_span(
                                                                  captures[i+1][0], self.splitted_code
                                                                  ), strip_quotes)
        return ret_struct
    
    def get_all_method_docstrings(self, strip_quotes: bool=False) -> Dict:
        """
        Returns a dict where method names are the key and the docstrings are the values

        Excludes any functions, i.e., functions defined outside a class.

        Optional argugmet "strip_quotes" gives the choice whether the docstring returned 
        will be strippted out of tripple quotes or not. Default: False
        """
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
                                                                                      ), strip_quotes)
        return ret_struct
    
    def get_all_function_bodies(self, strip_docstr: bool=False) -> Dict:
        """
        Returns a dict where function names are the key and the whole function code are the values

        Excludes any methods, i.e., functions defined inside a class.

        Optional argugmet "strip_docstr" gives the choice whether the docstring should
        be returned as a part of the function body or separately.
        """
        function_names = self.get_all_function_names()
        func_and_params = self.function_names_with_params()
        func_and_docstr = self.get_all_function_docstrings()
        captures = self._run_query_and_get_captures('all_function_bodies', self.root_node)
        ret_struct = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                ret_struct[func_name] = match_from_span(captures[i+1][0], self.splitted_code)
        
        if strip_docstr:
            for k, v in ret_struct.items():
                first_quote_pos = -1
                first_quote_pos = v.find(TRIPPLE_QUOTE) if starts_with_tripple_quote(v) else v.find(TRIPPLE_SINGLE_QUOTE)
                if first_quote_pos == -1:
                    first_quote_pos = v.find(TRIPPLE_QUOTE_NUMPY_STYLE) if starts_with_numpy_style_tripple_quote(v) else v.find(TRIPPLE_SINGLE_QUOTE_NUMPY_STYLE)
                if first_quote_pos != -1:
                    next_quote_pos = v.find(TRIPPLE_QUOTE, first_quote_pos+1) if v.startswith(TRIPPLE_QUOTE) else v.find(TRIPPLE_SINGLE_QUOTE, first_quote_pos+1)
                    next_quote_pos = next_quote_pos + 3
                    ret_struct[k] = (f"def {k}{func_and_params[k]}:{v[next_quote_pos:]}", func_and_docstr[k])
                else:
                    ret_struct[k] = (f"def {k}{func_and_params[k]}:\n    {v}", "")
        else:
            for k, v in ret_struct.items():
                ret_struct[k] = f"def {k}{func_and_params[k]}:\n    {v}"
        return ret_struct
    
    def function_names_with_params(self, split_params_in_list: bool=False):
        function_names = self.get_all_function_names()
        captures = self._run_query_and_get_captures('all_function_names_and_params', self.root_node)
        ret_struct = {}

        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                params = match_from_span(captures[i+1][0], self.splitted_code)
                if split_params_in_list:
                    if params.startswith("(") and params.endswith(")"):
                        params = params[1:-1]
                        params = params.split(",")
                ret_struct[func_name] = params
        
        return ret_struct
