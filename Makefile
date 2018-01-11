.PHONY: build run

build:
	docker build -t moose/bakedbeans .

run: build
	docker run -it --rm -p 3000:3000 -v $(PWD)/contents:/contents moose/bakedbeans
