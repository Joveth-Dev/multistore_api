# Generated by Django 5.1.5 on 2025-02-23 07:25

import store.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_address_options_address_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='image',
            field=models.ImageField(default='store/images/default.jpg', upload_to='store/images', validators=[store.validators.validate_file_size]),
        ),
    ]
