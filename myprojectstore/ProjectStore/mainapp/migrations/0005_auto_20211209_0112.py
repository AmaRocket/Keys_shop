# Generated by Django 3.2.9 on 2021-12-09 01:12

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_auto_20211208_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255, verbose_name='Name')),
                ('last_name', models.CharField(max_length=255, verbose_name='Last Name')),
                ('phone', models.CharField(max_length=20, verbose_name='Telephone')),
                ('address', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Address')),
                ('status', models.CharField(choices=[('new', 'NEW'), ('in_progress', 'IN PROGRESS'), ('is_ready', 'READY'), ('completed', 'COMPLETED')], default='new', max_length=100, verbose_name='Order Status')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Order Comment')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='Date Order Creating ')),
                ('order_date', models.DateField(default=django.utils.timezone.now, verbose_name='Date Order Receipt')),
                ('cart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.cart', verbose_name='Basket')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_orders', to='mainapp.customer', verbose_name='Customer')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='orders',
            field=models.ManyToManyField(related_name='related_order', to='mainapp.Order', verbose_name='Customer Orders'),
        ),
    ]
