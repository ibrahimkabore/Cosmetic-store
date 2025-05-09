# Generated by Django 5.1.6 on 2025-02-20 12:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("e_commerce", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="payment_method",
            field=models.CharField(
                choices=[
                    ("CB", "Carte Bancaire"),
                    ("MM", "Mobile Money"),
                    ("CS", "Cash"),
                ],
                default="CB",
                max_length=2,
                verbose_name="Payment Method",
            ),
        ),
        migrations.CreateModel(
            name="OrderLine",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=0, max_digits=10)),
                ("line_total", models.DecimalField(decimal_places=0, max_digits=10)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lines",
                        to="e_commerce.order",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="e_commerce.product",
                    ),
                ),
            ],
        ),
    ]
