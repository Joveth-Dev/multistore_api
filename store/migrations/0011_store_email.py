# Generated by Django 5.1.5 on 2025-02-24 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_alter_category_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='email',
            field=models.EmailField(default='samplemail@domain.com', max_length=254, unique=True),
            preserve_default=False,
        ),
    ]
