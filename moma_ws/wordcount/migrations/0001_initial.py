# Generated by Django 2.2.5 on 2022-04-07 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WordReference',
            fields=[
                ('word', models.CharField(max_length=31, primary_key=True, serialize=False)),
                ('count', models.IntegerField()),
                ('lastreset', models.DateTimeField()),
            ],
        ),
    ]