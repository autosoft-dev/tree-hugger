import pytest

from tree_hugger.core import JavascriptParser

@pytest.fixture
def js_parser():
	jp = JavascriptParser()
	jp.parse_file("tests/assets/file_with_different_functions.js")
	return jp

def test_parser_get_all_function_names(js_parser):
	assert set(js_parser.get_all_function_names()) == set([
		'test',
		'utf8_to_b64',
		'sum',
		'multiply'
	])

def test_get_all_function_names_with_params(js_parser):
	assert js_parser.get_all_function_names_with_params()["test"] == []
	assert js_parser.get_all_function_names_with_params()["multiply"] == [
		('a', None),
		('b', '1'),
	]
	assert js_parser.get_all_function_names_with_params()["utf8_to_b64"] == [
		('str', None)
	]
	assert js_parser.get_all_function_names_with_params()["sum"] == [
		('args', None)
	]

def test_parser_get_all_class_method_names(js_parser):
	assert js_parser.get_all_class_method_names() == {
		'Rectangle': [
			'constructor',
			'area',
			'computeArea'
		]
	}

def test_parser_get_all_class_names(js_parser):
	assert set(js_parser.get_all_class_names()) == set([
		'Rectangle'
	])

def test_parser_get_all_class_documentations(js_parser):
	assert js_parser.get_all_class_documentations() == {
		'Rectangle': '/**\n * Representation of a rectangle\n */'
	}

def test_parser_get_all_function_documentations(js_parser):
	assert js_parser.get_all_function_documentations() == {
		'test': '/**\n * @param {very_long_type} name           Description.\n * @param {type}           very_long_name Description.\n */'
	}

def test_parser_get_all_function_bodies(js_parser):
	assert js_parser.get_all_function_bodies()['multiply'] ==  \
	    '{\n  return a * b;\n}'
	assert js_parser.get_all_function_bodies()['test'] == \
		'{\n\t alert("Hello Javatpoint");  \n}'


