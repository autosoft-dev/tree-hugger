- Provide a uniform and consistent API between the implemented parser

- Refactor the data structure (in particular BaseParser class)

- Find a way to automatically add the queries in the yml file into the implemented parser class without defining it explicitly: it can be interesting, the user just have to add request in queries file and they are availables in the parser class. If users need post-processing of the request, they can just extend with a new method their parser class that process the query output.

- Make the output of the request more structured (maybe use class)

- For few languages maybe the analysis of only one file is not sufficient (for example in C++ we may need to parse the header file and code file the retrieve all the information)


