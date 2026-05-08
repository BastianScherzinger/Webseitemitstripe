import os
from django.conf import settings

def shop_owner_check(request):
    """
    Ein Context-Processor, der prüft, ob der aktuelle Benutzer der Shopbesitzer ist.
    Gibt 'is_shop_owner' an alle Templates weiter.
    """
    is_shop_owner = False
    if request.user.is_authenticated:
        admin_username = os.getenv('ADMIN_USERNAME', 'shopbesitzer')
        if request.user.username == admin_username:
            is_shop_owner = True
        elif request.user.is_superuser:
            # Optional: Auch Superuser als Shopbesitzer zählen
            is_shop_owner = True
            
    return {
        'is_shop_owner': is_shop_owner
    }
