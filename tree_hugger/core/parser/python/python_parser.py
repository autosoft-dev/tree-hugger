import re
from typing import List, Dict
import logging
from pathlib import Path

from tree_sitter import Tree, Node

from tree_hugger.core.queries import Query
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

regex = r"([ ]{2,})"


class PythonParser(BaseParser):
    """
    The PythonParser class, extending the BaseParser and supplying some easy-to-use API s for mining code files

    @TODO - Implement a tree walker.
    """

    QUERY_FILE_PATH = Path(__file__).parent / "queries.yml"

    def __init__(self, library_loc: str=None, query_file_path: str=None):
        super(PythonParser, self).__init__('python', 'python_queries', PythonParser.QUERY_FILE_PATH, library_loc)
    
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
    
    def _outer_indent(self, code):
        spaces_arr = []
        matches = re.finditer(regex, code)
        for _, match in enumerate(matches, start=1):
            spaces_arr.append(len(match.group(0)))
        return min(spaces_arr) if spaces_arr else 4

    
    def get_all_class_method_names(self) -> Dict:
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
        Returns a dict where function names are the key and the documentationd are the values

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
        
    def get_all_function_documentations(self) -> Dict:
        """
        Returns a dict where function names are the key and the docstrings are the values

        Excludes any methods, i.e., functions defined inside a class.
        """
        return self.get_all_function_docstrings()
    
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
    
    def get_all_method_documentations(self, strip_quotes: bool=False) -> Dict:
        """
        Returns a dict where method names are the key and the docstrings are the values

        Excludes any functions, i.e., functions defined outside a class.
        """
        return self.get_all_method_docstrings()
    
    def _get_var_names_as_string_from_param_list(self, param_list):
        return "(" + ", ".join([var_name for var_name, _, _ in param_list]) + ")"
    
    def get_all_class_method_bodies(self, strip_docstr: bool=False, get_index: bool=False) -> Dict:
        class_method_names = self.get_all_class_method_names()
        methods_and_params = self.get_all_function_names_with_params()
        method_and_docstr = self.get_all_method_docstrings()

        captures = self._run_query_and_get_captures('all_function_bodies', self.root_node)

        ret_struct = {}
        pp = {}

        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            for class_name, method_name_list in class_method_names.items():
                if func_name in method_name_list and (func_name != "__init__" and func_name != "__new__"):
                    if pp.get(class_name) is None:
                        pp[class_name] = {}
                        pp[class_name] = {func_name: 
                                          (match_from_span(captures[i+1][0], self.splitted_code), captures[i+1][0].start_point, captures[i+1][0].end_point)
                                          }
                    else:
                        if func_name != "__init__" and func_name != "__new__":
                            pp[class_name][func_name] =  (match_from_span(captures[i+1][0], self.splitted_code), captures[i+1][0].start_point, captures[i+1][0].end_point)

        if strip_docstr:
            for class_name, func_data_struct in pp.items():
                ret_struct[class_name] = {}
                for k, (v,sp,ep) in func_data_struct.items():
                    if method_and_docstr[class_name].get(k) is not None and method_and_docstr[class_name].get(k) is not '':
                        code = v.replace(method_and_docstr[class_name][k], "")
                        outer_indent = self._outer_indent(code)
                        spaces = " ".join([''] * (outer_indent + 1))
                        if code.startswith("\n"):
                            ret_struct[class_name][k] = (f"def {k}{self._get_var_names_as_string_from_param_list(methods_and_params[k])}:{code}", 
                                                         method_and_docstr[class_name][k])
                        else:
                            ret_struct[class_name][k] = (f"def {k}{self._get_var_names_as_string_from_param_list(methods_and_params[k])}:\n{spaces}{code}",
                                                         method_and_docstr[class_name][k])
                    else:
                        outer_indent = self._outer_indent(v)
                        spaces = " ".join([''] * (outer_indent + 1))
                        ret_struct[class_name][k] = (f"def {k}{self._get_var_names_as_string_from_param_list(methods_and_params[k])}:\n{spaces}{v}", "")
                    if get_index:
                        ret_struct[class_name][k] = ret_struct[class_name][k],sp,ep
        else:
            for class_name, func_data_struct in pp.items():
                for k, (v,sp,ep) in func_data_struct.items():
                    outer_indent = self._outer_indent(v)
                    spaces = " ".join([''] * (outer_indent + 1))
                    if ret_struct.get(class_name) is None:
                        ret_struct[class_name] = {}
                        ret_struct[class_name][k] = f"def {k}{self._get_var_names_as_string_from_param_list(methods_and_params[k])}:\n{spaces}{v}"
                    else:
                        ret_struct[class_name][k] = f"def {k}{self._get_var_names_as_string_from_param_list(methods_and_params[k])}:\n{spaces}{v}"
                    if get_index:
                        ret_struct[class_name][k] = (ret_struct[class_name][k], sp, ep)
        return ret_struct
    
    def get_all_function_bodies(self, strip_docstr: bool=False, get_index: bool=False) -> Dict:
        """
        Returns a dict where function names are the key and the whole function code are the values

        Excludes any methods, i.e., functions defined inside a class.

        Optional argugmet "strip_docstr" gives the choice whether the docstring should
        be returned as a part of the function body or separately.
        """
        function_names = self.get_all_function_names()
        func_and_params = self.get_all_function_names_with_params()
        func_and_docstr = self.get_all_function_docstrings()

        
        captures = self._run_query_and_get_captures('all_function_bodies', self.root_node)
        
        ret_struct = {}
        pp = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            if func_name in function_names:
                pp[func_name] = match_from_span(captures[i+1][0], self.splitted_code), captures[i+1][0].start_point, captures[i+1][0].end_point
        
        if strip_docstr:
            for k, (v,sp,ep) in pp.items():
                if func_and_docstr.get(k) is not None and func_and_docstr.get(k) is not '':
                    code = v.replace(func_and_docstr[k], "")
                    outer_indent = self._outer_indent(code)
                    spaces = " ".join([''] * (outer_indent + 1))
                    if code.startswith("\n"):
                        ret_struct[k] = (f"def {k}{self._get_var_names_as_string_from_param_list(func_and_params[k])}:{code}", 
                                         func_and_docstr[k])
                    else:
                        ret_struct[k] = (f"def {k}{self._get_var_names_as_string_from_param_list(func_and_params[k])}:\n{spaces}{code}",
                                         func_and_docstr[k])
                else:
                    outer_indent = self._outer_indent(v)
                    spaces = " ".join([''] * (outer_indent + 1))
                    ret_struct[k] = (f"def {k}{self._get_var_names_as_string_from_param_list(func_and_params[k])}:\n{spaces}{v}", "")
                if get_index:
                    ret_struct[k] = ret_struct[k],sp,ep
        else:
            for k, (v,sp,ep) in pp.items():
                outer_indent = self._outer_indent(v)
                spaces = " ".join([''] * (outer_indent + 1))
                ret_struct[k] = f"def {k}{self._get_var_names_as_string_from_param_list(func_and_params[k])}:\n{spaces}{v}"
                if get_index:
                    ret_struct[k] = ret_struct[k],sp,ep
        return ret_struct
    
    def get_all_function_names_with_params(self):
        """
        Returns a dictionary with all the function names and their params
        """
        captures = self._run_query_and_get_captures('all_function_names_and_params', self.root_node)
        ret_struct = {}
        for i in range(0, len(captures), 2):
            func_name = match_from_span(captures[i][0], self.splitted_code)
            params = []
            for param in captures[i+1][0].children:
                if param.type == 'identifier':
                    name = match_from_span(param, self.splitted_code)
                    typ = None
                    default_value = None
                elif param.type == 'typed_parameter':
                    name = match_from_span(param.children[0], self.splitted_code)
                    typ = match_from_span(param.child_by_field_name("type"), self.splitted_code)
                    default_value = None
                elif param.type == 'default_parameter':
                    name = match_from_span(param.child_by_field_name("name"), self.splitted_code)
                    typ = None
                    default_value = match_from_span(param.child_by_field_name("value"), self.splitted_code)
                elif param.type == 'typed_default_parameter':
                    name = match_from_span(param.child_by_field_name("name"), self.splitted_code)
                    typ = match_from_span(param.child_by_field_name("type"), self.splitted_code)
                    default_value = match_from_span(param.child_by_field_name("value"), self.splitted_code)
                else:
                    continue
                params.append((name, typ, default_value))
            ret_struct[func_name] = params        
        return ret_struct
    
    def get_all_class_names(self) -> List[str]:
        """
        Returns a list of all class names present in a file
        """
        captures = self._run_query_and_get_captures('all_class_names', self.root_node)
        return [match_from_span(t[0], self.splitted_code) for t in captures]
    
    def get_all_class_docstrings(self, strip_quotes: bool=False) -> Dict[str, str]:
        """
        Returns the docstring of all classes

        Optional argument strip_quotes strips the tripple quotes from both sides
        """
        captures = self._run_query_and_get_captures("all_class_docstrings", self.root_node)

        ret_struct = {}
        for i in range(0, len(captures), 2):
            class_name = match_from_span(captures[i][0], self.splitted_code)
            class_body_node = captures[i+1][0]
            if self._has_children(class_body_node):
                cursor = class_body_node.walk()
                if cursor.goto_first_child() and cursor.node.type == "expression_statement":
                    if cursor.goto_first_child() and cursor.node.type == "string":
                        class_docstr = match_from_span(cursor.node, self.splitted_code)
                        if strip_quotes:
                            class_docstr = self._strip_py_doc_string(class_docstr, strip_quotes)
                        ret_struct[class_name] = class_docstr
        return ret_struct
        
    def get_all_class_documentations(self, strip_quotes: bool=False) -> Dict[str, str]:
        """
        Returns the docstring of all classes
        """
        return self.get_all_class_docstrings()
    def get_info(self):
        """
        Returns an info_dict which would be a
        complete information of a given  file.
        """
        self.info_dict = {
            "class":[],
            "functions":[]
        }
        #Function related Mapping
        all_func_bodies = self.get_all_function_bodies()
        all_func_doc_string = self.get_all_function_docstrings()
        all_funcs = {i:{"doc_string":[all_func_doc_string[i]],"body":[all_func_bodies[i]]} for i in self.get_all_function_names()}
        #Class related Mapping
        all_class_bodies = self.get_all_class_docstrings()
        all_classes = {i:{"doc_string":[all_class_bodies[i]]} for i in self.get_all_class_names()}
        #Appending to info_dict
        self.info_dict["class"] = all_classes
        self.info_dict["functions"] = all_funcs

        return self.info_dict#self.info_dict#self.info_dict["class"]