# Generated by Django 4.2.6 on 2023-10-19 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("globals", "0007_alter_specialcontent_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="link",
            name="parent_link",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="globals.link",
                verbose_name="parent link",
            ),
        ),
    ]
