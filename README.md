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

To initialize the database run this (warning: it deletes all users)

```
$ flask setup-debug-database
```

This creates a default user with username 'tim' and password 'tim'.

## Add New Dependencies

```
# install em with pip in the venv
$ pip freeze --local > requirements.txt
```

## Testing email services

Open a local email server like so:

```
$ flask open-mail-server
```
