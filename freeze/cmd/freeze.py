import sys
import re
import os
import spack.config
import spack.cmd
import spack.environment as ev
import spack.cmd.common.arguments as arguments
import spack.util.spack_yaml as syaml
import llnl.util.tty.color


description = "Build packages.yaml fragment to freeze a package in an environment"
section = "environments"
level = "short"


def setup_parser(subparser):
    arguments.add_common_arguments(subparser, ["spec"])
    subparser.add_argument("--file", help="file to write package definitions")


def freeze(parser, args):
    # print("parser is " + repr(parser) + "args: " + repr(args))

    # dont get color strings in the specs...
    llnl.util.tty.color.set_color_when(False)

    # try to expand specs with -E and then turn it back off...
    args.no_env = True

    specs = spack.cmd.parse_specs(args.spec)

    if not specs:
        tty.die("You must supply a spec.")

    if len(specs) != 1:
        tty.die("Too many specs.  Supply only one.")

    spec = spack.cmd.disambiguate_spec(specs[0], None, first=False)

    args.no_env = False

    env = ev.active_environment()
    file = None
    if env and not args.file:
        file = f"{env.path}/freeze.{spec._hash[:8]}.yaml"
    elif args.file:
        file = args.file
    else:
        print("# no --file and no environment, printing to stdout")

    if file:
        with open(file, "w") as ofd:
            freeze2(parser, args, ofd, spec)
    else:
        freeze2(parser, args, sys.stdout, spec)

    if env and file:
        add_include(file, env.path + "/spack.yaml")


def add_include(include_file, file):
    with open(file, "r") as fin:
        fdict = syaml.load(fin)

    # if the file is in the environment, use the basname not the full path
    if os.path.dirname(include_file) == os.path.dirname(file):
        include_file = os.path.basename(include_file)

    if not fdict["spack"].get("include", None):
        fdict["spack"]["include"] = []

    if include_file in fdict["spack"]["include"]:
        print(f"{include_file} already included in {file}")
    else:
        print(f"adding include for {include_file} to  {file}")
        fdict["spack"]["include"].append(include_file)
        with open(file, "w") as fout:
            syaml.dump(fdict, fout)


def freeze2(parser, args, outf, spec):
    print(f"# spack freeeze of {spec.name}/{spec._hash[:8]}", file=outf)
    print("packages:", file=outf)
    did_already = set()
    for dep in spec.traverse():

        name = dep.name

        # don't export our externals
        if dep.external:
            continue

        # gcc-runtime and glx are packages that shouldn't be exported
        if name in did_already or name == "gcc-runtime" or name == "glx":
            continue
        did_already.add(name)

        requirebits = dep.cformat(
            "{name}:\n    require:\n    - '{@version}'\n    - '{variants}'\n    - '{%compiler.name}{@compiler.version}'"
        )
        requirebits = re.sub('patches=[^ ]*', '', requirebits)

        print(" ", requirebits, file=outf)
