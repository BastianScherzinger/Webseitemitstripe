from django.db import migrations, models


def rename_seite_to_site(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cur:
        cur.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='shop1_visitorlog' AND column_name='seite'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='shop1_visitorlog' AND column_name='site'
                ) THEN
                    ALTER TABLE shop1_visitorlog RENAME COLUMN seite TO site;
                END IF;
            END$$;
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('shop1', '0015_pystorevisitorlog'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(rename_seite_to_site, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='visitorlog',
                    name='seite',
                    field=models.CharField(
                        blank=True, default='pystore', max_length=100, db_column='site'
                    ),
                ),
            ],
        ),
    ]
