from django.db import migrations, models


class Migration(migrations.Migration):
    """Einstufung der Kontaktnachrichten (24.11.2026): Anfrage, Dienstleistungs-Angebot oder Spamverdacht.

    Bestehende Zeilen bleiben ``anfrage`` (so wurden sie bisher behandelt)."""

    dependencies = [
        ('shop1', '0039_stueckanfrage'),
    ]

    operations = [
        migrations.AddField(
            model_name='kontaktanfrage',
            name='einstufung',
            field=models.CharField(choices=[('anfrage', 'Anfrage'), ('angebot', 'Dienstleistungs-Angebot'), ('spam', 'Spamverdacht')], db_index=True, default='anfrage', max_length=10, verbose_name='Einstufung'),
        ),
        migrations.AddField(
            model_name='kontaktanfrage',
            name='einstufung_gruende',
            field=models.CharField(blank=True, max_length=200, verbose_name='Gründe der Einstufung'),
        ),
        migrations.AddField(
            model_name='kontaktanfrage',
            name='absage_am',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Absage verschickt am'),
        ),
        migrations.AddField(
            model_name='kontaktanfrage',
            name='absage_sprache',
            field=models.CharField(blank=True, max_length=5, verbose_name='Sprache der Absage'),
        ),
    ]
