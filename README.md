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

# Deployer le Frontend

## Installer les dependences
```
$> yarn install
```
## Constuire le html
```
$> REACT_APP_API_URL=/api yarn build
```
## Deployer dans apache
```
$> cp -r  build/* /var/www/exacam/
```

# Server Samba local:

We create a local samba server for development purposes.

OSX doesn't allow connection to localhost so we create a 127.0.0.2 interface 

```
sudo ifconfig lo0 alias 127.0.0.2 up
```

```
docker run -it \
      --expose 137 -p 127.0.0.2:137:137  \
      --expose 138 -p 127.0.0.2:138:138  \
      --expose 139 -p 127.0.0.2:139:139  \
      --expose 445 -p 127.0.0.2:445:445 \
      -d dperson/samba -p \
      -u "user;password" \
      -s "Workspace$;/share;yes;no;no" \
      -g "netbios name=NAME" \
      -g "server min protocol = LANMAN1"
```
