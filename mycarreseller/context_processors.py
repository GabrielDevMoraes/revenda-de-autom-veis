# mycarreseller/context_processors.py

from django.conf import settings

def global_contact_info(request):
    """
    Adiciona as informações de contato globais do settings.py ao contexto de todos os templates.
    """
    return {
        'GLOBAL_CONTACT_INFO': settings.GLOBAL_CONTACT_INFO
    }

