import pytest

from tree_hugger.core import PythonParser

@pytest.fixture
def python_parser():
	pp = PythonParser()
	pp.parse_file("tests/assets/file_with_different_functions.py")
	return pp


@pytest.fixture
def python_parser_from_string():
	pp = PythonParser()
	with open("tests/assets/file_with_different_functions.py") as f:
		code_blob = f.read()
		pp.parse_code_as_string(code_blob)
		return pp


def test_parser_get_all_function_names(python_parser):
	assert set(python_parser.get_all_function_names()) == set([
		'wrapper', 
		'parent', 
		'first_child', 
		'my_decorator', 
		'second_child', 
		'say_whee',
		'function_different_args'
	])


def test_parser_get_all_function_names_from_string_based_parsing(python_parser_from_string):
	assert set(python_parser_from_string.get_all_function_names()) == set([
		'wrapper', 
		'parent', 
		'first_child', 
		'my_decorator', 
		'second_child', 
		'say_whee',
		'function_different_args'
	])

	
def test_get_all_function_names_with_params(python_parser):
	assert python_parser.get_all_function_names_with_params()["function_different_args"] == [
	    ('foo', None, None),
	    ('bar', 'int', None),
	    ('no', None, 'None'),
	    ('pi', None, '3.14'),
	    ('opt_typed', 'Dict[str,str]', '{}')
	]
	
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
			'__init__',
			'get_class_name'
		]
	}

def test_parser_get_all_class_names(python_parser):
	assert set(python_parser.get_all_class_names()) == set([
		'BaseClass',
		'AnotherClass'
	])

def test_parser_get_all_function_bodies(python_parser):
	assert python_parser.get_all_function_bodies()["second_child"] == \
		'def second_child():\n        """\n        This is second child\n        """\n        for i in range(10):\n            print(i)\n\n        return "Call me Liam"'
	assert python_parser.get_all_function_bodies(get_index=True)["second_child"] == (
		'def second_child():\n        """\n        This is second child\n        """\n        for i in range(10):\n            print(i)\n\n        return "Call me Liam"', 
		(22, 8),
		(28, 29)
	)
	assert python_parser.get_all_function_bodies()["function_different_args"] == \
		'def function_different_args(foo, bar, no, pi, opt_typed):\n    return 0'

def test_parser_get_all_method_bodies(python_parser):
	assert python_parser.get_all_class_method_bodies()['BaseClass']["get_name"] == \
		"def get_name(self):\n        '''Get the name parameter\n        '''\n        return self.name"
	assert python_parser.get_all_class_method_bodies(get_index=True)['BaseClass']["get_name"] ==(
		"def get_name(self):\n        '''Get the name parameter\n        '''\n        return self.name",
   		(75, 8),
   		(77, 24)
	)
	assert python_parser.get_all_class_method_bodies(get_index=True, strip_docstr=True)['BaseClass']["get_name"] == (
		('def get_name(self):\n        return self.name',
    	"'''Get the name parameter\n        '''"),
   		(75, 8),
   		(77, 24)
	)

	
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
	assert sum(l) == 13

def test_parser_reduction(python_parser):
	assert python_parser.reduction(
	    lambda node,acc: acc+1 if node.type == "function_definition" else acc, 0
	) == 13
	

