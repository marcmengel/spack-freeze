import sys
import os
import spack.config
import spack.cmd
import spack.cmd.common.arguments as arguments

def setup_parser(subparser):
    arguments.add_common_arguments(subparser, ["constraint"])

    
def freeze(parser, args):
    #print("parser is " + repr(parser) + "args: " + repr(args))
    results = args.specs()
    print(f"#need to handle: {results[0].__dict__}")
    print(f"#have {results[0].name} hash {results[0]._hash}")

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
                specstr = line[:ppos-1]
                path = line[ppos:]
                name = line[:apos]
                if name in did_already:
                    continue
                did_already.add(name)

                print(f"  {name}:\n    externals:\n    - spec: {specstr}\n      prefix: {path}\n      buildable: false")


