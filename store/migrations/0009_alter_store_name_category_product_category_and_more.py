# Generated by Django 5.1.5 on 2025-02-23 16:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_alter_store_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.store')),
            ],
            options={
                'ordering': ['-updated_at', '-created_at'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='store.category'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(fields=('store', 'name'), name='unique_store_name'),
        ),
    ]
