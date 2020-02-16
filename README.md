# A Django Toolkit for Journalism

This is a tool I've started to create in order to organize my work as a journalist and in order to file public records requests.

This is still a work in progress, but right now it's capable of allowing you to keep track of and search for sources and to file bulk public records requests. Because of the scope of the project, there's a lot that I hope to add, from more extensive search functionality to the ability to run scheduled requests (for instance, for salary data or FOIA logs). Those additional features are documented in the [future roadmap](#future-roadmap) section of this README.

## Table of Contents
- [Setup and installation](#setup-and-installation)
- [FOIA](#foia)
    - [Templates](#templates)
- [Future Roadmap](#future-roadmap)
- [Credits](#credits)

## Setup and Installation

This project requires PostgreSQL to run, primarily because it uses full-text search from PostgreSQL. In addition, you need Python version 3.6+, because this uses f-strings.

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

State-level public records laws are similar enough to one another that you can largely use the same template to file requests across state lines. However, because states have different public records provisions (for instance, some have fee waivers written into statute, while others don't; some have residency requirements, while others don't), it can be beneficial to have different templates for different states.

The templating system I've decided to use offers a compromise. The program will look for state-level templates if you've uploaded them (they're part of the States model in Django admin), but will use a base template as a fallback if it can't find a relevant template.

#### Formatting

Like most templating systems, this one is fairly picky about how you do things. However, if you've used Django or Jinja2, its preferences should feel familiar.

First of all, your federal FOIA template should go into the `FEDERAL_FOIA_TEMPLATE` location within your `MEDIA_ROOT/foia_templates` in `settings`. The same principal goes with a base request you use to file FOIA requests in places where you don't have a blanket form. But in the case of the base requests, you set the value of `BASE_FOIA_TEMPLATE`. (These are set to `federal_foia.docx` and `base_request.docx` by default.)

You should upload state-specific requests in the admin field in Django.

Second, any keywords in your FOIA request should be enclosed with two brackets, like `{{recipient_name}}`. You can use any amount of whitespace you want in between the brackets and the keyword. Those keywords can go anywhere you'd like, but you must limit yourself to the following keywords:

- `requested_records`: This is the field you use to specify the records you want to request. 
**Note: This is the only *mandatory* item in your template. If you do not include it, you will not be able to upload your template file.**
- `recipient_name`: The name of the FOIA Officer you're addressing the request to. If the underlying data is blank, it will automatically fill to "Public Records Officer," so you don't have to worry about not knowing the name of the public records officer.
- `public_records_act`: If you want to put the name of the state's public records act into the body of your request, you can do so with this keyword. This is mainly intended for base request forms and for filling out the subject line of your request.
- `expedited_processing`: This is where you offer your justification for why an agency should speed up how quickly it processes your request. This is mainly intended for federal FOIA requests, where provisions allowing for FOIA to expedite processing on some requests (rather than operating purely on a first in, first out basis) [is written into the law](https://foia.wiki/wiki/Expedited_Processing).
- `fee_waiver`: If you are asking to be exempt from charges under the public records act, use this keyword. In some places, like the federal Freedom of Information Act and the Connecticut Freedom of Information Act, there are specific provisions offering limited waivers from some fees.
- `max_response_time`: This is intended to allow you to write things like "I look forward to hearing from you within x business days." It's mainly intended for the base class. (If the state doesn't have a maximum response requirement, this skips the "within x business days" part entirely.)
- `agency_name`, `agency_street_address`, `agency_municipality`, `state`, `zip_code`: All of these are intended for you to be able to add an address into your form letter.
- `subject_line`, `foia_email`: These are mainly intended to help fill out the template and send the email. However, there may be some cases in which you'd want to use them.

## Future Roadmap

As it stands, this is not a complete project. Instead, it's a usable start for a project I intend to use for some time to keep track of my sources, file public records requests, and integrate my contacts (including public records requests) to projects I'm working on.

I encourage people to play around with this, fork the project, file pull requests, etc. If you want to help but don't know where to start, I have these specific tasks/features I want to add:

- Scheduling: I'm hoping to add functionality to allow people to schedule requests. This can be useful for files like FOIA logs or directories that are periodically released. If you're dealing with [an obstinate agency that refuses to provide bulk records](https://twitter.com/twallack/status/1025346534471348225) that decides not to provide you with bulk data, it can also be useful for slowly building up a database. (I plan on using `apscheduler` and `django-apscheduler` for this.)
    - I also intend to use this scheduling in order to keep track of responses to requests I've filed.
- Admin forms: Right now, I'm dealing with all of the forms except for request filing from within the django admin. Eventually, I want to customize those views a bit or create my own forms outside of the admin to make portions of this program easier to use and administer.
- More views: I'm hoping to add some more views to allow users to better see their contacts, link those contacts to sources and FOIA requests, etc.
- Search and autofill: I want to add more searching functionality in order to make it easier to keep track of requests, sources, etc. (I plan on using `autocomplete-light` and either PostGreSQL full search or ElasticSearch for this.)
- Testing: Right now, I'm really light on testing, because I wanted to get this program up to a somewhat functional state quickly. That is, I've manually tested the tool on some common-use cases, but I haven't added any programmatic tests and I haven't tested on any edge cases or corner cases. I would like to change this. I'll be using `pytest-cov` for testing and coverage tests, `nox` for testing against different environments, and `hypothesis` for running property-based tests. (This comes in handy for checking custom form validation and custom serialization/deserialization.)
- Documentation and easy installation: As you can see from this README, you really need some programming experience in order to get set up with this tool. Eventually, I'd like that to change.In particular, I think it would be cool to have a video or two demonstrating how to use and get set up with this tool.
- Authentication: Right now, everything in this data is public, without any user authentication. My initial thought with this project was to largely ignore user authentication with the idea that everything should be done locally. But I think there's a lot of potential to convert some of the FOIA work in particular in a collaborative way. So possibly have user auth --> if person.is_authenticated => can see all FOIA requests related to collaborative projects & all of their own sourcing.
- Agency groups: Right now, in order to bulk file requests, you need to manually set all of the agencies you want to send a request to. I'd like to allow you to create groups so you can send a request to every agency in a group. (For instance, you might have a 'State Police' group that files a public records request to every state police agency.)

## Credits

In order to create this tool, I relied on a number of useful guides and libraries. In particular:

-  I used parts of [`foiamail`](https://github.com/bettergov/foiamail) to deal with g-mail authentication and in order to send requests. I was also heavily inspired by the design of `foiamail`, even if those design choices don't directly appear in the code I wrote.
- I used [@loganchien's Django Full-text search demo](http://logan.tw/posts/2017/12/30/full-text-search-with-django-and-postgresql/) to implement the indexing for the full-text search.
- I used [Simon Willison's guide for implementing full-text search in Django](https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/) in order to set up full-text search (outside of the indexing, as described above).