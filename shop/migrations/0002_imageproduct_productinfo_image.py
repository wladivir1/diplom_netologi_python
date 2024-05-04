# Generated by Django 5.0.4 on 2024-05-01 17:19

import django.db.models.deletion
import versatileimagefield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('image', versatileimagefield.fields.VersatileImageField(height_field='height', upload_to='images/products/', verbose_name='Image', width_field='width')),
                ('height', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image Height')),
                ('width', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image Width')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shop.product')),
            ],
            options={
                'verbose_name': 'Фото продукта',
                'verbose_name_plural': 'Фото продуктов',
            },
        ),
        migrations.AddField(
            model_name='productinfo',
            name='image',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product_infos', to='shop.imageproduct', verbose_name='Изображение'),
            preserve_default=False,
        ),
    ]