from django.utils import timezone
from django.db.models import F
from .models import PageVisit

class PageVisitMiddleware:
    """
    Middleware zur Zählung von Seitenbesuchen pro Tag.
    Nutzt die Session, um mehrfache Seitenaufrufe durch denselben 
    Nutzer an einem Tag nicht mehrfach zu zählen.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Nur aufrufen, wenn es kein static/media/admin request ist
        if not request.path.startswith('/static/') and \
           not request.path.startswith('/media/') and \
           not request.path.startswith('/admin/'):
            
            today = timezone.localdate()
            today_str = today.isoformat()
            
            # Prüfen ob der Nutzer heute schon da war
            last_visit = request.session.get('last_visit_date')
            
            if last_visit != today_str:
                # Neuen Besuch für heute registrieren
                visit, created = PageVisit.objects.get_or_create(
                    date=today,
                    defaults={'visits': 1}
                )
                if not created:
                    # Direkter Datenbank-Update ohne Race Conditions
                    PageVisit.objects.filter(date=today).update(visits=F('visits') + 1)
                
                # Session-Variable setzen
                request.session['last_visit_date'] = today_str
                
        response = self.get_response(request)
        return response
