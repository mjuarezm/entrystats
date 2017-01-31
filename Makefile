all: build run destroy

build:
	mkdir -p results
	docker build -t entrystats --rm .

collect:
	docker run -v `pwd`:/entrystats -it --privileged entrystats sh -c 'tor --ControlPort 9051 --RunAsDaemon 1; sleep 5; python entry_stats.py'

analyse:
	docker run -v `pwd`:/entrystats -it --privileged entrystats sh -c 'jupyter nbconvert --execute stats_analysis.ipynb'

destroy:
	docker stop `docker ps -a -q -f ancestor=entrystats`
	docker rm `docker ps -a -q -f ancestor=entrystats`
	docker rmi -f entrystats

clean:
	rm -rf *.pdf
	rm -rf results/*

reset: destroy clean
