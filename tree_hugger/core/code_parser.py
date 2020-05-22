import os
from pathlib import Path
from typing import List

from tree_sitter import Node, Language, Parser, Tree

from tree_hugger.exceptions import ParserLibraryNotFoundError, SourceFileNotFoundError, QueryFileNotFoundError
from tree_hugger.core.queries import Query


def match_from_span(node: Node, lines: List) -> str:
    line_start = node.start_point[0]
    line_end = node.end_point[0]
    char_start = node.start_point[1]
    char_end = node.end_point[1]
    if line_start != line_end:
        return '\n'.join([lines[line_start][char_start:]] + lines[line_start+1:line_end] + 
                          [lines[line_end][:char_end]])
    else:
        return lines[line_start][char_start:char_end]


class BaseParser(object):
    """
    Base parser exposes the common interface that we extend per language
    """

    def __init__(self, language: str, query_class_name: str, library_loc: str=None, query_file_path: str=None):
        if os.getenv("TS_LIB_PATH") is not None and library_loc is None:
            library_loc = os.getenv("TS_LIB_PATH")
        
        if not library_loc:
            raise ParserLibraryNotFoundError("Parser library path is 'None'. Please either set up the environment or call the constructor with the path")

        if not Path(library_loc).exists() or not Path(library_loc).is_file():
            raise ParserLibraryNotFoundError(f"Parser library '{library_loc}' not found. Did you set up the environement variables?")
        
        if os.getenv("QUERY_FILE_PATH") is not None and query_file_path is None:
            query_file_path =  os.getenv("QUERY_FILE_PATH")
        
        if not query_file_path:
            raise QueryFileNotFoundError(f"Query file path is 'None'")

        
        self.language = Language(library_loc, language)
        self.parser = Parser()
        self.parser.set_language(self.language)
        self.qclass = Query(query_file_path)
        self.QUERIES = self.qclass[query_class_name]
    
    def _run_query_and_get_captures(self, q_name: str, root_node:  Node) -> List:
        """
        Runs a query on the the language and returns the raw spans.

        Sometimes you may need to do to some specilized processing on the returned lines
        Check languane specific codes to see what that can be.
        """
        query = self.language.query(self.QUERIES[q_name])
        captures = query.captures(root_node)
        return captures
    
    def parse_file(self, file_path: str):
        """
        Parses a single file and retunrs True if success
        """
        if not Path(file_path).exists() or not Path(file_path).is_file():
            raise SourceFileNotFoundError(f"Source file {file_path} not found")
        try:
            with open(file_path, encoding='utf-8') as f:
                blob = f.read()
        except UnicodeDecodeError:
            return False
        self.raw_code = blob
        self.splitted_code = blob.split("\n")
        self.tree :Tree = self.parser.parse(bytes(blob.encode('utf-8')))
        self.root_node :Node = self.tree.root_node
        return True
    
    def sexp(self):
        return self.tree.root_node.sexp()
    
    def reload_queries(self, query_file_path: str=None):
        """
        Reloads the query file and the internal data structure.

        This is a temporary method and it should not be a part of the API. 
        mainly to dynamically reload the queries while in development for 
        IPython console
        """
        if os.getenv("QUERY_FILE_PATH") is not None and query_file_path is None:
            query_file_path =  os.getenv("QUERY_FILE_PATH")
        
        self.qclass = Query(query_file_path)
        self.QUERIES = self.qclass['python_quaries']
