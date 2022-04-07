build:
	docker build --tag monte_py .

run:
	docker run --rm --name mvm_blog monte_py --cvs=2
