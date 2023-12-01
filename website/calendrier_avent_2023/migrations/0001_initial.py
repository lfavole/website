# Generated by Django 4.2.7 on 2023-11-27 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("blog", "0003_rename_image_image_file_alter_image_content_type_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Day",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day", models.IntegerField(unique=True, verbose_name="day")),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="blog.image", verbose_name="image"
                    ),
                ),
            ],
            options={
                "verbose_name": "Day",
            },
        ),
    ]