from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("core", "0003_teacher_user_profilephoto")]

    operations = [
        migrations.CreateModel(
            name="AccountSecurity",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("must_change_password", models.BooleanField(default=False)),
                ("activation_pending", models.BooleanField(default=False)),
                ("password_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="security",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        )
    ]
