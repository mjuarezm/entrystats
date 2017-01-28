all: clean build run

build:
	docker build -t entrystats --rm .

run:
	docker run -it --privileged entrystats "python ./entry_stats.py"

clean:
	docker stop `docker ps -a -q -f ancestor=entrystats`
	docker rm `docker ps -a -q -f ancestor=entrystats`
	docker rmi -f entrystats
