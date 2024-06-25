import sys
import os
import spack.config
import spack.cmd
import spack.cmd.common.arguments as arguments

description = "Build packages.yaml fragment to freeze a package in an environment"
section = "basic"
level = "short"

def setup_parser(subparser):
    arguments.add_common_arguments(subparser, ["constraint"])

    
def freeze(parser, args):
    #print("parser is " + repr(parser) + "args: " + repr(args))
    results = args.specs()
    print(f"# spack freeeze of {results[0].name}/{results[0]._hash[:8]}")

    print("packages:")
    did_already = set()
    for spec in results:
        with os.popen(f"spack find -dpvf {spec.name}/{spec._hash}") as sffd:
            for line in sffd:
                line = line.strip()
                if line.startswith("--") or line.startswith('==') or not line:
                    continue
                ppos = line.find('/')
                apos = line.find('@')
                specstr = line[:ppos-1].strip()
                path = line[ppos:]
                name = line[:apos]
                if name in did_already:
                    continue
                did_already.add(name)
                print(f"  {name}:\n    externals:\n    - spec: {specstr}\n      prefix: {path}\n      buildable: false")


