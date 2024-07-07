# Generated by Django 4.2 on 2023-04-12 08:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('globals', '0002_alter_page_url')]

    operations = [
        migrations.AlterModelOptions(
            name='page',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='page',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Order'),
        ),
        migrations.AlterField(
            model_name='page',
            name='hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden link'),
        ),
        migrations.AlterField(
            model_name='page',
            name='parent_page',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.page', verbose_name='Parent link'),
        ),
        migrations.AlterField(
            model_name='page',
            name='title',
            field=models.CharField(max_length=100, verbose_name='Title'),
        ),
        migrations.RenameModel(
            old_name='Page',
            new_name='Link',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='parent_page',
            new_name='parent_link',
        ),
    ]