from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="currency",
            field=models.CharField(choices=[("USD", "USD"), ("EUR", "EUR")], default="USD", max_length=3),
        ),
    ]
