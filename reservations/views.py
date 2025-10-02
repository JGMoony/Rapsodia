from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count
from django.utils.timezone import now
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
# Importaciones necesarias para el envío de correo
from django.core.mail import EmailMessage 
from django.template.loader import render_to_string
# Fin de importaciones de correo
from .forms import EditarReservaForm, ReservaForm, DisponibilidadForm
from users.forms import ProfileForm 
from .models import Mesa, Reserva
from users.models import User
import json
from calendar import month_name


@login_required
def disponibilidad_y_reserva(request):
    form = DisponibilidadForm(request.POST or None)
    mesas_disponibles = None
    mesas_ocupadas = None
    todas_mesas = Mesa.objects.all().order_by('numero')
    fecha = hora = personas = None
    ids_mesas_disponibles = []

    if request.method == "POST":
        if request.POST.get("consultar") == "1" and form.is_valid():
            fecha_obj = form.cleaned_data["fecha"]
            hora_obj = form.cleaned_data["hora"]
            personas = form.cleaned_data["personas"]

            dt_consulta = datetime.combine(fecha_obj, hora_obj)
            reservas_activas = Reserva.objects.filter(fecha=fecha_obj, estado="activa")

            mesas_ocupadas_ids = []
            for reserva in reservas_activas:
                dt_inicio = datetime.combine(reserva.fecha, reserva.hora)
                dt_fin = dt_inicio + timedelta(hours=3)
                if dt_inicio <= dt_consulta < dt_fin:
                    mesas_ocupadas_ids.append(reserva.mesa.id)

            mesas_ocupadas = Mesa.objects.filter(id__in=mesas_ocupadas_ids)
            mesas_disponibles = Mesa.objects.filter(capacidad__gte=personas).exclude(id__in=mesas_ocupadas_ids)
            ids_mesas_disponibles = list(mesas_disponibles.values_list("id", flat=True))

            fecha = fecha_obj.strftime("%Y-%m-%d")
            hora = hora_obj.strftime("%H:%M")

        elif request.POST.get("reservar") == "1":
            mesa_id = request.POST.get("mesa_id")
            mesa = get_object_or_404(Mesa, id=mesa_id)
            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")
            personas = request.POST.get("personas")

            datos = {
                "mesa": mesa.numero,
                "capacidad": mesa.capacidad,
                "fecha": fecha,
                "hora": hora,
                "personas": personas,
                "cliente": request.user.get_full_name(),
            }

            return render(request, "reservations/confirmar_reserva.html", {
                "datos": datos,
                "mesa_id": mesa.id,
                "fecha": fecha,
                "hora": hora,
                "personas": personas,
            })

    return render(request, "reservations/availability.html", {
        "form": form,
        "mesas_disponibles": mesas_disponibles,
        "mesas_ocupadas": mesas_ocupadas,
        "todas_mesas": todas_mesas,
        "ids_mesas_disponibles": ids_mesas_disponibles,
        "fecha": fecha,
        "hora": hora,
        "personas": personas,
    })


