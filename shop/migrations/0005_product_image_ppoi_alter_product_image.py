# Generated by Django 5.0.4 on 2024-05-01 21:36

import versatileimagefield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_product_image_delete_imageproduct'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_ppoi',
            field=versatileimagefield.fields.PPOIField(default='0.5x0.5', editable=False, max_length=20),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='product_images/', verbose_name='Изображение'),
        ),
    ]
