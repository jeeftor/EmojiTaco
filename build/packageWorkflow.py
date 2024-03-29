#!/usr/bin/env python
#
# Copyright (c) 2013 deanishe@deanishe.net.
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2013-11-01
#

"""workflow-build [options] <workflow-dir>

Build Alfred Workflows.

Compile contents of <workflow-dir> to a ZIP file (with extension
`.alfredworkflow`).

The name of the output file is generated from the workflow name,
which is extracted from the workflow's `info.plist`. If a `version`
file is contained within the workflow directory, it's contents
will be appended to the compiled workflow's filename.

Usage:
    workflow-build [-v|-q|-d] [-f] [-o <outputdir>] <workflow-dir>...
    workflow-build (-h|--version)

Options:
    -o, --output=<outputdir>    Directory to save workflow(s) to.
                                Default is current working directory.
    -f, --force                 Overwrite existing files.
    -h, --help                  Show this message and exit.
    -V, --version               Show version number and exit.
    -q, --quiet                 Only show errors and above.
    -v, --verbose               Show info messages and above.
    -d, --debug                 Show debug messages.

"""


import sys
import os
import logging
import logging.handlers
import plistlib
import semantic_version

from subprocess import check_call, CalledProcessError

from docopt import docopt

__version__ = "0.2"
__author__ = "deanishe@deanishe.net"

DEFAULT_LOG_LEVEL = logging.WARNING
LOGPATH = os.path.expanduser("~/Library/Logs/MyScripts.log")
LOGSIZE = 1024 * 1024 * 5  # 5 megabytes


EXCLUDE_PATTERNS = [
    "*.pyc",
    "*.log",
    ".DS_Store",
    "*.acorn",
    "*.swp",
    "*.sublime-project",
    "*.sublime-workflow",
    "*.git",
    "*.dist-info",
    "*.idea",
    ".idea",
    ".git",
    "./eenv/*",
    "./img/*.png",
    "/build/*",
    "/sketch/*",
    "*.csv",
    "*.alfredworkflow",
]


class TechnicolorFormatter(logging.Formatter):
    """
    Prepend level name to any message not level logging.INFO.

    Also, colour!

    """

    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET = "\033[0m"
    COLOUR_BASE = "\033[1;{:d}m"
    BOLD = "\033[1m"

    LEVEL_COLOURS = {
        logging.DEBUG: BLUE,
        logging.INFO: WHITE,
        logging.WARNING: YELLOW,
        logging.ERROR: MAGENTA,
        logging.CRITICAL: RED,
    }

    def __init__(self, fmt=None, datefmt=None, technicolor=True):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.technicolor = technicolor
        self._isatty = sys.stderr.isatty()

    def format(self, record):
        if record.levelno == logging.INFO:
            msg = logging.Formatter.format(self, record)
            return msg
        if self.technicolor and self._isatty:
            colour = self.LEVEL_COLOURS[record.levelno]
            bold = (False, True)[record.levelno > logging.INFO]
            levelname = self.colourise(f"{record.levelname:9s}", colour, bold)
        else:
            levelname = f"{record.levelname:9s}"
        return levelname + logging.Formatter.format(self, record)

    def colourise(self, text, colour, bold=False):
        colour = self.COLOUR_BASE.format(colour + 30)
        output = []
        if bold:
            output.append(self.BOLD)
        output.append(colour)
        output.append(text)
        output.append(self.RESET)
        return "".join(output)


# logfile
logfile = logging.handlers.RotatingFileHandler(LOGPATH, maxBytes=LOGSIZE, backupCount=5)
formatter = logging.Formatter(
    "%(asctime)s %(levelname)-8s [%(name)-12s] %(message)s", datefmt="%d/%m %H:%M:%S"
)
logfile.setFormatter(formatter)
logfile.setLevel(logging.DEBUG)

# console output
console = logging.StreamHandler()
formatter = TechnicolorFormatter("%(message)s")
console.setFormatter(formatter)
console.setLevel(logging.DEBUG)

log = logging.getLogger("")
log.addHandler(logfile)
log.addHandler(console)


def safename(name):
    """Make name filesystem-safe."""
    name = name.replace("/", "-")
    name = name.replace(":", "-")
    return name


def build_workflow(workflow_dir, outputdir, overwrite=False, verbose=False):
    """Create an .alfredworkflow file from the contents of `workflow_dir`."""
    curdir = os.curdir
    os.chdir(workflow_dir)
    version = None
    if not os.path.exists("info.plist"):
        log.error("info.plist not found")
        return False

    if os.path.exists("version"):

        # Read version
        with open("version") as fp:
            initial_version = semantic_version.Version.coerce(
                fp.read().strip().decode("utf-8")
            )
            fp.close()
            version = str(initial_version.next_patch())

            target = open("version", "w")
            target.truncate()
            target.write(version)
            target.close()

    if not version:
        with open('info.plist', 'rb') as f:
            pl = plistlib.load(f)
        initial_version = semantic_version.Version.coerce(pl["version"])
        version = str(initial_version.next_patch())

        pl["version"] = version
        with open('info.plist', 'wb') as f:
            plistlib.dump(pl, f)

            # plistlib.writePlist(pl, "info.plist")
    with open('info.plist', 'rb') as f:
        pl = plistlib.load(f)
        name = safename(pl["name"]).replace(" ", "_")
        zippath = os.path.join(outputdir, name)

    if version:
        zippath += "-" + version
    zippath += ".alfredworkflow"

    if os.path.exists(zippath):
        if overwrite:
            log.info("Overwriting existing workflow")
            os.unlink(zippath)
        else:
            log.error(f"File '{zippath}' already exists. Use -f to overwrite")
            return False

    # build workflow
    command = ["zip"]
    if not verbose:
        command.append("-q")
    command.append(zippath)
    for root, dirnames, filenames in os.walk("."):
        dirnames[:] = [d for d in dirnames if not d in [".git", ".idea"]]
        for filename in filenames:
            path = os.path.join(root, filename)
            command.append(path)
    command.append("-x")
    command.extend(EXCLUDE_PATTERNS)
    log.debug("command : {}".format(" ".join(command)))
    try:
        check_call(command)
    except CalledProcessError as err:
        log.error(f"zip returned : {err.returncode}")
        os.chdir(curdir)
        return False
    log.info(f"Wrote {zippath}")
    # Return workflow filename and actual filename
    print(name, os.path.basename(zippath), version)
    os.chdir(curdir)
    return True


def main(args=None):
    """Run CLI."""
    args = docopt(__doc__, version=__version__)

    if args.get("--verbose"):
        log.setLevel(logging.INFO)
    elif args.get("--quiet"):
        log.setLevel(logging.ERROR)
    elif args.get("--debug"):
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(DEFAULT_LOG_LEVEL)

    log.debug("Set log level to %s" % logging.getLevelName(log.level))

    log.debug(f"args :\n{args}")

    # Build options
    outputdir = os.path.abspath(args.get("--output") or os.curdir)
    workflow_dirs = [os.path.abspath(p) for p in args.get("<workflow-dir>")]
    log.debug(f"outputdir : {outputdir}, workflow_dirs : {workflow_dirs}")
    errors = False
    verbose = False
    if log.level == logging.DEBUG:
        verbose = True

    # Build workflow(s)
    for path in workflow_dirs:
        ok = build_workflow(path, outputdir, args.get("--force"), verbose)
        if not ok:
            errors = True
    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
