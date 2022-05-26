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
