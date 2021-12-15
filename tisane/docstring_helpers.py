import functools
import re

# for decorating class methods and extending docstrings
# from: https://stackoverflow.com/questions/60000179/sphinx-insert-argument-documentation-from-parent-method/60012943#60012943
class extend_docstring:
    def __init__(self, method, replace=None, replaceWith=None):
        self.doc = method.__doc__
        if replace and replaceWith:
            self.doc = re.sub(replace, replaceWith, self.doc)
            pass
        pass

    def get_parameters(self):
        splits = re.split(r"---+", self.doc)

    def __call__(self, function):
        if self.doc is not None:
            functools.update_wrapper(self, function)
            doc = function.__doc__
            function.__doc__ = self.doc
            if doc is not None:
                function.__doc__ += doc
        return function
