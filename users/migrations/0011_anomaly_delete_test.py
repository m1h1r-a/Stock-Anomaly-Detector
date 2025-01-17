# Generated by Django 5.1.1 on 2024-11-12 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_rename_buy_threshold_portfolio_threshold_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anomaly',
            fields=[
                ('AnomalyID', models.AutoField(primary_key=True, serialize=False)),
                ('StockSymbol', models.CharField(max_length=10)),
                ('AnomalyType', models.CharField(max_length=10)),
                ('AnomalyDate', models.DateField()),
                ('AlertTimestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Anomaly',
            },
        ),
        migrations.DeleteModel(
            name='test',
        ),
    ]
