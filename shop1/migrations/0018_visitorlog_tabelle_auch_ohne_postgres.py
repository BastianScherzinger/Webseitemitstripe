from django.db import migrations

#: Modelle, deren Tabellen die Migrationen 0013 und 0014 nur auf PostgreSQL
#: anlegen. Reihenfolge beachten: WerbungStat hat einen Fremdschluessel auf
#: Werbung.
_NACHZUZIEHEN = [
    ('Werbung', 'shop1_werbung'),
    ('WerbungStat', 'shop1_werbungstat'),
    ('VisitorLog', 'shop1_visitorlog'),
]


def tabellen_nachziehen(apps, schema_editor):
    """Legt fehlende Tabellen an, die 0013/0014 nur auf PostgreSQL erzeugen.

    Beide Migrationen beginnen mit
    ``if schema_editor.connection.vendor != 'postgresql': return`` und trennen
    den Modellzustand per ``SeparateDatabaseAndState`` von der Datenbank ab.
    Auf SQLite – also in der lokalen Entwicklung und im Testlauf – entstehen
    die Tabellen deshalb nie. Folge: ``PageVisitMiddleware`` verliert dort
    jeden ``VisitorLog``-Eintrag (der Fehler wird nur protokolliert) und jede
    Seite des Werbebereichs im Admin-Panel bricht mit ``no such table`` ab.

    Im Betrieb laeuft PostgreSQL und die Tabellen stehen bereits; dort findet
    die Funktion alle drei vor und aendert nichts.
    """
    vorhanden = set(schema_editor.connection.introspection.table_names())
    for modellname, tabelle in _NACHZUZIEHEN:
        if tabelle not in vorhanden:
            schema_editor.create_model(apps.get_model('shop1', modellname))


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0017_produkt_slug_seo'),
    ]

    operations = [
        migrations.RunPython(tabellen_nachziehen, migrations.RunPython.noop),
    ]
