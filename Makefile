all:	flake8

refresh:	clean init migrate load

server:
	python manage.py runserver

init:
	pip install -r requirements.txt
	python manage.py collectstatic

migrate:
	python manage.py makemigrations pages
	python manage.py migrate

load:
	python manage.py load

flake8:
	flake8

clean::
	rm -rf explorer/staticfiles
	find . -name '*.pyc' | xargs rm -f
	find . -name '__pycache__' | xargs rm -rf
