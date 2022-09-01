"""Helper fucntions."""

from typing import Optional, Union, Tuple

class IndentedLines(list):
    """Container for indented lines."""
    def __str__(self):
        return "\n".join(f"{indent * ' '}{text}" for indent, text in self)


class AstNode:
    """Node container for tree of operations.

    This is used to build a tree and pretty-print it.

    Some payloads are encoded as tuples:
    - 1-tuple: the "root" object
    - 3-tuple: ordinary (=non-operator) method calls
      1. function name
      2. positional arguments as list of ``AstNode`` objects, e.g. repr of the argumment
      3. keyword arguments as list of keyword-name ``AstNode`` pairs.
    """
    def __init__(
        self,
        payload:Union[str, Tuple],
        parent:Optional["AstNode"]=None,
        left:Optional["AstNode"]=None,
        right:Optional["AstNode"]=None,
    ):
        self.payload = payload
        self.parent = parent
        self.left = left
        self.right = right

    @property
    def root(self) -> "AstNode":
        """Get the root of this node."""
        if self.parent is None:
            return self
        return self.parent.root

    def pprint(self, indent=0) -> IndentedLines:
        lines = IndentedLines()

        inc_right = 0
        is_root_object_node = False

        if self.left:
            lines.extend(self.left.pprint(indent + 2))
            inc_right = 2

        if isinstance(self.payload, str):
            lines.append([indent, self.payload])
        elif len(self.payload) == 1:
            root_name, = self.payload
            is_root_object_node = True
            lines.append([indent, root_name])
            inc_right = len(root_name)
        else:
            fname, args, kwargs = self.payload
            if not args and not kwargs:
                lines.append([indent, f".{fname}()"])
            else:
                lines.append([indent, f".{fname}("])
                for arg in args:
                    lines.extend(arg.pprint(indent + 2))
                    lines[-1][1] = f"{lines[-1][1]},"
                for kw, arg in kwargs:
                    kw_indent = indent + 2 + len(kw) + 1
                    kw_lines = arg.pprint(kw_indent)
                    kw_lines[0] = [indent + 2, f"{kw}={kw_lines[0][1]}"]
                    kw_lines[-1][1] = f"{kw_lines[-1][1]},"
                    lines.extend(kw_lines)
                lines.append([indent, ")"])

        if self.right:
            lines.extend(self.right.pprint(indent + inc_right))

        # Merge the root and 
        if is_root_object_node and len(lines) > 1:
            lines[0] = [lines[0][0],
                        lines[0][1] + lines[1][1]
                       ]
            del lines[1]

        return lines

    def collapse(self, allowed_width=80):
        if self.left:
            self.left, collapsed = self.left.collapse(allowed_width - 1)
            if not collapsed:
                return self, False
        if self.right:
            self.right, collapsed = self.right.collapse(allowed_width - 1)
            if not collapsed:
                return self, False

        if isinstance(self.payload, str):
            # print("SS {!r} {!r} {!r}".format(self.payload, self.left and self.left.payload, self.right and self.right.payload))
            if self.right and isinstance(self.right.payload, str):
                # print("RR")
                if self.left and isinstance(self.left.payload, str):
                    # print("LL")
                    # Binary operator
                    new_payload = f"{self.left.payload} {self.payload} {self.right.payload}"
                else:
                    # Unary operator
                    new_payload = f"{self.payload}{self.right.payload}"

                # print("NP", new_payload)

                if len(new_payload) + 2 <= allowed_width:
                    return AstNode(new_payload, self.parent), True
        # print("CC {!r} {!r} {!r}".format(self.payload, self.left and self.left.payload, self.right and self.right.payload))
        return self, True


binary_dunders = {
    "__and__": "&",
    "__eq__": "==",
    "__neq__": "!=",
    "__neq__": "!=",
    "__or__": "|",
    "__add__": "+",
    "__mul__": "*",
    "__sub__": "-",
    "__div__": "/",
    "__truediv__": "//",
    "__xor__": "^",
    "__lt__": "<",
    "__le__": "<=",
    "__gt__": ">",
    "__ge__": ">=",
}


unary_dunders = {
    "__invert__": "~",
    "__neg__": "-",
    "__pos__": "+",
}
