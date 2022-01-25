.PHONY: ssh-tunnel

ssh-tunnel:
	ssh -L 9000:192.168.2.111:554 -L 9001:192.168.2.112:554 -L 8999:192.168.2.201:139 -o ServerAliveInterval=30 alex@sifklic.sif-revetement.com -p 30022

install:
	. ./env/bin/activate; \
	pip install -r requirements.txt; \
	yarn;

api-server:
	. ./env/bin/activate; \
	python sifapi/manage.py runserver

frontend-server:
	yarn start
