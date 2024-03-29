# Generated by Django 4.0.6 on 2023-01-26 17:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Titre')),
                ('url', models.CharField(max_length=100, verbose_name='URL')),
                ('hidden', models.BooleanField(default=False, verbose_name='Page cachée')),
                ('parent_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.page', verbose_name='Page précédente')),
            ],
        ),
    ]
