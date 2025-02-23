# Generated by Django 5.1.5 on 2025-02-23 15:47

import django.db.models.deletion
import store.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_store_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='image',
            field=models.ImageField(default='store/store/images/default.jpg', upload_to='store/store/images', validators=[store.validators.validate_file_size]),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('image', models.ImageField(default='store/product/default.jpg', upload_to='store/product/images', validators=[store.validators.validate_file_size])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
            options={
                'ordering': ['-updated_at', '-created_at'],
            },
        ),
    ]
