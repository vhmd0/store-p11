# Generated manually for new Profile fields

import django.db.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_alter_address_options_address_addr_user_def_idx_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True, verbose_name="Date of birth"),
        ),
        migrations.AddField(
            model_name="profile",
            name="gender",
            field=models.CharField(
                blank=True,
                choices=[
                    ("male", "Male"),
                    ("female", "Female"),
                    ("unspecified", "Prefer not to say"),
                ],
                default="unspecified",
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="email_marketing",
            field=models.BooleanField(default=False, verbose_name="Email promotions"),
        ),
        migrations.AddField(
            model_name="profile",
            name="push_notifications",
            field=models.BooleanField(default=True, verbose_name="Push notifications"),
        ),
    ]
