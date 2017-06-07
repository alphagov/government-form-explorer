all:	flake8

refresh:	clean init static migrate load

server:
	python3 manage.py runserver

init:
	pip3 install -r requirements.txt

static:
	python3 manage.py collectstatic --noinput --clear

migrate:
	python3 manage.py makemigrations pages
	python3 manage.py migrate

load:
	python3 manage.py load organisations
	python3 manage.py load pages
	python3 manage.py load attachments
	python3 manage.py load history
	python3 manage.py load downloads

flake8:
	flake8

clean::
	rm -rf explorer/staticfiles
	find . -name '*.pyc' | xargs rm -f
	find . -name '__pycache__' | xargs rm -rf