@login_required
def confirmar_reserva(request):
    if request.method == "POST":
        if request.POST.get("confirmar") == "1":
            mesa_id = request.POST.get("mesa_id")
            try:
                mesa = get_object_or_404(Mesa, id=mesa_id)
            except Exception:
                messages.error(request, "Mesa no válida.")
                return redirect("disponibilidad_y_reserva")

            fecha_str = request.POST.get("fecha", "")
            hora_str = request.POST.get("hora", "")
            personas_raw = request.POST.get("personas", "")
            cliente = request.user if request.user.is_authenticated else None

            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except Exception:
                try:
                    fecha = datetime.fromisoformat(fecha_str).date()
                except Exception:
                    messages.error(request, "Formato de fecha inválido.")
                    return redirect("disponibilidad_y_reserva")

            try:
                hora = datetime.strptime(hora_str, "%H:%M").time()
            except Exception:
                try:
                    hora = datetime.strptime(hora_str, "%H:%M:%S").time()
                except Exception:
                    try:
                        hora = datetime.fromisoformat(hora_str).time()
                    except Exception:
                        messages.error(request, "Formato de hora inválido.")
                        return redirect("disponibilidad_y_reserva")

            try:
                personas = int(personas_raw)
            except Exception:
                messages.error(request, "Número de personas inválido.")
                return redirect("disponibilidad_y_reserva")

            try:
                reserva = Reserva.objects.create(
                    mesa=mesa,
                    fecha=fecha,
                    hora=hora,
                    personas=personas,
                    cliente=cliente
                )

                if cliente and cliente.email:
                    try:
                        contexto_email = {
                            'reserva': reserva,
                            'user': cliente,
                            'fecha_display': reserva.fecha.strftime('%d de %B de %Y'),
                            'hora_display': reserva.hora.strftime('%H:%M'),
                        }
                        
                        html_content = render_to_string('reservations/email/confirmacion_reserva.html', contexto_email)
                        
                        email = EmailMessage(
                            f'¡Reserva Confirmada en Rapsodia! - Mesa {reserva.mesa.numero}',
                            html_content,
                            None,
                            [cliente.email] 
                        )
                        email.content_subtype = "html"
                        email.send()
                        
                    except Exception as e:
                        print(f"Error al enviar correo de confirmación para {cliente.email}: {e}")



            except ValidationError as e:
                messages.error(request, "No fue posible crear la reserva: " + "; ".join(e.messages))
                return redirect("disponibilidad_y_reserva")
            except Exception as e:
                messages.error(request, "Error al crear la reserva.")
                return redirect("disponibilidad_y_reserva")

            messages.success(request, "Reserva creada con éxito.")
            return redirect("reserva_confirmada", reserva_id=reserva.id)

        elif request.POST.get("editar") == "1":
            fecha_str = request.POST.get("fecha", "")
            hora_str = request.POST.get("hora", "")
            personas_raw = request.POST.get("personas", "")

            try:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except Exception:
                try:
                    fecha_obj = datetime.fromisoformat(fecha_str).date()
                except Exception:
                    fecha_obj = None

            try:
                try:
                    hora_obj = datetime.strptime(hora_str, "%H:%M").time()
                except Exception:
                    hora_obj = datetime.strptime(hora_str, "%H:%M:%S").time()
            except Exception:
                hora_obj = None

            initial = {}
            if fecha_obj:
                initial["fecha"] = fecha_obj
            if hora_obj:
                initial["hora"] = hora_obj
            if personas_raw:
                try:
                    initial["personas"] = int(personas_raw)
                except Exception:
                    pass

            form = DisponibilidadForm(initial=initial)
            return render(request, "reservations/availability.html", {"form": form})

        elif request.POST.get("cancelar") == "1":
            return redirect("disponibilidad_y_reserva")

    return redirect("disponibilidad_y_reserva")


@login_required
def reserva_confirmada(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    return render(request, "reservations/reserva_confirmada.html", {"reserva": reserva})

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    dt_reserva = datetime.combine(reserva.fecha, reserva.hora)
    dt_actual = datetime.now()

    if dt_reserva - dt_actual < timedelta(hours=24):
        messages.error(request, "Solo puedes cancelar la reserva con al menos 24 horas de anticipación.")
        return redirect("perfil_usuario")

    reserva.estado = "cancelada"
    reserva.save()

    messages.info(request, "Reserva cancelada.")
    return redirect("perfil_usuario")

@login_required
def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if request.method == "POST":
        form = EditarReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva actualizada correctamente.")
            return redirect("perfil_usuario")
    else:
        form = EditarReservaForm(instance=reserva)

    return render(request, "reservations/editar_reserva.html", {"form": form})

@login_required
def perfil_usuario(request):
    reservas = Reserva.objects.filter(cliente=request.user).order_by("id")
    return render(request, "users/perfil.html", {"reservas": reservas})


@login_required
def eliminar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)
    if reserva.estado == "cancelada":
        reserva.delete()
        messages.success(request, "Reserva eliminada correctamente.")
    else:
        messages.error(request, "Solo puedes eliminar reservas canceladas.")
    return redirect("perfil_usuario")


            
