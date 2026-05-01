from config.choices import EstadoGeneral

from .models import Empleado


def obtener_empleado_para_usuario(user):
    """
    Resolve the employee linked to the current authenticated user.

    The guide suggests matching by email. As a small fallback for classroom
    setups, we also use the first active employee if there is no exact match.
    """

    if not user.is_authenticated:
        return None

    if user.email:
        empleado = Empleado.objects.filter(
            email__iexact=user.email,
            estado=EstadoGeneral.ACTIVO,
        ).first()
        if empleado:
            return empleado

    return Empleado.objects.filter(estado=EstadoGeneral.ACTIVO).order_by(
        "apellidos",
        "nombres",
    ).first()
