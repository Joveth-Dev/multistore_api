# Generated by Django 5.1.5 on 2025-03-03 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0019_alter_product_price'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='cartitem',
            constraint=models.UniqueConstraint(models.F('cart'), models.F('product'), name='unique_cart_product'),
        ),
    ]
