init:
	- pipenv install
	- cd django_sourcebook
	- python manage.py makemigrations
	- python manage.py migrate
	- python manage.py get_credentials
	- ls initial_data/*.json | xargs -I {} python manage.py loaddata {}