import os


ENTRY = "entry"

long_str = """This is a long string

With a looooooooooooottttttttt of characters


Hoooooooooo
"""


def parent(num) :
    def first_child():
        """
        This is first child
        """
        return "Hi, I am Emma"

    def second_child():
        """
        This is second child
        """
        for i in range(10):
            print(i)

        return "Call me Liam"

    if num == 1:
        return first_child
    else:
        return second_child
    

def my_decorator(func):
    """
    Outer decorator function
    """
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper


@my_decorator
def say_whee():
    """
    Hellooooooooo

    This is a function with decorators
    """
    print("Whee!")



class BaseClass(object):

    def __init__(self, x):
        self.x = x
        self.name = "BaseClass"

    def get_name(self):
        '''Get the name parameter
        '''
        return self.name
    
    @property
    def jj(self, x):
        def scan(children):
            print(children)
        return x * x
