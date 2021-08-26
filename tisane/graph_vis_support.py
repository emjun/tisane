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
                    nests/.style={dashed},
                    depvar/.style={draw=none,fill=grey!30}]
"""

graph = """    \\graph[layered layout,sibling distance={},level distance={}]{}
"""

tikz_template_end = """    };
\\end{tikzpicture}
"""
document_end = """
\\end{document}
"""

dot_formats = [
    "bmp",
    "canon",
    # "cgimage",
    "cmap",
    "cmapx",
    "cmapx_np",
    "dot",
    "dot_json",
    "eps",
    "exr",
    "fig",
    "gd",
    "gd2",
    "gif",
    "gv",
    "icns",
    "ico",
    "imap",
    "imap_np",
    "ismap",
    "jp2",
    "jpe",
    "jpeg",
    "jpg",
    "json",
    "json0",
    "mp",
    "pct",
    "pdf",
    "pic",
    "pict",
    "plain",
    "plain-ext",
    "png",
    "pov",
    "ps",
    "ps2",
    "psd",
    "sgi",
    "svg",
    "svgz",
    "tga",
    "tif",
    "tiff",
    "tk",
    "vdx",
    "vml",
    "vmlz",
    "vrml",
    "wbmp",
    "webp",
    "xdot",
    "xdot1.2",
    "xdot1.4",
    "xdot_json",
]
dot_formats_extensions = {
    "bmp": {"description": "", "extensions": ["bmp"]},
    "canon": {
        "description": "Pretty-printed DOT, without layout calculations",
        "extensions": ["dot"],
    },
    "dot": {"description": "DOT, with layout calculations", "extensions": ["dot"]},
    "dot_json": {"description": "", "extensions": ["json"]},
    "eps": {
        "description": "Encapsulated PostScript",
        "extensions": ["eps", "epsi", "epsf"],
    },
    "exr": {"description": "OpenEXR", "extensions": ["exr"]},
    "fig": {"description": "Xfig, the FIG graphics language", "extensions": []},
    "gif": {"description": "Graphics Interchange Format", "extensions": ["gif"]},
    "gv": {"description": 'Alias for the "dot" format', "extensions": ["dot"]},
    "icns": {"description": "Apple Icon Image", "extensions": ["icns"]},
    "ico": {"description": "Windows Icon", "extensions": ["ico"]},
    "jp2": {"description": "JPEG 2000", "extensions": ["jp2"]},
    "jpe": {"description": "Joint Photographic Experts Group", "extensions": ["jpe"]},
    "jpeg": {"description": "Joint Photographic Experts Group", "extensions": ["jpeg"]},
    "jpg": {"description": "Joint Photographic Experts Group", "extensions": ["jpg"]},
    "json": {
        "description": "JavaScript Object Notation, containing information produced by xdot",
        "extensions": ["json"],
    },
    "json0": {
        "description": "JavaScript Object Notation, containing information produced by dot",
        "extensions": ["json"],
    },
    "pdf": {"description": "Portable Document Format", "extensions": ["pdf"]},
    "png": {"description": "Portable Network Graphics", "extensions": ["png"]},
    "ps": {"description": "Adobe PostScript", "extensions": ["ps"]},
    "ps2": {
        "description": "Adobe PostScript for Portable Document Format (PDF), PostScript output with PDF notations",
        "extensions": ["ps"],
    },
    "psd": {"description": "Adobe Photoshop Document", "extensions": ["psd"]},
    "svg": {"description": "Scalable Vector Graphics", "extensions": ["svg"]},
    "svgz": {
        "description": "Compressed Scalable Vector Graphics",
        "extensions": ["svg"],
    },
    "tga": {
        "description": "Truevision TGA",
        "extensions": ["tga", "icb", "vda", "vst"],
    },
    "tif": {"description": "Tag Image File Format", "extensions": ["tiff"]},
    "tiff": {"description": "Tag Image File Format", "extensions": ["tiff"]},
    "wbmp": {"description": "Wireless Bitmap", "extensions": [".wbmp"]},
    "xdot": {
        "description": "Extended DOT format, with more detailed information about graph drawing",
        "extensions": ["xdot"],
    },
    "xdot1.2": {
        "description": "Extended DOT format, using xdot version 1.2",
        "extensions": ["xdot"],
    },
    "xdot1.4": {
        "description": "Extended DOT format, using xdot version 1.4",
        "extensions": ["xdot"],
    },
}
pydot_formats = [
    "canon",
    "cmap",
    "cmapx",
    "cmapx_np",
    "dia",
    "dot",
    "fig",
    "gd",
    "gd2",
    "gif",
    "hpgl",
    "imap",
    "imap_np",
    "ismap",
    "jpe",
    "jpeg",
    "jpg",
    "mif",
    "mp",
    "pcl",
    "pdf",
    "pic",
    "plain",
    "plain-ext",
    "png",
    "ps",
    "ps2",
    "svg",
    "svgz",
    "vml",
    "vmlz",
    "vrml",
    "vtx",
    "wbmp",
    "xdot",
    "xlib",
]

default_dot_edge_style = {
    "associates": "",
    "causes": "",
    "nests": "dashed",
    "has": "dotted",
    "default": "solid",
}
default_dot_edge_color = {"default": "black"}
default_dot_edge_label = {"associates": "assoc.", "causes": "cause", "default": ""}


def indent(code):
    return "\t" + re.sub(r"\n", "\n\t", code)


def formatTikzVis(
    graphCode="", nodesCode="", siblingDistance=1, levelDistance=1, fullDocument=True
):
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
