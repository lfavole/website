# Generated by Django 4.2.3 on 2023-10-18 13:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0006_specialcontent"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="specialcontent",
            options={"verbose_name": "special content", "verbose_name_plural": "special contents"},
        ),
    ]
