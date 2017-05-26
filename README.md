Django app for exploring the offline forms found on GOV.UK

Reference data from GOV.UK and registers is loaded from [government-form-data](https://github.com/openregister/government-form-data).

## Running Locally

Depends upon [Python 3](http://install.python-guide.org)

```sh
$ make clean

$ make init
$ make migrate

$ make server
```
