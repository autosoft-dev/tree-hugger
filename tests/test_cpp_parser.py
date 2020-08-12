import pytest

from tree_hugger.core import CPPParser

@pytest.fixture
def cpp_parser():
	cp = CPPParser()
	cp.parse_file("tests/assets/file_with_different_functions.cpp")
	return cp

def test_parser_get_all_function_names(cpp_parser):
	assert set(cpp_parser.get_all_function_names()) == set([
		'main', 
		'f',
		'test'
	])

def test_get_all_function_names_with_params(cpp_parser):
	assert cpp_parser.get_all_function_names_with_params()["test"] == []
	assert cpp_parser.get_all_function_names_with_params()["f"] == [
		('x', 'int', None),
		('y[]', 'float', None), 
		('z', 'int', '5')
	]

def test_parser_get_all_class_method_names(cpp_parser):
	assert cpp_parser.get_all_class_method_names() == {
		'Rectangle': [
			'set_values',
			'area'
		], 
		'Square': [
			'area', 
			'set_size'
		], 
		'Shape': [
		
		]
	}


def test_parser_get_all_class_names(cpp_parser):
	assert set(cpp_parser.get_all_class_names()) == set([
		'Rectangle',
		'Square',
		'Shape'
	])

def test_parser_get_all_class_documentations(cpp_parser):
	assert cpp_parser.get_all_class_documentations() == {
		'Rectangle': '/**\n * Class documentation\n */'
	}

def test_parser_get_all_function_bodies(cpp_parser):
	assert cpp_parser.get_all_function_bodies()['test'] ==  \
	    '{\n\n}'
	assert cpp_parser.get_all_function_bodies()['main'] == \
		'{\n\treturn 0;\n}'
