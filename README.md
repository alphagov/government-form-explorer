[Django](https://www.djangoproject.com/) app for exploring offline forms found on GOV.UK using data
loaded from [government-form-data](https://github.com/openregister/government-form-data).

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

```
$ psql
hello=# CREATE DATABASE forms;
^D

$ export DATABASE_URL=postgres://username:password@localhost/forms
```

```sh
$ make migrate
$ make server
```

Load the data from the [government-form-data](https://github.com/openregister/government-form-data) project.

```sh
$ make load
```
