import re

document_begin = """
\\documentclass{standalone}
\\usepackage{tikz}

\\usetikzlibrary{graphs,graphdrawing,quotes}
\\usegdlibrary{force,layered}
\\begin{document}
"""

template_begin = """
\\begin{tikzpicture}[cause/.style={draw=black, "cause", text=black},
                    associate/.style={draw=black, "assoc."},
                    min/.style={minimum size=2cm},
                    unit/.style={min,draw=black},
                    measure/.style={min,circle,draw=black},
                    has/.style={densely dotted},
                    nests/.style={dashed}]
"""

graph = """    \graph[layered layout,sibling distance={},level distance={}]{}
"""

tikz_template_end = """    };
\end{tikzpicture}
"""
document_end = """
\end{document}
"""


def indent(code):
    return "\t" + re.sub(r"\n", "\n\t", code)


def formatTikzVis(graphCode="", nodesCode="", siblingDistance=1, levelDistance=1, fullDocument=True):
    prefix = document_begin if fullDocument else ""
    postfix = document_end if fullDocument else ""
    return (
        prefix
        + template_begin
        + indent(nodesCode)
        + "\n"
        + graph.format(f"{siblingDistance}cm", f"{levelDistance}cm", "{")
        + indent(indent(graphCode))
        + "\n"
        + tikz_template_end
        + postfix
    )
