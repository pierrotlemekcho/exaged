# Generated by Django 3.2.7 on 2021-10-13 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0005_auto_20210907_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='lignedecommande',
            name='gamme_status',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='gamme',
            name='exact_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gamme', to='planning.article', to_field='exact_id'),
        ),
        migrations.AlterField(
            model_name='lignedecommande',
            name='exact_order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='planning.commande', to_field='exact_order_id'),
        ),
    ]
