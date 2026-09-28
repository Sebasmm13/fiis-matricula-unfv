from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0004_accountsecurity")]
    operations = [
        migrations.AddField(
            model_name="course",
            name="academic_data_verified",
            field=models.BooleanField(default=False),
        )
    ]
