

default: requirements static

requirements:
	pip install -r requirements.txt
	mkdir -p public/media
	mkdir -p public/static

static:
	python src/manage.py collectstatic --noinput -v0 -c

