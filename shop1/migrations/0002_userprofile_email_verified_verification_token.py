import uuid
from django.db import migrations, models


def generate_unique_tokens(apps, schema_editor):
    """Generiert einzigartige Tokens für alle existierenden UserProfiles."""
    UserProfile = apps.get_model('shop1', 'UserProfile')
    for profile in UserProfile.objects.all():
        profile.verification_token = uuid.uuid4()
        profile.save(update_fields=['verification_token'])


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0001_initial'),
    ]

    operations = [
        # Schritt 1: email_verified hinzufügen
        migrations.AddField(
            model_name='userprofile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
        # Schritt 2: verification_token hinzufügen OHNE unique constraint
        migrations.AddField(
            model_name='userprofile',
            name='verification_token',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        # Schritt 3: Einzigartige Tokens für existierende Zeilen generieren
        migrations.RunPython(generate_unique_tokens, migrations.RunPython.noop),
        # Schritt 4: unique constraint setzen und null=True entfernen
        migrations.AlterField(
            model_name='userprofile',
            name='verification_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
