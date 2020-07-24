import pytest

from tree_hugger.core import JavaParser

@pytest.fixture
def java_parser():
	jp = JavaParser()
	jp.parse_file("tests/assets/file_with_different_methods.java")
	return jp

def get_all_function_names_with_params(java_parser):
	assert java_parser.get_all_method_names_with_params()["main"] == [('arg', 'String[]')]
	assert java_parser.get_all_method_names_with_params()["bark"] == [
        ('sound', 'String'),
        ('repeat', 'int')
    ]
	assert java_parser.get_all_method_names_with_params()["move"] == []

def test_parser_get_all_class_method_names(java_parser):
	assert java_parser.get_all_class_method_names() == {
	    'HelloWorld': [
	        'main',
	        'variadic_main'
	    ],
	    'Animal': [
	        'move'
	    ],
	    'Dog': [
	        'create',
	        'bark',
	        'move'
	    ]
	}

def test_parser_get_all_class_names(java_parser):
	assert set(java_parser.get_all_class_names()) == set([
        'HelloWorld',
        'Animal',
        'Dog'
	])

def test_parser_get_all_method_bodies(java_parser):
	assert java_parser.get_all_method_bodies()["main"] == '{\n\t\tSystem.out.println("Hello world");\n\t}'

def test_parser_get_all_class_documentations(java_parser):
	assert java_parser.get_all_class_documentations()['Animal'] == \
	 '/**\n * Abstract representation of an animal\n */'
