
unary_ops = (
        "abs",
        "bool",
        "invert",
        "neg",
        "not",
        "pos",
)

# Binary ops have a __r{op}__, too.
binary_ops = (
        "add",
        "and",
        "contains",
        "div",
        "divmod",
        "eq",
        "floordiv",
        "ge",
        "gt",
        "le",
        "lt",
        "mod",
        "mul",
        "ne",
        "or",
        "pow",
        "sub",
        "truediv",
        "xor",
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
    if method_name.endswith("__"):
        method_name = method_name[:-2]
    if method_name.startswith("r"):
        method_name = method_name[1:]

    if method_name in _unary_syntax:
        return "unary", _unary_syntax[method_name]
    if method_name in _binary_syntax:
        return "binary", _binary_syntax[method_name]
    return None, method_name
