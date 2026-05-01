from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from config.choices import EstadoEnvio

from .forms import EncomiendaForm
from .models import Encomienda
from .utils import obtener_empleado_para_usuario


@login_required
def dashboard(request):
    """Main dashboard with live shipment counters."""

    hoy = timezone.now().date()
    ultimas = Encomienda.objects.con_relaciones()[:5]

    context = {
        "total_activas": Encomienda.objects.activas().count(),
        "en_transito": Encomienda.objects.en_transito().count(),
        "con_retraso": Encomienda.objects.con_retraso().count(),
        "entregadas_hoy": Encomienda.objects.filter(
            estado=EstadoEnvio.ENTREGADO,
            fecha_entrega_real=hoy,
        ).count(),
        "ultimas": ultimas,
    }
    return render(request, "envios/dashboard.html", context)


@require_GET
@login_required
def encomienda_lista(request):
    """Paginated list with search and state filters."""

    qs = Encomienda.objects.con_relaciones()
    estado = request.GET.get("estado", "")
    q = request.GET.get("q", "")

    if estado:
        qs = qs.filter(estado=estado)

    if q:
        qs = qs.filter(
            Q(codigo__icontains=q)
            | Q(remitente__apellidos__icontains=q)
            | Q(remitente__nombres__icontains=q)
            | Q(destinatario__apellidos__icontains=q)
            | Q(destinatario__nombres__icontains=q)
            | Q(remitente__nro_doc__icontains=q)
            | Q(destinatario__nro_doc__icontains=q)
        )

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page", 1)
    encomiendas = paginator.get_page(page_number)

    return render(
        request,
        "envios/lista.html",
        {
            "encomiendas": encomiendas,
            "estados": EstadoEnvio.choices,
            "estado_activo": estado,
            "q": q,
        },
    )


@login_required
def encomienda_detalle(request, pk):
    """Show a single shipment with its state history."""

    encomienda = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)
    historial = encomienda.historial.select_related("empleado")

    return render(
        request,
        "envios/detalle.html",
        {
            "encomienda": encomienda,
            "historial": historial,
            "estados": EstadoEnvio.choices,
        },
    )


@login_required
def encomienda_crear(request):
    """GET shows the form, POST validates and stores a new shipment."""

    if request.method == "POST":
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            enc = form.save(commit=False)
            empleado = obtener_empleado_para_usuario(request.user)
            if empleado is None:
                messages.error(
                    request,
                    "No hay un empleado activo disponible para registrar la encomienda.",
                )
                return render(
                    request,
                    "envios/form.html",
                    {"form": form, "titulo": "Nueva Encomienda"},
                )

            enc.empleado_registro = empleado
            enc.save()
            messages.success(
                request,
                f"Encomienda {enc.codigo} registrada correctamente.",
            )
            return redirect("encomienda_detalle", pk=enc.pk)
    else:
        form = EncomiendaForm()

    return render(
        request,
        "envios/form.html",
        {
            "form": form,
            "titulo": "Nueva Encomienda",
        },
    )


@require_POST
@login_required
def encomienda_cambiar_estado(request, pk):
    """Change shipment status from the detail modal."""

    encomienda = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)
    nuevo_estado = request.POST.get("estado")
    observacion = request.POST.get("observacion", "")
    empleado = obtener_empleado_para_usuario(request.user)

    if empleado is None:
        messages.error(
            request,
            "No hay un empleado activo disponible para registrar el cambio de estado.",
        )
        return redirect("encomienda_detalle", pk=pk)

    try:
        encomienda.cambiar_estado(nuevo_estado, empleado, observacion)
        messages.success(
            request,
            f"Estado actualizado a {encomienda.get_estado_display()}.",
        )
    except (ValidationError, ValueError) as exc:
        messages.error(request, str(exc))

    return redirect("encomienda_detalle", pk=pk)


@require_GET
@login_required
def encomienda_estado_json(request, pk):
    """Small JSON endpoint useful for AJAX or quick checks."""

    encomienda = get_object_or_404(Encomienda, pk=pk)
    return JsonResponse(
        {
            "codigo": encomienda.codigo,
            "estado": encomienda.estado,
            "display": encomienda.get_estado_display(),
            "retraso": encomienda.tiene_retraso,
            "dias": encomienda.dias_en_transito,
        }
    )
