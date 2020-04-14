# ph-hospital

## Setup
Use Python 3

Install dependencies with
```
$ pip install -r requirements.txt
```

Setup the database with
```
$ flask db upgrade
```

## Develop

Run app with
```
$ flask run
```

Access it on [localhost](localhost:5000)

## Add New Dependencies

```
# install em with pip in the venv
$ pip freeze --local > requirements.txt
```

## Testing email services

Set the `FLASK_DEBUG` to 0 on `.flaskenv` and open a local email
server like so:

```
$ python -m smtpd -n -c DebuggingServer localhost:8025
```