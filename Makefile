.PHONY: test

init:
	- pipenv install
	- cd django_sourcebook
	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py get_credentials
	- ls initial_data/*.json | xargs -I {} python manage.py loaddata {}

test:
	- find django_sourcebook/ -name *.py | xargs black
	- export DEBUG_TOOLBAR=OFF
	- nohup python django_sourcebook/manage.py runserver &
	- pytest django_sourcebook/
	- exit