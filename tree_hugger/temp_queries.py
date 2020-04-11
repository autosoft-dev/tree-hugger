PYTHON_QUERIES = {
    "all_class_names": """
        (
            class_definition
            name: (identifier) @class.def
        )
    """,
    "all_function_names": """
        (
            function_definition
            name: (identifier) @function.def
        )
    """,
    "all_function_doctrings":"""
        (
            function_definition
            name: (identifier) @function.def
            body: (block(expression_statement(string))) @function.docstring
        )
    """,
    "all_class_docstrings": """
        (
            class_definition
            name: (identifier) @class.def
            body: (block(expression_statement(string))) @class.docstring
        )
    """,
    "all_class_methods": """
        (
            
            class_definition
            name: (identifier) @class.name
        )

        ( class_definition
            body: (
                block(
                    function_definition
                    name: (identifier) @method.name
                )
            )
        )        
    """,
    "all_class_method_docstrings":"""
        (
            class_definition
            name: (identifier) @class.name
        )
            
        ( class_definition
            body: (
                block(
                    function_definition
                    name: (identifier) @method.name
                    body: (block(expression_statement(string))) @method.docstr
                )
            )
        )        
    """,
    "all_function_names_and_params": """
        (
            function_definition
            name: (identifier) @func.def
            parameters: (parameters) @func.params
        )
    """
}

PHP_QUERIES = {
    "namespace_declaration":"""
        (
            namespace_definition
            (
                namespace_name
                (name) @namespace.name
            )
        )
    """,
    "all_used_namespaces": """
        (
            namespace_name_as_prefix
            (
                namespace_name
                (name) @used.namespace.name
            )
        )
    """,
    "all_qualified_names": """
        (
            qualified_name
            (name) @qualified.name
        )
    """
}