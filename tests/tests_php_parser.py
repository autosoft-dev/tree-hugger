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
