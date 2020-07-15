import pytest

from tree_hugger.core import PythonParser

@pytest.fixture
def python_parser():
	pp = PythonParser()
	pp.parse_file("tests/assets/file_with_different_functions.py")
	return pp

def test_parser_get_all_function_names(python_parser):
	assert set(python_parser.get_all_function_names()) == set([
		'wrapper', 
		'parent', 
		'first_child', 
		'my_decorator', 
		'second_child', 
		'say_whee'
	])
	
def test_parser_get_all_class_documentations(python_parser):
	assert python_parser.get_all_class_documentations() == {
		'BaseClass': '"""\n    This is a class docstring\n\n    Which spans multiple lines\n\n    Helloooooooooo\n    """',
		'AnotherClass': "'''Another line of useless doc :)\n    '''"
	}
	
def test_parser_get_all_class_method_names(python_parser):
	assert python_parser.get_all_class_method_names() == {
		'BaseClass': [
			'__init__',
			'get_name',
			'jj', 
			'scan'
		], 
		'AnotherClass': [
			'__init__'
		]
	}

def test_parser_get_all_class_names(python_parser):
	assert set(python_parser.get_all_class_names()) == set([
		'BaseClass',
		'AnotherClass'
	])

def test_parser_get_all_function_documentations(python_parser):
	assert python_parser.get_all_function_documentations() == {
		'first_child': '"""\n        This is first child\n        """',
		'second_child': '"""\n        This is second child\n        """',
		'my_decorator': '"""\n    Outer decorator function\n    """',
		'say_whee': '"""\n    Hellooooooooo\n\n    This is a function with decorators\n    """'
	}

def test_parser_walk(python_parser):
	l = []
	python_parser.walk(lambda node: l.append(1) if node.type == "function_definition" else l.append(0))
	assert sum(l) == 11

def test_parser_reduction(python_parser):
	assert python_parser.reduction(
	    lambda node,acc: acc+1 if node.type == "function_definition" else acc, 0
	) == 11
	

