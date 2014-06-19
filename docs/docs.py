"""this script make it crzy easy to build docs with sphinx.
before use this script, you need install sphinx_rtd_theme.

Noice:
    autodoc: automatically insert docstrings from modules (y/n) [n]: y
you have to answer y to use the feature automatically insert docstrings from your modules.

usage::
    python docs.py /path/to/your/project/
    
That's it~
"""
import os
import time
import sys
import fileinput


def path_and_theme(path):
    processing = False
    theming = False

    for line in fileinput.input("conf.py", inplace=1):
        if line.startswith("import os"):
            processing = True
        else:
            if processing:
                sys.stdout.write("sys.path.append('%s')" % path)
            processing = False
        if line.startswith("html_theme = "):
            theming = True
            line = line.replace('html_theme = "default"', '')
        else:
            if theming:
                sys.stdout.write("import sphinx_rtd_theme\n")
                sys.stdout.write("html_theme = 'sphinx_rtd_theme'\n")
                sys.stdout.write("html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]\n")
            theming = False
        sys.stdout.write(line)


def modify_index_rst(current_path):
    rsting = False
    rstlist = []

    for file in os.listdir(current_path):
        if file.endswith(".rst") and not file.startswith("index.rst"):
            rstlist.append("   %s" % file.rsplit(".", 1)[0])

    rst_str = "\n".join(rstlist)

    for line in fileinput.input("index.rst", inplace=1):
        if line.strip().startswith(":maxdepth:"):
            rsting = True
            sys.stdout.write("\n")
        else:
            if rsting:
                sys.stdout.write(rst_str)
            rsting = False
        sys.stdout.write(line)


if __name__ == "__main__":
    path = sys.argv[1:]
    if len(path) == 0:
        print("project path is missed!")
        sys.exit(-1)
    path = path[0]
    os.system("sphinx-quickstart")
    time.sleep(1)

    path_and_theme(path)
    current_path = os.getcwd()
    os.chdir(path)
    os.system("sphinx-apidoc %s -o %s" % (path, current_path))

    time.sleep(0.5)
    os.chdir(current_path)
    modify_index_rst(current_path)
    os.system("make html")
    time.sleep(0.5)
    os.chdir(current_path + "/_build/html/")
    os.system("python -m SimpleHTTPServer")
