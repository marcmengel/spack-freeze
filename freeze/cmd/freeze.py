import sys
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
    arguments.add_common_arguments(subparser, ["constraint"])
    subparser.add_argument("--file", help="file to write package definitions")


def freeze(parser, args):
    # print("parser is " + repr(parser) + "args: " + repr(args))

    # dont get color strings in the specs...
    llnl.util.tty.color.set_color_when(False)

    env = ev.active_environment()
    file = None
    results = args.specs()
    if env and not args.file:
        file = f"{env.path}/freeze.{results[0]._hash[:8]}.yaml"
    elif args.file:
        file = args.file
    else:
        print("# no --file and no environment, printing to stdout")

    if file:
        with open(file, "w") as ofd:
            freeze2(parser, args, ofd, results)
    else:
        freeze2(parser, args, sys.stdout, results)

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


def freeze2(parser, args, outf, results):
    print(f"# spack freeeze of {results[0].name}/{results[0]._hash[:8]}", file=outf)
    print("packages:", file=outf)
    did_already = set()
    for spec in results:
        for dep in spec.traverse():
            # don't export our externals
            if dep.external:
                continue
            path = dep.prefix
            name = dep.name
            key = name + path
            specstr = dep.cformat(
                "{name} {@version} {variants} {%compiler.name}{@compiler.version}"
            )
            # gcc-runtime and glx are packages that shouldn't be exported
            if key in did_already or name == "gcc-runtime" or name == "glx":
                continue
            did_already.add(key)
            print(
                f"  {name}:\n    externals:\n    - spec: {specstr}\n      prefix: {path}\n      buildable: false",
                file=outf,
            )
