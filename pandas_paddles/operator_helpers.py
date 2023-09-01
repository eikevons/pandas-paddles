"""Helpers to wrap operator methods."""


unary_ops = (
        "abs",
        "bool",
        "invert",
        "neg",
        "not",
        "pos",
)

# Binary ops that have a __r{op}__, too.
binary_ops = (
    "add",
    "and",
    "divmod",
    "floordiv",
    "mod",
    "mul",
    "or",
    "pow",
    "sub",
    "truediv",
    "xor",
)

# Binary ops that don't have a __r{op}__, too.
binary_ops_non_reversable = (
    "contains",
    "eq",
    "ge",
    "gt",
    "le",
    "lt",
    "ne",
)



_binary_syntax = {
    "add": "+",
    "and": "&",
    "div": "/",
    "eq": "==",
    "ge": ">=",
    "gt": ">",
    "le": "<=",
    "lt": "<",
    "mod": "%",
    "mul": "*",
    "ne": "!=",
    "or": "|",
    "sub": "-",
    "truediv": "//",
    "xor": "^",
}

_unary_syntax = {
    "invert": "~",
    "neg": "-",
    "pos": "+",
}

def get_op_syntax(method_name):
    if method_name.startswith("__"):
        method_name = method_name[2:]
    else:
        return None, method_name

    if method_name.endswith("__"):
        method_name = method_name[:-2]
    else:
        return None, method_name

    reverse = False
    if method_name.startswith("r"):
        reverse = True
        method_name = method_name[1:]

    if method_name in _unary_syntax:
        return "unary", _unary_syntax[method_name]
    if method_name in _binary_syntax:
        return "binary" if not reverse else "reverse-binary", _binary_syntax[method_name]
    return None, method_name
