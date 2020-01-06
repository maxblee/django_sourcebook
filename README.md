# A Django Toolkit for Journalism

## Table of Contents
- [Setup and installation](#setup-and-installation)
- FOIA
    - [Templates](#templates)
- [Future Roadmap](#future-roadmap)

## Setup and Installation

This project requires PostGreSQL and Python 3.6 or greater. You will need to have them installed prior to running this program.
In addition, you will need to set up a new database for the project and enter information about the database in your project
`settings` folder. By default, this grabs the username and password for your database from environment settings and specifies
that the name of your database is `sourcebook`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': "sourcebook",
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PWD"],
        "HOST": "localhost",
        "PORT": "",
    }
}
```

You can of course override this behavior.

In addition, you should set the GMail address you want your FOIA requests sent from in your `settings` file:

```python
FROM_EMAIL = "givemerecords@gmail.com"
```

After setting up your database, you should run a virtual environment, migrate your changes into your database, add
your GMail credentials so you can file FOIA requests, and load initial data into your database (this is mostly default information about states and their public records laws). Assuming you have `pipenv` and `make` installed,
this should be as easy as running:

```bash
$ make init
```

From here, you should be able to run

```bash
$ python manage.py runserver
```

## FOIA
### Templates

Creating FOIA templates in this tool is fairly simple. But the tool is also picky about how you format things.

First of all, your federal FOIA template should go into the `FEDERAL_FOIA_TEMPLATE` location within your `MEDIA_ROOT/foia_templates` in `settings`. The same principal goes with a base request you use to file FOIA requests in places where you don't have a blanket form. But in the case of the base requests, you set the value of `BASE_FOIA_TEMPLATE`. (These are set to `federal_foia.docx` and `base_request.docx` by default.)

You should upload state-specific requests in the admin field in Django.

Second, any keywords in your FOIA request should be enclosed with two brackets, like `{{recipient_name}}`. You can use any amount of whitespace you want in between the brackets and the keyword. Those keywords can go anywhere you'd like, but you must limit yourself to the following keywords:

- `requested_records`: This is the field you use to specify the records you want to request. 
**Note: This is the only *mandatory* item in your template. If you do not include it, you will not be able to upload your template file.**
- `recipient_name`: The name of the FOIA Officer you're addressing the request to. If the underlying data is blank, it will automatically fill to "Public Records Officer," so you don't have to worry about not knowing the name of the public records officer.
- `public records act`: If you want to put the name of the state's public records act into the body of your request, you can do so with this keyword. This is mainly intended for base request forms and for filling out the subject line of your request.
- `expedited_processing`: This is where you offer your justification for why an agency should speed up how quickly it processes your request. This is mainly intended for federal FOIA requests, where provisions allowing for FOIA to expedite processing on some requests (rather than operating purely on a first in, first out basis) [is written into the law](https://foia.wiki/wiki/Expedited_Processing).
- `fee_waiver`: If you are asking to be exempt from charges under the public records act, use this keyword. In some places, like the federal Freedom of Information Act and the Connecticut Freedom of Information Act, there are specific provisions offering limited waivers from some fees.
- `max_response_time`: This is intended to allow you to write things like "I look forward to hearing from you within x business days." It's mainly intended for the base class. (If the state doesn't have a maximum response requirement, this skips the "within x business days" part entirely.)
- `agency_name`, `agency_street_address`, `agency_municipality`, `state`, `zip_code`: All of these are intended for you to be able to add an address into your form letter.
- `subject_line`, `foia_email`: These are mainly intended to help fill out the template and send the email. However, there may be some cases in which you'd want to use them.

## Future Roadmap

As it stands, this is far from a complete project. It's really a first stab at a tool that I plan on using for a long time
to keep track of sources, file FOIA requests, and integrate all of my contacts (including FOIA requests) to projects I'm working
on.

I have a bunch of features that I plan on adding in the future. Because of this, you should refrain from any attempts
to use portions of this tool as a library, since future releases may break the functionality of your tool. If you absolutely need to use portions of this tool as a library, make sure to link the specific tag number on installation. 

All releases will follow standard protocol, using the format `v{major_version}.{minor_version}.{revision}`. Any feature additions or model changes will result in an increase in the minor version, and any minor code revisions or bug or security fixes will result in an increase in the revision number. If this tool ever becomes stable (i.e. reaches major version 1), breaking changes (other than security fixes) will result in a change of major version. As long as the major version is 0 (unstable), expect breaking changes on a change of minor versions.

I encourage people to play around with this, fork the project, file pull requests, etc. If you want to help but don't know where to start, I have these specific tasks/features I want to add:

- Scheduling: I'm hoping to add functionality to allow people to schedule requests. This can be useful for files like FOIA logs or directories that are periodically released. If you're dealing with [an obstinate agency that refuses to provide bulk records](https://twitter.com/twallack/status/1025346534471348225) that decides not to provide you with bulk data, it can also be useful for slowly building up a database. (I plan on using `apscheduler` and `django-apscheduler` for this.)
- Admin forms: Right now, I'm dealing with all of the forms except for request filing from within the django admin. Eventually, I want to customize those views a bit or create my own forms outside of the admin to make portions of this program easier to use and administer.
- More views: I'm hoping to add some more views to allow users to better see their contacts, link those contacts to sources and FOIA requests, etc.
- Search and autofill: I want to add some searching functionality so that people can better filter their results and find what they're looking for. (I plan on using `autocomplete-light` and either PostGreSQL full search or ElasticSearch for this.)
- Testing: Right now, I'm really light on testing, because I wanted to get this program up to a somewhat functional state quickly. I would like to change this. I'll be using `pytest-cov` for testing and coverage tests, `nox` for testing against different environments, and `hypothesis` for running property-based tests. (This comes in handy for checking custom form validation and custom serialization/deserialization.)
- Documentation: I have tried to make this README usable. But eventually, I'd like to add a more thorough user guide. In particular, I think it would be cool to have a video or two demonstrating how to use this tool.