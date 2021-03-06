# Generated by Django 3.0.1 on 2020-01-01 08:31

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields
import re
import taggit.managers
import utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="The time of the contact",
                    ),
                ),
                (
                    "contact_method",
                    models.CharField(
                        choices=[
                            ("e", "e-mail"),
                            ("p", "phone call"),
                            ("t", "text"),
                            ("i", "in-person"),
                            ("l", "letter"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "answered",
                    models.BooleanField(
                        help_text="Has this person answered your attempt to reach them?"
                    ),
                ),
                ("short_description", models.CharField(max_length=500)),
                (
                    "addl_notes",
                    models.CharField(
                        blank=True, max_length=400, verbose_name="additional notes"
                    ),
                ),
                (
                    "ground_rules",
                    models.CharField(
                        choices=[
                            ("otr", "on-the-record"),
                            ("bg", "on background"),
                            ("db", "deep background"),
                            ("or", "off-the-record"),
                        ],
                        default="otr",
                        max_length=3,
                    ),
                ),
                (
                    "audio_file",
                    models.FileField(blank=True, null=True, upload_to="audio_files/"),
                ),
                (
                    "transcript",
                    models.FileField(
                        blank=True, null=True, upload_to="audio_transcript/"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Entity",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("street_address", models.CharField(max_length=200)),
                ("municipality", models.CharField(blank=True, max_length=100)),
                ("locality", models.CharField(blank=True, max_length=100)),
                (
                    "zip_code",
                    models.CharField(
                        max_length=9,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="The ZIP code does not match a NNNNN or NNNNN-NNNN format",
                                regex="^[0-9]{5}(\\-[0-9]{4})?$",
                            )
                        ],
                    ),
                ),
                (
                    "foia_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                ("is_federal", models.BooleanField()),
            ],
            options={"verbose_name_plural": "entities",},
        ),
        migrations.CreateModel(
            name="Project",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "short_description",
                    models.CharField(
                        help_text="Enter a 6-word description of the piece",
                        max_length=100,
                    ),
                ),
                (
                    "long_description",
                    models.CharField(
                        help_text="Provide a more detailed description of the project",
                        max_length=3000,
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("link", models.URLField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name="Source",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=100)),
                ("last_name", models.CharField(blank=True, max_length=100)),
                ("title", models.CharField(max_length=200)),
                (
                    "work_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                (
                    "home_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                (
                    "cell_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, null=True, region=None
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("address", models.CharField(blank=True, max_length=400)),
                (
                    "twitter",
                    models.CharField(
                        blank=True,
                        max_length=16,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Twitter handles must start with @ and contain between 1 and 15 alphanumeric characters",
                                regex=re.compile("^@[_A-Za-z0-9]{1,15}$"),
                            )
                        ],
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("m", "Man"),
                            ("w", "Woman"),
                            ("n", "Nonconforming"),
                            ("i", "Inapplicable"),
                            ("u", "Unknown"),
                        ],
                        max_length=1,
                    ),
                ),
                (
                    "race",
                    models.CharField(
                        choices=[
                            ("poc", "Person of color"),
                            ("w", "White"),
                            ("unk", "Unknown"),
                        ],
                        max_length=3,
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[
                            ("db", "Database administrator"),
                            ("rp", "Person affected (anecdotal source)"),
                            ("e", "Expert"),
                            ("pr", "Spokesperson, PR-Rep"),
                            ("f", "Public Records officer"),
                            ("o", "Public/Company official"),
                            (
                                "i",
                                "Insider (employee, often speaking on-background, etc.)",
                            ),
                        ],
                        max_length=2,
                    ),
                ),
                (
                    "notes",
                    models.CharField(
                        blank=True,
                        help_text="Random notes about this person.",
                        max_length=1000,
                    ),
                ),
                ("time_added", models.DateTimeField(auto_now_add=True)),
                ("last_modified", models.DateTimeField(auto_now=True)),
                (
                    "entity",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Entity",
                    ),
                ),
            ],
            options={"ordering": ["last_name", "first_name"],},
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "fips_code",
                    models.CharField(
                        max_length=2, validators=[utils.validators.validate_fips]
                    ),
                ),
                (
                    "foia_template",
                    models.FileField(
                        upload_to="foia_templates/",
                        validators=[utils.validators.validate_template_extension],
                        verbose_name="Public Records act template",
                    ),
                ),
                (
                    "maximum_response_time",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        help_text="What is the maximum response time allowed under this state's public records act?",
                        null=True,
                    ),
                ),
                (
                    "business_days",
                    models.BooleanField(
                        blank=True,
                        help_text="Is the response time the number of business days or actual days to respond to requests?",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Story",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("headline", models.CharField(max_length=100)),
                ("link", models.URLField(max_length=300)),
                (
                    "story_type",
                    models.CharField(
                        choices=[
                            ("i", "investigative"),
                            ("x", "explanatory"),
                            ("b", "breaking news"),
                            ("d", "data-driven piece"),
                            ("e", "entertainment"),
                        ],
                        max_length=1,
                    ),
                ),
                ("interviews", models.ManyToManyField(to="sourcebook.Contact")),
                (
                    "project",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Project",
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Publication",
                    ),
                ),
                ("sources", models.ManyToManyField(to="sourcebook.Source")),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProjectTask",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("short_description", models.CharField(max_length=150)),
                ("description", models.CharField(max_length=500)),
                ("completed", models.BooleanField(default=False)),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Project",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FoiaRequest",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_filed", models.DateTimeField(default=datetime.date.today)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("nr", "no response"),
                            ("a", "acknowledged"),
                            ("cf", "closed - no redactions"),
                            ("cr", "closed - some redactions"),
                            ("ce", "closed - did not pay fee"),
                            ("ap", "appealed"),
                            ("s", "sued"),
                        ],
                        default="nr",
                        max_length=2,
                    ),
                ),
                ("requested_records", models.CharField(max_length=2000)),
                (
                    "expedited_processing",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        verbose_name="justification for expedited processing",
                    ),
                ),
                (
                    "fee_waiver",
                    models.CharField(
                        blank=True,
                        max_length=1000,
                        verbose_name="Fee waiver justification",
                    ),
                ),
                (
                    "fee_assessed",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=9, null=True
                    ),
                ),
                (
                    "modified_request",
                    models.BooleanField(
                        default=False,
                        help_text="Have you modified (narrowed or broadened) your initial request?",
                    ),
                ),
                (
                    "agency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Entity",
                    ),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.Source",
                    ),
                ),
                (
                    "requested_formats",
                    taggit.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="entity",
            name="state",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="sourcebook.State",
            ),
        ),
        migrations.CreateModel(
            name="Document",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("short_description", models.CharField(max_length=400)),
                (
                    "addl_notes",
                    models.CharField(
                        blank=True, max_length=1000, verbose_name="additional notes"
                    ),
                ),
                (
                    "doc_file",
                    models.FileField(upload_to="documents/", verbose_name="file"),
                ),
                (
                    "foia_request",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sourcebook.FoiaRequest",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="contact",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="sourcebook.Source"
            ),
        ),
    ]
