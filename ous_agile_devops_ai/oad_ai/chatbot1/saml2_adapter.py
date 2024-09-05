# saml2_adapter.py

from django.contrib.auth import get_user_model
from djangosaml2.backends import Saml2Backend

User = get_user_model()

class CustomSAML2Backend(Saml2Backend):
    def authenticate(self, request, session_info=None, attribute_mapping=None, create_unknown_user=True, **kwargs):
        user = super().authenticate(request, session_info, attribute_mapping, create_unknown_user, **kwargs)
        if user:
            # You can add custom logic here, such as updating user attributes
            user.save()
        return user