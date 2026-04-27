.PHONY: run migrate makemigrations shell

run:
	python3 manage.py runserver

migrate:
	python3 manage.py migrate

makemigrations:
	python3 manage.py makemigrations

shell:
	python3 manage.py shell_plus