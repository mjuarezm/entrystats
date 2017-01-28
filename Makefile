all: clean build run

build:
	docker build -t entrystats --rm .

run:
	docker run -it --privileged entrystats

clean:
	docker rmi -f entrystats
