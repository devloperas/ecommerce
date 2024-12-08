# Generated by Django 5.1.3 on 2024-11-26 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_user_deleted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_token_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]