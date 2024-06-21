

## Spack-freeze

a [Spack extension](https://spack.readthedocs.io/en/latest/extensions.html#custom-extensions) to generate a packages.yaml fragment listing a package and its dependencies as non-buildable externals.


### Usage

In most cases you can just do:

  spack freeze package@version > freeze_package.yaml


You can then include freeze_package.yaml in an envrionment spack.yaml file
to use that package as a dependency.

### Installation

After cloning the repository somewhere, See the [Spack docs](https://spack.readthedocs.io/en/latest/extensions.html#configure-spack-to-use-extensions) on adding the path to config.yaml under 'extensions:'
