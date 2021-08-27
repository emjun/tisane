from tisane.variable import (
    Nominal,
    Measure,
    SetUp,
    Unit,
    AbstractVariable,
    Has,
    Associates,
    Causes,
    Moderates,
    Nests,
    Repeats,
    NumberValue,
)
import networkx as nx
import pydot
from typing import List, Set, Union, Tuple
import typing
import copy
from tisane.graph_vis_support import (
    formatTikzVis,
    dot_formats,
    dot_formats_extensions,
    default_dot_edge_style,
    default_dot_edge_color,
    default_dot_edge_label,
)
import re
import os

"""
Class for expressing how variables (i.e., proxies) relate to one another at a
conceptual level: cause, correlate, contribute.
"""


class Graph(object):
    _graph: nx.MultiDiGraph

    @classmethod
    def cast(**kwargs):
        gr = Graph()

        return gr

    def __init__(self):
        self._graph = nx.MultiDiGraph()

    def __repr__(self):
        return str(self._graph.__dict__)

    def __str__(self):
        nodes = [n for n in self._graph.nodes()]
        edges = [e for e in self._graph.edges()]
        return f"Nodes: {str(nodes)} has {len(nodes)} concepts. Edges: {str(edges)} has {len(edges)} relationships."

    # @returns True if the variable is in the grah
    def has_variable(self, variable: AbstractVariable) -> bool:
        return self._graph.has_node(variable.name)

    # @returns True if the edge between @params start and end is in the graph; False otherwise
    def has_edge(
        self, start: AbstractVariable, end: AbstractVariable, edge_type: str
    ) -> bool:
        # return self._graph.has_edge(start.name, end.name)

        edge = self.get_edge(start=start, end=end, edge_type=edge_type)

        return edge is not None

    # @returns tuple representing edge or None if edge is not found in graph
    def get_edge(
        self, start: AbstractVariable, end: AbstractVariable, edge_type: str
    ) -> Union[Tuple, None]:
        edges = self.get_edges()

        for (n0, n1, edge_data) in edges:

            if n0 == start.name and n1 == end.name:
                if edge_type == edge_data["edge_type"]:
                    return (n0, n1, edge_data)

        return None

    # @returns handle to Node that represents the @param variable
    # @returns None if @param variable is not found in the graph
    def _get_variable_node(self, variable: AbstractVariable):
        for n in self._graph.nodes("variable"):
            if n[0] == variable.name:
                return n
        return None

    # Variables have unique names and are indexed by their names.
    # Variables also have a 'tag' that indicate if they are 'identifiers' for a level
    def _add_variable(self, variable: AbstractVariable, is_identifier: bool = False):
        if not self._graph:
            self._graph = nx.MultiDiGraph()
        # Depends on composing/non-nesting relationship: This might not make sense in the long term
        if isinstance(variable, Unit):
            is_identifier = True
        elif isinstance(variable, SetUp):
            is_identifier = True
        self._graph.add_node(
            variable.name, variable=variable, is_identifier=is_identifier
        )

    # Add edge to graph
    # If nodes aren't already in the graph, add them
    def _add_edge(
        self,
        start: AbstractVariable,
        end: AbstractVariable,
        edge_type: str,
        repetitions: int = None,
        edge_obj: Union[Nests, Repeats, Associates] = None,
    ):

        # If the variables aren't in the graph, add nodes first.
        start_node = None
        end_node = None

        if not self.has_variable(start):
            self._add_variable(start)
        start_node = self._get_variable_node(start)

        if not self.has_variable(end):
            self._add_variable(end)
        end_node = self._get_variable_node(end)
        # Assert the start and end nodes are not None
        assert start_node
        assert end_node

        # This assumes that each variable has a unique name
        # Add edges between variable names, use the variable names later to look
        # up the actual variable objects
        # Add edge using NetworkGraph's API
        if edge_type == "treat":
            self._graph.add_edge(
                start_node[0],
                end_node[0],
                edge_type=edge_type,
                edge_obj=edge_obj,
                repetitions=repetitions,
            )
        elif edge_type == "nests":
            self._graph.add_edge(
                start_node[0],
                end_node[0],
                edge_type=edge_type,
                edge_obj=edge_obj,
                repetitions=repetitions,
            )
        elif edge_type == "repeat":
            self._graph.add_edge(
                start_node[0],
                end_node[0],
                edge_type=edge_type,
                edge_obj=edge_obj,
                repetitions=repetitions,
            )
        else:
            self._graph.add_edge(
                start_node[0],
                end_node[0],
                edge_type=edge_type,
                edge_obj=edge_obj,
                repetitions=repetitions,
            )

    def get_causes_associates_tikz_graph(
        self, path="causes_associates_graph.tex", dv: AbstractVariable = None
    ):
        self.get_tikz_graph(
            edge_filter=lambda edge_data: edge_data["edge_type"] == "causes"
            or edge_data["edge_type"] == "associates",
            path=path,
            dv=dv,
        )

    def get_tikz_graph(
        self, path="graph.tex", edge_filter=lambda x: True, dv: AbstractVariable = None
    ):
        path_dir = os.path.dirname(path)
        if path_dir and not os.path.exists(path_dir):
            os.makedirs(path_dir)
        with open(path, "w") as f:
            f.write(self._get_tikz_graph(edge_filter=edge_filter, dv=dv))
            pass

    def _get_tikz_graph(self, edge_filter=lambda x: True, dv: AbstractVariable = None):
        def sanitize_characters(string):
            # Remove all underscores from the string, and replace them with
            # spaces. LaTeX doesn't like underscores, because of math mode.
            return re.sub(r"_", " ", string)

        edges = list(self._graph.edges(data=True))
        tikz_edges = []
        nodes = []
        for (nstart, nend, edge_data) in edges:
            if edge_filter(edge_data):
                n0 = sanitize_characters(nstart)
                n1 = sanitize_characters(nend)
                if n0 not in nodes:
                    nodes.append(n0)
                    pass
                if n1 not in nodes:
                    nodes.append(n1)
                edge_type = edge_data["edge_type"]
                tikz_edges.append({"start": n0, "end": n1, "style": edge_type})
                pass
            pass

        # variables = self.get_variables()
        nodeStyles = {}
        for n in nodes:
            var = self.get_variable(n)
            if var:
                nodeStyles[n] = (
                    "unit"
                    if isinstance(var, Unit) and not isinstance(var, Measure)
                    else "measure"
                ) + (",depvar" if var == dv else "")
        nodes_code = ""
        # for n in nodes:
        #     # TODO: get the type of the node
        #     nodes_code += "\\node ({}) at ()"
        graph_code = ""
        seen_nodes = []
        for tedge in tikz_edges:
            start_style = ""
            end_style = ""
            if tedge["start"] not in seen_nodes:
                start_style = f"[{nodeStyles[tedge['start']]}]"
                seen_nodes.append(tedge["start"])
                pass
            if tedge["end"] not in seen_nodes:
                end_style = f"[{nodeStyles[tedge['end']]}]"
                seen_nodes.append(tedge["end"])
                pass
            graph_code += "{} -> [{}] {};\n".format(
                tedge["start"] + start_style, tedge["style"], tedge["end"] + end_style
            )
            pass
        return formatTikzVis(graph_code, siblingDistance=3, levelDistance=3)

    def get_causes_associates_dot_graph(
        self,
        path="causes_associates_dot.png",
        format="png",
        edge_filter=lambda x: True,
        add_extension=True,
        style=default_dot_edge_style,
        color=default_dot_edge_color,
        label=default_dot_edge_label,
        dv: AbstractVariable = None,
    ):
        """Write a DOT graph representation to a file, containing only the edges with types "causes" or "associates"

        Parameters
        ----------
        path : str
            The desired location of the graph. Defaults to "graph.png"
        format : str
            The format to use for the output file. This supports all formats supported by DOT (https://graphviz.org/docs/outputs/). Defaults to "png"
        edge_filter : edge_data -> bool
            An additional filter function to choose which edges to add to the graph. Defaults to `lambda x: True`, which adds all edges of types "causes" or "associates".
        add_extension : bool
            Whether to add the proper extension designated by "format"
            to the end of the path. Defaults to `True`. If `True`, and
            an extension is known for the specified format, such as `psd`, and `path=graph`, then the output graph will be
            written to `graph.psd`.

        """
        # TODO: Add style, color, and label parameter descriptions
        self.get_dot_graph(
            path=path,
            format=format,
            edge_filter=lambda edge_data: (
                edge_data["edge_type"] == "causes"
                or edge_data["edge_type"] == "associates"
            )
            and edge_filter(edge_data),
            add_extension=add_extension,
            style=style,
            color=color,
            label=label,
            dv=dv,
        )

    def get_dot_graph(
        self,
        path="graph.png",
        format="png",
        edge_filter=lambda x: True,
        add_extension=True,
        style=default_dot_edge_style,
        color=default_dot_edge_color,
        label=default_dot_edge_label,
        dv: AbstractVariable = None,
    ):
        """Write the DOT graph representation to a file.

        Parameters
        ----------
        path : str
            The desired location of the graph. Defaults to "graph.png"
        format : str
            The format to use for the output file. This supports all formats supported by DOT (https://graphviz.org/docs/outputs/). Defaults to "png"
        edge_filter : edge_data -> bool
            An optional filter function to choose which edges to add to the graph. Defaults to `lambda x: True`, which adds
            all edges.
        add_extension : bool
            Whether to add the proper extension designated by "format"
            to the end of the path. Defaults to `True`. If `True`, and
            an extension is known for the specified format, such as `psd`, and `path=graph`, then the output graph will be
            written to `graph.psd`.

        """
        # TODO: Add style, color, and label parameter descriptions
        graph = self._get_dot_graph(
            edge_filter=edge_filter, style=style, color=color, label=label, dv=dv
        )
        assert (
            format in dot_formats
        ), "Format {} not supported. Supported formats are {}".format(
            format, ",".join(dot_formats)
        )
        if add_extension:
            if format in dot_formats_extensions:
                if not any(
                    path.endswith(ext)
                    for ext in dot_formats_extensions[format]["extensions"]
                ):
                    first_extension = dot_formats_extensions[format]["extensions"][0]
                    path = path + "." + first_extension
                    pass
                pass
            pass
        path_dir = os.path.dirname(path)
        if path_dir and not os.path.exists(path_dir):
            # print("Path directory: {}".format(path_dir))
            # Create the directory, if it doesn't exist
            os.makedirs(path_dir)
            pass

        graph.write(path, format=format)

    def _get_dot_graph(
        self,
        edge_filter=lambda x: True,
        style=default_dot_edge_style,
        color=default_dot_edge_color,
        label=default_dot_edge_label,
        dv: AbstractVariable = None,
    ):
        """Internal method to obtain a DOT graph object representing this graph.

        Parameters
        ----------
        edge_filter : edge_data -> bool
            An optional filter function to choose which edges to add to the graph. Defaults to `lambda x: True`, which adds
            all edges.
        style : dict
            A dictionary where keys are edge types and values are the DOT style to use. "nests" edges are dashed, "has" edges are dotted,
            To customize edge style, provide a dictionary with a default defined (by the key `default`), and define the style for a edge type
        color : dict
            A dictionary where keys are edge types and values are the DOT color to use for an edge. All edges by default are black. To customize edge color, provide a dictionary with a default defined (by the key `default`), and edges customized by edge type.
        label : dict
            A dictionary where keys are edge types and values are the label to use for the edge. Associates and cause edges are labeled with their type, and all other edges have no label by default. To provide custom labels, use the edge keys `associate`, `cause`, etc., and provide a `default`

        Returns
        -------
        pydot.Dot
            A `pydot.Dot` graph object representing this graph

        """
        # TODO: fix style parameter description
        graph = pydot.Dot("graph_vis", graph_type="digraph")
        edges = list(self._graph.edges(data=True))
        nodes = []
        for (n0, n1, _) in edges:
            if n0 not in nodes:
                nodes.append(n0)
                pass
            if n1 not in nodes:
                nodes.append(n1)
                pass
            pass
        for n0 in nodes:
            var0 = self.get_variable(n0)
            shape = (
                "box"
                if isinstance(var0, Unit) and not isinstance(var0, Measure)
                else "ellipse"
            )
            nodestyle = ""
            fillcolor = "white"
            if var0 == dv:
                nodestyle = "filled"
                fillcolor = "#AAAAAA"
                pass
            graph.add_node(
                pydot.Node(
                    n0, label=n0, style=nodestyle, fillcolor=fillcolor, shape=shape
                )
            )
            pass

        for (n0, n1, edge_data) in edges:
            if edge_filter(edge_data):
                edge_type = edge_data["edge_type"]
                edge_style = (
                    style[edge_type] if edge_type in style else style["default"]
                )
                edge_color = (
                    color[edge_type] if edge_type in color else color["default"]
                )
                edge_label = (
                    label[edge_type] if edge_type in label else label["default"]
                )
                graph.add_edge(
                    pydot.Edge(
                        n0, n1, style=edge_style, color=edge_color, label=edge_label
                    )
                )
                pass
            pass
        return graph

    # @return List of variables represented in this graph as nodes
    def get_variables(self) -> List[AbstractVariable]:
        variables = list()

        nodes = list(self._graph.nodes(data=True))
        for (n, data) in nodes:
            n_var = data["variable"]
            variables.append(n_var)

        return variables

    # @return list of nodes in graph
    def get_nodes(self) -> List:
        return list(self._graph.nodes(data=True))

    # @return Node representing @param variable in graph
    def get_node(self, variable: AbstractVariable):
        nodes = self.get_nodes()

        for n in nodes:
            if n[1]["variable"].name == variable.name:
                return n

    # @return list of edges in graph
    def get_edges(self) -> List:
        return list(self._graph.edges(data=True))

    # @return neighbors of @param variable with @param edge_type such that there is an edge of @param edge_type between @param to neighbor
    # If @param edge_type == 'ALL' then return all neighbors
    def get_neighbors(self, variable: AbstractVariable, edge_type: str = "ALL"):

        neighbors = self._graph.neighbors(
            variable.name
        )  # nodes are referenced by their variable name

        # List of variables with edge_type
        neigh_list = list()

        if edge_type.upper() == "ALL":
            return neighbors
        else:
            for n in neighbors:
                n_var = self.get_variable(name=n)
                if self.has_edge(start=variable, end=n_var, edge_type=edge_type):
                    neigh_list.append(n_var)

        return neigh_list

    # @param name is the name of the variable we are looking for
    # @return AbstractVariable in Graph with @param name, None otherwise
    def get_variable(self, name: str) -> AbstractVariable:
        nodes = self.get_nodes()

        for (n, data) in nodes:
            n_var = data["variable"]
            if n_var.name == name:
                return n_var
        return None

    # @return iterator over predecessors of @param var
    def get_predecessors(self, var: AbstractVariable):
        if self.has_variable(var):
            nodes = self.get_nodes()
            for n, data in nodes:
                n_var = data["variable"]
                if n_var == var:
                    return self._graph.predecessors(n)  # pass node, not variable

    # @return a list of identifiers
    def get_identifiers(self) -> List[AbstractVariable]:
        identifiers = list()

        nodes = self.get_nodes()

        for (n, data) in nodes:
            is_id = data["is_identifier"]
            n_var = data["variable"]

            if isinstance(n_var, Unit):
                assert is_id
                identifiers.append(n_var)
            elif isinstance(n_var, SetUp):
                assert is_id
                identifiers.append(n_var)
            # Removed this when add composing/has relationships between measure and unit
            # This is to be backwards compatible with code that does not use the Unit type
            # else:
            #     if is_id:
            #         identifiers.append(n_var)

        return identifiers

    # @return the variable in graph that is the identifier for @param variable
    def get_identifier_for_variable(
        self, variable: AbstractVariable
    ) -> AbstractVariable:
        identifiers = self.get_identifiers()

        # Is the variable itself an identifier?
        if variable in identifiers:
            return variable

        for i in identifiers:
            if self.has_edge(i, variable, "has"):
                return i

        return None

    # Update the edge by first removing then adding
    def update_edge(
        self, start: AbstractVariable, end: AbstractVariable, new_edge_type: str
    ):
        start_node = self._get_variable_node(variable=start)
        end_node = self._get_variable_node(variable=end)

        # First remove
        assert self._graph.has_edge(start_node[0], end_node[0])
        self._graph.remove_edge(start_node[0], end_node[0])

        # Then add back in
        self._add_edge(start=start, end=end, edge_type=new_edge_type)

    # Add a node that identifies levels in the Graph
    def add_identifier(self, identifier: AbstractVariable):
        self._add_variable(variable=identifier, is_identifier=True)

    def add_relationship(
        self, relationship: Union[Has, Nests, Associates, Causes, Moderates]
    ):
        if isinstance(relationship, Has):
            identifier = relationship.variable
            measure = relationship.measure
            repetitions = relationship.repetitions
            self.has(identifier, measure, relationship, repetitions)
        # elif isinstance(relationship, Treatment):
        #     identifier = relationship.unit
        #     treatment = relationship.treatment
        #     repetitions = relationship.num_assignments
        #     self.treat(unit=identifier, treatment=treatment, treatment_obj=relationship)
        elif isinstance(relationship, Nests):
            base = relationship.base
            group = relationship.group
            self.nests(base, group, relationship)
        elif isinstance(relationship, Associates):
            lhs = relationship.lhs
            rhs = relationship.rhs
            self.associates(lhs, rhs, associates_obj=relationship)
        elif isinstance(relationship, Causes):
            cause = relationship.cause
            effect = relationship.effect
            self.causes(cause, effect, relationship)
        elif isinstance(relationship, Moderates):
            self.moderates(
                moderator=relationship.moderator,
                on=relationship.on,
                moderates_obj=relationship,
            )
        elif isinstance(relationship, Repeats):  # TODO: Rename to Repeat?
            unit = relationship.unit
            measure = relationship.measure
            according_to = relationship.according_to
            self.repeat(unit=unit, measure=measure, repeat_obj=relationship)

    # Add an edge that indicates that identifier 'has' the variable measurement
    def has(
        self,
        identifier: AbstractVariable,
        variable: AbstractVariable,
        has_obj: Union[Has, Nests, Repeats],
        repetitions: NumberValue,
    ):
        if not self.has_variable(identifier):
            self._add_variable(variable=identifier, is_identifier=True)
        else:
            # Update the variable to have an identifier
            (node, node_data) = self.get_node(variable=identifier)
            node_data["is_identifier"] = True
        # Is this edge new?
        if not self.has_edge(start=identifier, end=variable, edge_type="has"):
            self._add_edge(
                start=identifier,
                end=variable,
                edge_type="has",
                edge_obj=has_obj,
                repetitions=repetitions,
            )

    # Add an ''associate'' edge to the graph
    # Adds two edges, one in each direction
    def associates(
        self,
        lhs: AbstractVariable,
        rhs: AbstractVariable,
        associates_obj: typing.Union[Associates, Moderates],
    ):
        # Is this edge new?
        if not self.has_edge(start=lhs, end=rhs, edge_type="associates"):
            assert not self.has_edge(start=rhs, end=lhs, edge_type="associates")
            self._add_edge(
                start=lhs, end=rhs, edge_type="associates", edge_obj=associates_obj
            )
            self._add_edge(
                start=rhs, end=lhs, edge_type="associates", edge_obj=associates_obj
            )

    # Add a causal edge to the graph
    def causes(
        self, cause: AbstractVariable, effect: AbstractVariable, causes_obj: Causes
    ):
        # Is this edge new?
        if not self.has_edge(start=cause, end=effect, edge_type="causes"):
            self._add_edge(
                start=cause, end=effect, edge_type="causes", edge_obj=causes_obj
            )

    def moderates(
        self,
        moderator: List[AbstractVariable],
        on: AbstractVariable,
        moderates_obj: Moderates,
    ):
        # First make sure that all the moderators are in the graph itself
        for m in moderator:
            if isinstance(m, Measure):
                # Get identifier for each moderator
                identifier = m.get_unit()
                assert identifier is not None
                # If the moderator is not in the graph, add it first
                if not self.has_edge(start=identifier, end=m, edge_type="has"):
                    relationship = m.get_unit_relationsihp()
                    self.has(
                        identifier,
                        m,
                        relationship,
                        repetitions=relationship.repetitions,
                    )

        # Create new interaction variable
        m_names = [m.name for m in moderator]
        name = "*".join(m_names)

        m_cardinality = 1
        for m in moderator:
            if m.get_cardinality() is not None:
                m_cardinality *= m.get_cardinality()

        var = Nominal(
            name, cardinality=m_cardinality
        )  # Interaction variables are cast as nominal variables

        # Add associate edges between interaction and @param on variable
        # associates_obj = Associates(lhs=var, rhs=on)
        # Store Moderates obj even though edge is an Associates edge
        self.associates(lhs=var, rhs=on, associates_obj=moderates_obj)

        # Inherit unit has relationships from moderators
        for m in moderator:
            identifier = self.get_identifier_for_variable(m)

            if identifier is not None:
                relationship = Has(
                    variable=identifier, measure=var, repetitions=m_cardinality
                )
                self.has(identifier, var, relationship, repetitions=m_cardinality)

    # Add an ambiguous/contribute edge to the graph
    def contribute(self, lhs: AbstractVariable, rhs: AbstractVariable):
        # Is this edge new?
        if not self.has_edge(start=lhs, end=rhs, edge_type="contribute"):
            self._add_edge(start=lhs, end=rhs, edge_type="contribute")

    # Add a 'treat' edge to the graph
    def treat(
        self,
        unit: AbstractVariable,
        treatment: AbstractVariable,
        treatment_obj: Measure,  # Used to be Treatment
    ):
        # Is this edge new?
        if not self.has_edge(start=treatment, end=unit, edge_type="treat"):
            self._add_edge(
                start=treatment, end=unit, edge_type="treat", edge_obj=treatment_obj
            )

    # Add a 'nests' edge to the graph
    def nests(self, base: Unit, group: Unit, nests_obj: Nests = None):
        # Is this edge new?
        if not self.has_edge(start=base, end=group, edge_type="nests"):
            # Mark as identifiers
            self._add_variable(base, is_identifier=True)
            self._add_variable(group, is_identifier=True)
            self._add_edge(start=base, end=group, edge_type="nests", edge_obj=nests_obj)

    # Add a 'repeat' edge to the graph
    def repeat(
        self,
        unit: Unit,
        measure: Measure,
        repeat_obj: Repeats,
    ):
        # Is this edge new?
        if not self.has_edge(start=unit, end=measure, edge_type="repeat"):
            self._add_edge(
                start=unit, end=measure, edge_type="repeat", edge_obj=repeat_obj
            )

    # # Generate Z3 consts that correspond to nodes in this graph
    # def generate_consts(self):
    #     pass

    # @returns sub-graph containing only conceptual edges
    def get_conceptual_subgraph(self):
        gr = copy.deepcopy(self)

        edges = self.get_edges()
        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            if edge_type == "causes" or edge_type == "associates":
                pass
            else:
                gr._graph.remove_edge(n0, n1)

        return gr

    # @returns sub-graph containing only CAUSAL edges
    def get_causal_subgraph(self):
        gr = copy.deepcopy(self)

        edges = self.get_edges()
        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            if edge_type == "causes":
                pass
            else:
                gr._graph.remove_edge(n0, n1)

        return gr

    # @returns sub-graph containing only NESTS edges
    def get_nesting_subgraph(self):
        gr = copy.deepcopy(self)
        nodes_to_remove = set()

        edges = self.get_edges()
        for (n0, n1, edge_data) in edges:
            edge_type = edge_data["edge_type"]
            if edge_type == "nests":
                edge_obj = edge_data["edge_obj"]
                assert isinstance(edge_obj, Nests)
            else:
                gr._graph.remove_edge(n0, n1)
                n0_var = gr.get_variable(n0)
                n1_var = gr.get_variable(n1)
                # If all the edges have been removed from a node, remove the node from the graph
                # but make sure not to prematurely remove Units
                if len(gr._graph.edges(n0)) == 0 and not isinstance(n0_var, Unit):
                    # gr._graph.remove_node(n0)
                    nodes_to_remove.add(n0)
                if len(gr._graph.edges(n1)) == 0 and not isinstance(n1_var, Unit):
                    # gr._graph.remove_node(n1)
                    nodes_to_remove.add(n1)

        for n in nodes_to_remove:
            gr._graph.remove_node(n)

        return gr

    # Remove outgoing associative relationships from the DV
    # Remove outgoing edges from @param variable
    def remove_outgoing_edges(self, variable: AbstractVariable):
        assert self.has_variable(variable)
        gr = copy.deepcopy(self)

        # Iterate over outgoing edges from dv
        for n in self._graph.neighbors(variable.name):
            gr._graph.remove_edge(variable.name, n)

        return gr
