from django.db import migrations, models


class Migration(migrations.Migration):
    """Fügt PyStoreVisitorLog als unmanaged Proxy-Modell hinzu.
    managed=False → kein CREATE TABLE, spiegelt nur den Zustand für Django.
    """

    dependencies = [
        ('shop1', '0014_visitorlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='PyStoreVisitorLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('country', models.CharField(blank=True, default='', max_length=100)),
                ('country_code', models.CharField(blank=True, default='', max_length=5)),
                ('city', models.CharField(blank=True, default='', max_length=100)),
                ('path', models.CharField(blank=True, default='', max_length=255)),
                ('user_agent', models.CharField(blank=True, default='', max_length=500)),
                ('seite', models.CharField(blank=True, default='luviq', max_length=100)),
            ],
            options={
                'managed': False,
                'db_table': 'shop1_visitorlog',
            },
        ),
    ]
