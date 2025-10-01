from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class RapsodiaSocialAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        extra_data = sociallogin.account.extra_data

        user.email = extra_data.get('email', '')
        user.nombre = extra_data.get('given_name', '') or extra_data.get('name', '').split()[0]
        user.apellido = extra_data.get('family_name', '') or extra_data.get('name', '').split()[-1]

        user.save()
        sociallogin.save(request)

        return user