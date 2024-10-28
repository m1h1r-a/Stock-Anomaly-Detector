# Generated by Django 5.1.1 on 2024-10-28 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocktransaction',
            name='user',
        ),
        migrations.AddField(
            model_name='portfolio',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stocktransaction',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
    ]
