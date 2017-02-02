Little tool to collect and analyse statistics about TCP stack properties of all Tor entry guards.

Data collection
---------------

 1. Install `docker`: [installation instructions](https://docs.docker.com/engine/installation/) (docker should be able to run without sudo)

 1. Clone the repo: `git clone https://github.com/mjuarezm/entrystats.git`

 1. Build docker image: `make build`

 1. Collect measurements in a docker instance: `make collect`

Analysis
--------

1. Install Jupyter notebook: [installation instructions](http://jupyter.readthedocs.io/en/latest/install.html)

1. You may need to install the following dependencies: `matplotlib`, `numpy`, `pandas`

1. Run analysis scripts: `make analyse`

1. Check results in `results_analysis.html`

All
---

You can collect and then run the analyses by doing: `make all`
