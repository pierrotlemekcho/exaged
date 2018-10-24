# exaged

## Virtualenv

```
virtualenv -p python3 env

. ./env/bin/activate
pip install -r requirements.txt
```

## Configuration
Pour pouvoir utliser exaged il faut modifier exaged.ini

```
database_url = 
exact_api_config_file = 
```

## Database
- Creer un base de donees vide
```
mysql> CREATE DATABASE exaged;
```
- modifier alembic.ini sqlalchemy.url

- Appliquer les migrations definies dans le dossier `./alembic/versions`
```
$> PYTHONPATH=. alembic upgrade head
```

## Synchronization

```
python sync_exaged.py
```
