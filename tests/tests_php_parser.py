import pytest

from tree_hugger.core import PHPParser

@pytest.fixture
def php_parser():
	pp = PHPParser()
	pp.parse_file("tests/assets/file_with_different_functions.php")
	return pp

def test_parser_get_all_function_names(php_parser):
	assert set(php_parser.get_all_function_names()) == set([
		'foo', 
		'test',
	])

def test_parser_get_all_class_method_names(php_parser):
	assert php_parser.get_all_class_method_names() == {
		'Car': [
			'Car',
			'bar'
		],
		'Truck': [
			'drive'
		]
	}

def test_parser_get_all_class_names(php_parser):
	assert set(php_parser.get_all_class_names()) == set([
		'Car',
		'Truck'
	])

def test_parser_get_all_class_documentations(php_parser):
	assert php_parser.get_all_class_documentations() == {
		'Car': '/*\n * Car documentation\n */'
	}

def test_parser_get_all_function_documentations(php_parser):
	assert php_parser.get_all_function_documentations() == {
		'foo': '/**\n  * PHPDoc\n  *\n  * @param int    $arg1 First Argument\n  * @param string $arg2 Second Argument\n  * @param int    $argn Last Argument\n  */'
	}

def test_parser_get_all_function_bodies(php_parser):
	assert php_parser.get_all_function_bodies() == {
		'foo': '{\n    echo "Example\\n";\n    return $retval;\n}',
		'test': '{\n    return 2*x + 1;\n}'
	}

def test_parser_function_names_with_params(php_parser):
	assert php_parser.function_names_with_params() == {
		'foo': '($arg_1, $arg_2, $arg_n)', 
		'test': '()'
	}

def test_parser_walk(php_parser):
	l = []
	php_parser.walk(lambda node: l.append(1) if node.type == "function_definition" else l.append(0))
	assert sum(l) == 2

def test_parser_reduction(php_parser):
	assert php_parser.reduction(
	    lambda node,acc: acc+1 if node.type == "function_definition" else acc, 0
	) == 2


