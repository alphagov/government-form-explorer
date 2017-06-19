[Django](https://www.djangoproject.com/) app for exploring offline forms found on GOV.UK using data
loaded from [government-form-data](https://github.com/openregister/government-form-data).

- https://government-form-explorer.cloudapps.digital

# Building

Depends upon [Python 3](http://install.python-guide.org)
– we recommend using a [Python virtual environment](http://virtualenvwrapper.readthedocs.org/en/latest/):

```sh
$ mkvirtualenv -p python3 government-form-explorer
$ workon government-form-explorer
$ make clean

$ make init
$ make flake8
```

# Running locally

Create and configure your postgres database:

```sh
$ psql
hello=# CREATE DATABASE forms;
^D

$ export DATABASE_URL=postgres://username:password@localhost/forms

$ make migrate
```

Search depends up an Elasticsearch index of documents, produced and loaded by [government-form-data](https://github.com/openregister/government-form-data).

You can run an Elasticsearch locally, or use a hosted instance, such as Amazon Cloudsearch:

```sh
$ export ES_REGION=eu-west-1
$ export ES_HOST=search-government-form-odsdfdsfllfdsfdszzqddfflsu.eu-west-1.es.amazonaws.com
$ export ES_ACCESS_KEY='QQAS6AADCQQ999TYLDAZ'
$ export ES_SECRET_KEY='343fdsfsdf2323fdsf244fdfdsf213344XZZccYx'
```

```sh
$ make server
```

Load the data from the [government-form-data](https://github.com/openregister/government-form-data) project.

```sh
$ make load
```
