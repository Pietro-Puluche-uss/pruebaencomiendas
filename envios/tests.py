from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from clientes.models import Cliente
from config.choices import EstadoEnvio, EstadoGeneral, TipoDocumento
from rutas.models import Ruta

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
