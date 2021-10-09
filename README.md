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

# Tunnels SSH

Pour avoir access au Server samba (port 139) on ouvre un port local (-L) qui va nous connecter
au server samba sur 192.168.2.200:139 a travers un tunnle ssh


ssh -o ServerAliveInterval=30 -L 8999:192.168.2.201:139 alex@sifklic.sif-revetement.com -p 30022


Pour avoir access a quelques cameras

 ssh -L 9000:192.168.2.111:554 -L 9001:192.168.2.112:554 -o ServerAliveInterval=30 alex@82.127.103.1 -p 30022

# Server Samba local:

We create a local samba server for development purposes.

OSX doesn't allow connection to localhost so we create a 127.0.0.2 interface 

docker run -it \
      --expose 137 -p 127.0.0.2:137:137  \
      --expose 138 -p 127.0.0.2:138:138  \
      --expose 139 -p 127.0.0.2:139:139  \
      --expose 445 -p 127.0.0.2:445:445 \
      -d dperson/samba -p \
      -u "exaged;Ged.2020" \
      -s "Workspace$;/share;yes;no;no" \
      -g "netbios name=SIF-NEW" \
      -g "server min protocol = LANMAN1"

