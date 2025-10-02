from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.nombre = data.get("given_name", "") or data.get("first_name", "")
        user.apellido = data.get("family_name", "") or data.get("last_name", "")
        return user
