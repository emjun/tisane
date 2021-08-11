import re

template_begin = """
\\documentclass{standalone}
\\usepackage{tikz}

\\usetikzlibrary{graphs,graphdrawing,quotes}
\\usegdlibrary{force,layered}
\\begin{document}

\\begin{tikzpicture}[cause/.style={draw=red, "c", text=red},
                    associate/.style={draw=black},
                    min/.style={minimum size=2cm},
                    unit/.style={min,draw=black},
                    measure/.style={min,circle,draw=black}]
"""

graph = """    \graph[layered layout,sibling distance={},level distance={}]{}
"""

tikz_template_end = """    };
\end{tikzpicture}
\end{document}
"""


def indent(code):
    return "\t" + re.sub(r"\n", "\n\t", code)


def formatTikzVis(graphCode="", nodesCode="", siblingDistance=1, levelDistance=1):
    return (
        template_begin
        + indent(nodesCode)
        + "\n"
        + graph.format(f"{siblingDistance}cm", f"{levelDistance}cm", "{")
        + indent(indent(graphCode))
        + "\n"
        + tikz_template_end
    )
