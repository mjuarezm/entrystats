Little tool to collect and analyse statistics about TCP stack properties of all Tor entry guards.

Data collection
---------------

 1. Install `docker`: [installation instructions](https://docs.docker.com/engine/installation/)

 1. Clone the repo: `git clone https://github.com/mjuarezm/entrystats.git`

 1. Build docker image: `make build`

 1. Collect measurements in a docker instance: `make collect`

Analysis
--------

1. Run analysis scripts: `make analyse`

1. Check results in `results_analysis.html`
