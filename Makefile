all: build collect analyse destroy

build:
	mkdir -p results
	docker build -t entrystats --rm .

collect:
	docker run -v `pwd`:/entrystats -it --privileged entrystats

analyse:
	jupyter nbconvert  --ExecutePreprocessor.timeout=600 --execute stats_analysis.ipynb

stop:
	docker stop `docker ps -a -q -f ancestor=entrystats`
	docker rm `docker ps -a -q -f ancestor=entrystats`

destroy: stop
	docker rmi -f entrystats

clean:
	rm -rf *.html
	rm -rf results/*

reset: stop destroy clean
