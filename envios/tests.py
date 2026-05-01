from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Cliente
from config.choices import EstadoEnvio, EstadoGeneral, TipoDocumento
from rutas.models import Ruta

from .forms import EncomiendaForm
from .models import Empleado, Encomienda, HistorialEstado


class EncomiendaModelTests(TestCase):
    def setUp(self):
        self.remitente = Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="12345678",
            nombres="Carlos",
            apellidos="Ramirez Torres",
            telefono="987654321",
            email="carlos@mail.com",
        )
        self.destinatario = Cliente.objects.create(
            tipo_doc=TipoDocumento.DNI,
            nro_doc="87654321",
            nombres="Ana",
            apellidos="Flores Diaz",
            telefono="912345678",
        )
        self.ruta = Ruta.objects.create(
            codigo="LIM-TRU",
            origen="Lima",
            destino="Trujillo",
            precio_base=Decimal("25.00"),
            dias_entrega=2,
        )
        self.empleado = Empleado.objects.create(
            codigo="EMP001",
            nombres="Luis",
            apellidos="Mendoza Cruz",
            cargo="Operador de envios",
            email="luis@encomiendas.pe",
            fecha_ingreso=date.today(),
        )

    def test_validation_error_with_invalid_encomienda_data(self):
        encomienda = Encomienda(
            codigo="ENC-2026-002",
            descripcion="Prueba",
            peso_kg=Decimal("-1"),
            remitente=self.remitente,
            destinatario=self.remitente,
            ruta=self.ruta,
            empleado_registro=self.empleado,
            costo_envio=Decimal("25.00"),
            fecha_entrega_est=timezone.now().date() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as context:
            encomienda.save()

        errors = context.exception.message_dict
        self.assertIn("peso_kg", errors)
        self.assertIn("destinatario", errors)
        self.assertIn("fecha_entrega_est", errors)

    def test_cambiar_estado_crea_historial(self):
        encomienda = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Documentos legales",
            peso_kg=Decimal("1.50"),
        )

        encomienda.cambiar_estado(
            nuevo_estado=EstadoEnvio.EN_TRANSITO,
            empleado=self.empleado,
            observacion="Encomienda recogida en agencia Lima",
        )

        encomienda.refresh_from_db()
        self.assertEqual(encomienda.estado, EstadoEnvio.EN_TRANSITO)
        self.assertTrue(encomienda.esta_en_transito)
        self.assertEqual(HistorialEstado.objects.count(), 1)

    def test_querysets_y_propiedades_funcionan(self):
        encomienda = Encomienda.crear_con_costo_calculado(
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
            empleado=self.empleado,
            descripcion="Zapatos y ropa de nino",
            peso_kg=Decimal("7.00"),
        )

        self.assertEqual(Cliente.objects.activos().count(), 2)
        self.assertEqual(Cliente.objects.buscar("rami").count(), 1)
        self.assertEqual(Encomienda.objects.pendientes().count(), 1)
        self.assertEqual(Encomienda.objects.activas().por_ruta(self.ruta).count(), 1)
        self.assertEqual(self.remitente.nombre_completo, "Ramirez Torres, Carlos")
        self.assertEqual(self.remitente.total_encomiendas_enviadas, 1)
        self.assertEqual(encomienda.costo_envio, Decimal("30.00"))


class EncomiendaFormTests(TestCase):
    def setUp(self):
        self.remitente = Cliente.objects.create(
            nro_doc="12345678",
            nombres="Mario",
            apellidos="Lopez",
        )
        self.destinatario = Cliente.objects.create(
            nro_doc="87654321",
            nombres="Lucia",
            apellidos="Perez",
        )
        self.inactivo = Cliente.objects.create(
            nro_doc="11223344",
            nombres="Inactivo",
            apellidos="Cliente",
            estado=EstadoGeneral.DE_BAJA,
        )
        self.ruta = Ruta.objects.create(
            codigo="LIM-CUS",
            origen="Lima",
            destino="Cusco",
            precio_base=Decimal("40.00"),
            dias_entrega=3,
        )
        self.ruta_inactiva = Ruta.objects.create(
            codigo="LIM-PIU",
            origen="Lima",
            destino="Piura",
            precio_base=Decimal("35.00"),
            dias_entrega=2,
            estado=EstadoGeneral.DE_BAJA,
        )

    def test_form_solo_muestra_clientes_y_rutas_activas(self):
        form = EncomiendaForm()

        self.assertQuerySetEqual(
            form.fields["remitente"].queryset.order_by("pk"),
            Cliente.objects.activos().order_by("pk"),
            transform=lambda obj: obj,
        )
        self.assertQuerySetEqual(
            form.fields["ruta"].queryset.order_by("pk"),
            Ruta.objects.activas().order_by("pk"),
            transform=lambda obj: obj,
        )
        self.assertNotIn(self.inactivo, form.fields["remitente"].queryset)
        self.assertNotIn(self.ruta_inactiva, form.fields["ruta"].queryset)

    def test_form_rechaza_remitente_y_destinatario_iguales(self):
        form = EncomiendaForm(
            data={
                "codigo": "ENC-0001",
                "descripcion": "Documentos",
                "peso_kg": "1.00",
                "remitente": self.remitente.pk,
                "destinatario": self.remitente.pk,
                "ruta": self.ruta.pk,
                "costo_envio": "40.00",
                "fecha_entrega_est": (
                    timezone.now().date() + timedelta(days=1)
                ).isoformat(),
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            "El remitente y el destinatario no pueden ser la misma persona.",
            form.non_field_errors(),
        )


class EncomiendaViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="operador",
            email="operador@encomiendas.pe",
            password="clave-segura-123",
            first_name="Operador",
        )
        self.empleado = Empleado.objects.create(
            codigo="EMP100",
            nombres="Paola",
            apellidos="Diaz",
            cargo="Operadora",
            email="operador@encomiendas.pe",
            fecha_ingreso=date.today(),
        )
        self.remitente = Cliente.objects.create(
            nro_doc="12345678",
            nombres="Carlos",
            apellidos="Lopez",
        )
        self.destinatario = Cliente.objects.create(
            nro_doc="87654321",
            nombres="Elena",
            apellidos="Ruiz",
        )
        self.ruta = Ruta.objects.create(
            codigo="LIM-ARE",
            origen="Lima",
            destino="Arequipa",
            precio_base=Decimal("32.00"),
            dias_entrega=2,
        )

    def test_dashboard_redirige_si_no_hay_sesion(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_dashboard_carga_si_hay_sesion(self):
        self.client.login(username="operador", password="clave-segura-123")

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "envios/dashboard.html")
        self.assertIn("total_activas", response.context)

    def test_crear_encomienda_desde_formulario(self):
        self.client.login(username="operador", password="clave-segura-123")

        response = self.client.post(
            reverse("encomienda_crear"),
            data={
                "codigo": "ENC-TEST-001",
                "descripcion": "Paquete de prueba",
                "peso_kg": "2.50",
                "volumen_cm3": "1500.00",
                "remitente": self.remitente.pk,
                "destinatario": self.destinatario.pk,
                "ruta": self.ruta.pk,
                "costo_envio": "32.00",
                "fecha_entrega_est": (
                    timezone.now().date() + timedelta(days=1)
                ).isoformat(),
                "observaciones": "Entrega normal",
            },
        )

        self.assertEqual(Encomienda.objects.count(), 1)
        encomienda = Encomienda.objects.first()
        self.assertEqual(encomienda.empleado_registro, self.empleado)
        self.assertRedirects(response, reverse("encomienda_detalle", args=[encomienda.pk]))
