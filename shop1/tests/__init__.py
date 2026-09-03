"""Testsuite der App shop1.

Aufgeteilt nach Prüfgegenstand:

* ``test_seiten``       – jede öffentliche Adresse antwortet, geschützte nicht
* ``test_seo``          – Sitemap, robots.txt, Titel, Beschreibungen, canonical
* ``test_formulare``    – Kontakt- und Newsletterformular inklusive Spamschutz
* ``test_daten``        – Modell-Invarianten (Slugs, Denormalisierung)
* ``test_einstellungen``– Sicherheitseinstellungen im Betriebsmodus

Ausgeführt mit ``python manage.py test shop1``. Ein zweites Testwerkzeug
gibt es bewusst nicht – der Django-Test-Runner ist im Projekt vorhanden.
"""
