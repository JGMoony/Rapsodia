from django.core.mail import send_mail

def enviar_correo(destinatario, asunto, cuerpo):
    send_mail(
        subject=asunto,
        message=cuerpo,
        from_email=None,
        recipient_list=[destinatario],
        fail_silently=False,
    )
