from django.db import migrations, models
import django.db.models.deletion


def create_tables(apps, schema_editor):
    """Create werbung tables safely — IF NOT EXISTS handles pre-existing tables."""
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shop1_werbung (
                id BIGSERIAL PRIMARY KEY,
                titel VARCHAR(200) NOT NULL,
                beschreibung TEXT NOT NULL DEFAULT '',
                link VARCHAR(500) NOT NULL,
                bild VARCHAR(500) NOT NULL DEFAULT '',
                budget NUMERIC(10,2) NOT NULL DEFAULT 0,
                laufzeit_tage INTEGER NOT NULL DEFAULT 30,
                ablauf_email_gesendet BOOLEAN NOT NULL DEFAULT FALSE,
                aktiv BOOLEAN NOT NULL DEFAULT TRUE,
                impressionen INTEGER NOT NULL DEFAULT 0,
                klicks INTEGER NOT NULL DEFAULT 0,
                erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shop1_werbungstat (
                id BIGSERIAL PRIMARY KEY,
                werbung_id BIGINT NOT NULL
                    REFERENCES shop1_werbung(id) ON DELETE CASCADE,
                seite VARCHAR(100) NOT NULL,
                impressionen INTEGER NOT NULL DEFAULT 0,
                klicks INTEGER NOT NULL DEFAULT 0,
                datum DATE NOT NULL,
                CONSTRAINT shop1_werbungstat_werbung_seite_datum_uniq
                    UNIQUE (werbung_id, seite, datum)
            )
        """)
        print('shop1_werbung and shop1_werbungstat ensured.')


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0012_comment'),
    ]

    operations = [
        migrations.RunPython(create_tables, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Werbung',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('titel', models.CharField(max_length=200)),
                        ('beschreibung', models.TextField(blank=True, default='')),
                        ('link', models.URLField(max_length=500)),
                        ('bild', models.CharField(blank=True, default='', max_length=500)),
                        ('budget', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                        ('laufzeit_tage', models.PositiveIntegerField(default=30)),
                        ('ablauf_email_gesendet', models.BooleanField(default=False)),
                        ('aktiv', models.BooleanField(default=True)),
                        ('impressionen', models.PositiveIntegerField(default=0)),
                        ('klicks', models.PositiveIntegerField(default=0)),
                        ('erstellt_am', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={
                        'verbose_name': 'Werbung',
                        'verbose_name_plural': 'Werbungen',
                        'ordering': ['-erstellt_am'],
                    },
                ),
                migrations.CreateModel(
                    name='WerbungStat',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('seite', models.CharField(max_length=100)),
                        ('impressionen', models.PositiveIntegerField(default=0)),
                        ('klicks', models.PositiveIntegerField(default=0)),
                        ('datum', models.DateField()),
                        ('werbung', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='shop1.werbung')),
                    ],
                    options={
                        'verbose_name': 'Werbung Statistik',
                        'verbose_name_plural': 'Werbung Statistiken',
                        'unique_together': {('werbung', 'seite', 'datum')},
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
