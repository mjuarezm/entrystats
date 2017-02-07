all: build collect analyse destroy

build:
	mkdir -p results
	docker build -t nodestats --rm .

collect:
	docker run -v `pwd`:/nodestats -it --privileged nodestats

analyse:
	jupyter nbconvert  --ExecutePreprocessor.timeout=600 --execute stats_analysis.ipynb

stop:
	docker stop `docker ps -a -q -f ancestor=nodestats`
	docker rm `docker ps -a -q -f ancestor=nodestats`

destroy: stop
	docker rmi -f nodestats

clean:
	rm -rf *.html
	rm -rf results/*

reset: stop destroy clean
