# Generated by Django 5.0.7 on 2024-09-11 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot1', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('visibility', models.CharField(choices=[('global', 'Global'), ('private', 'Private')], default='private', max_length=10)),
                ('model', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
