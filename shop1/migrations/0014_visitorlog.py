from django.db import migrations, models


def create_visitorlog(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS shop1_visitorlog (
                id BIGSERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                ip_address INET,
                country VARCHAR(100) NOT NULL DEFAULT '',
                country_code VARCHAR(5) NOT NULL DEFAULT '',
                city VARCHAR(100) NOT NULL DEFAULT '',
                path VARCHAR(255) NOT NULL DEFAULT '',
                user_agent VARCHAR(500) NOT NULL DEFAULT '',
                seite VARCHAR(100) NOT NULL DEFAULT 'pystore'
            )
        """)
        print('shop1_visitorlog ensured.')


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0013_werbung_werbungstat'),
    ]

    operations = [
        migrations.RunPython(create_visitorlog, migrations.RunPython.noop),
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='VisitorLog',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('timestamp', models.DateTimeField(auto_now_add=True)),
                        ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                        ('country', models.CharField(blank=True, default='', max_length=100)),
                        ('country_code', models.CharField(blank=True, default='', max_length=5)),
                        ('city', models.CharField(blank=True, default='', max_length=100)),
                        ('path', models.CharField(blank=True, default='', max_length=255)),
                        ('user_agent', models.CharField(blank=True, default='', max_length=500)),
                        ('seite', models.CharField(blank=True, default='pystore', max_length=100)),
                    ],
                    options={
                        'verbose_name': 'Besucher Log',
                        'verbose_name_plural': 'Besucher Logs',
                        'ordering': ['-timestamp'],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
