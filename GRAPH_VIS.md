# Creating Graph Visualizations with TikZ

After obtaining a `tisane.Graph` object `g`, a visualization of a graph containing
all the nodes can be obtained by running `g._get_graph_tikz()`. A `standalone`
class of LaTeX document is
printed to standard out, which produces PDFs that exactly fit the figures created.
Note that in order to use automatic layout features, from the `graphdrawing` tikz
library, you have to typeset these documents with LuaLaTeX or LuaTeX.

For example, after running the unit tests in `tests/test_graph_vis.py`, we get the
following output.

```
\documentclass{standalone}
\usepackage{tikz}

\usetikzlibrary{graphs,graphdrawing,quotes}
\usegdlibrary{force,layered}
\begin{document}

\begin{tikzpicture}[cause/.style={draw=red, "c", text=red},
                    associate/.style={draw=black},
                    min/.style={minimum size=2cm},
                    unit/.style={min,draw=black},
                    measure/.style={min,circle,draw=black}]

    \graph[layered layout,sibling distance=3cm,level distance=3cm]{
		Student[unit] -> [has] Test score[measure];
		Student -> [associate] Test score;
		Student -> [has] Race[measure];
		Student -> [has] Race*SES[measure];
		Student -> [has] SES[measure];
		Test score -> [associate] Race;
		Test score -> [associate] Student;
		Test score -> [associate] Race*SES;
		Race -> [associate] Test score;
		Race -> [cause] treatment[measure];
		Race*SES -> [associate] Test score;

    };
\end{tikzpicture}
\end{document}

\documentclass{standalone}
\usepackage{tikz}

\usetikzlibrary{graphs,graphdrawing,quotes}
\usegdlibrary{force,layered}
\begin{document}

\begin{tikzpicture}[cause/.style={draw=red, "c", text=red},
                    associate/.style={draw=black},
                    min/.style={minimum size=2cm},
                    unit/.style={min,draw=black},
                    measure/.style={min,circle,draw=black}]

    \graph[layered layout,sibling distance=3cm,level distance=3cm]{
		student id[unit] -> [has] test score[measure];
		school id[unit] -> [cause] test score;

    };
\end{tikzpicture}
\end{document}
```

After typesetting using `LuaTeX` or `LuaLaTeX`, you should have the following:

![A graph containing four nodes, Student (square shaped), Test Score (circle shaped), Race (circle shaped), Race*SES (circle shaped), SES (circle shaped), and treatment (circle shaped).](examples/standalone1.png?raw=true)

![A graph containing the nodes student id, test score, and school. Student id and school are circles, and test score is a rectangle. There are arrows between student id and test score, and school id and test score. The arrow from school id to test score is red, and has a c next to it.](examples/standalone2.png?raw=true)