# DASHBOARD ADMINISTRATIVO
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    clientes = User.objects.all()
    mesas = Mesa.objects.all()
    
    reservas = Reserva.objects.all().order_by("-fecha", "-hora")

    filtro = request.GET.get("filtro", "semana")
    mes = request.GET.get("mes") 
    hoy = now()

    if mes:
        reservas = reservas.filter(fecha__month=mes)

    if filtro == "semana":
        inicio = hoy - timedelta(days=7)
        data = (
            reservas.filter(fecha__gte=inicio)
            .extra({"day": "date(fecha)"})
            .values("day")
            .annotate(total=Count("id"))
        )
        labels = [str(d["day"]) for d in data]
        values = [d["total"] for d in data]
    else:
        inicio = hoy - timedelta(days=30)
        data = (
            reservas.filter(fecha__gte=inicio)
            .extra({"month": "strftime('%%m', fecha)"})
            .values("month")
            .annotate(total=Count("id"))
        )
        labels = [f"Mes {d['month']}" for d in data]
        values = [d["total"] for d in data]

    dias_semana = (
        reservas.extra({"dow": "strftime('%%w', fecha)"})
        .values("dow")
        .annotate(total=Count("id"))
        .order_by("dow")
    )

    nombres_dias = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    dias_dict = {i: 0 for i in range(7)}
    for d in dias_semana:
        dias_dict[int(d["dow"])] = d["total"]

    dias_labels = [nombres_dias[i] for i in range(7)]
    dias_counts = [dias_dict[i] for i in range(7)]

    meses_disponibles = (
        Reserva.objects.dates("fecha", "month")
        .distinct()
        .values_list("fecha__month", flat=True)
    )

    MESES_ES = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    meses_contexto = [
        {"mes": m, "nombre": MESES_ES[m]} for m in sorted(set(meses_disponibles))
    ]

    mes_seleccionado_int = int(mes) if mes and mes.isdigit() else None
    
    if mes_seleccionado_int and 1 <= mes_seleccionado_int <= 12:
        nombre_mes_seleccionado = MESES_ES[mes_seleccionado_int]
    else:
        nombre_mes_seleccionado = "TODAS" 

    context = {
        "clientes": clientes,
        "mesas": mesas,
        "reservas": reservas,
        "labels": json.dumps(labels if labels else []),
        "data": json.dumps(values if values else []),
        "filtro": filtro,
        
        "reservas_activas": reservas.filter(estado__iexact="activa").count(),
        "reservas_canceladas": reservas.filter(estado__iexact="cancelada").count(),
        "reservas_pasadas": reservas.filter(estado__iexact="pasada").count(),
        
        "dias_labels": json.dumps(dias_labels),
        "dias_counts": json.dumps(dias_counts),
        "meses_disponibles": meses_contexto,
        "mes_seleccionado": mes_seleccionado_int,
        "nombre_mes_seleccionado": nombre_mes_seleccionado,
    }
    return render(request, "reservations/admin_dashboard.html", context)

class MesaListView(ListView):
    """
    Vista CRUD: Muestra el listado simple de mesas para Editar/Eliminar.
    Ahora usa la plantilla 'mesa_list_crud.html'
    """
    model = Mesa
    template_name = "reservations/mesa_list_crud.html" 
    context_object_name = "mesas"

class MesaCreateView(CreateView):
    model = Mesa
    fields = ["numero", "capacidad", "disponible"]
    template_name = "reservations/mesa_form.html"
    success_url = reverse_lazy("mesa_list")

class MesaUpdateView(UpdateView):
    model = Mesa
    fields = ["numero", "capacidad", "disponible"]
    template_name = "reservations/mesa_form.html"
    success_url = reverse_lazy("mesa_list")

class MesaDeleteView(DeleteView):
    model = Mesa
    template_name = "reservations/mesa_confirm_delete.html"
    success_url = reverse_lazy("mesa_list")

    def get(self, request, *args, **kwargs):
        print("kwargs:", kwargs)
        return super().get(request, *args, **kwargs)

@user_passes_test(lambda u: u.is_staff)
def mesa_plano_view(request):
    
    mesas = Mesa.objects.all().order_by('numero')
    
    current_time = now()
    DURACION_RESERVA = timedelta(hours=1, minutes=30) 
    
    for mesa in mesas:
        mesa.estado_actual = 'Libre'
        
        reservas_hoy = Reserva.objects.filter(
            mesa=mesa,
            fecha=current_time.date(),
            estado__iexact='activa'
        ).order_by('hora')
        
        for reserva in reservas_hoy:
            reserva_start = current_time.tzinfo.localize(
                datetime.combine(reserva.fecha, reserva.hora)
            )
            reserva_end = reserva_start + DURACION_RESERVA
            
            if reserva_start <= current_time < reserva_end:
                mesa.estado_actual = 'Ocupada'
                mesa.reserva_en_curso = reserva
                break
            
            elif current_time < reserva_start < current_time + timedelta(hours=2):
                if mesa.estado_actual == 'Libre': 
                    mesa.estado_actual = 'Reservada'
                    mesa.reserva_proxima = reserva
            

    context = {
        'mesas_con_estado': mesas,
        'now': current_time,
    }
    return render(request, 'reservations/mesa_plano.html', context)