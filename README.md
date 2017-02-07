# NodeStats

Small script to collect and analyse statistics about TCP stack properties of all Tor nodes.

## Data collection

 1. Install `docker`: [installation instructions](https://docs.docker.com/engine/installation/) (docker should be able to run without sudo)

 1. Clone the repo: `git clone https://github.com/mjuarezm/nodestats.git`

 1. Build docker image: `make build`

 1. Collect measurements in a docker instance: `make collect`

## Analysis

1. Install Jupyter notebook: [installation instructions](http://jupyter.readthedocs.io/en/latest/install.html)

1. You may need to install the following dependencies: `matplotlib`, `numpy`, `pandas`

1. Run analysis scripts: `make analyse`

1. Check results in `stats_analysis.html`

## Logs and data

Logs and data are dumped in `<tiestamp>.log` and `<timestamp>.csv` in `results/`.

## Example

Here there is an example on how the output of the analysis looks like: [stats_analysis.html](http://homes.esat.kuleuven.be/~mjuarezm/tmp/stats_analysis.html)
