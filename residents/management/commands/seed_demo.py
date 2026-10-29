"""Carga datos ficticios para demostrar el primer incremento.

Reglas de seguridad:
- Solo se ejecuta con DEMO_MODE activo (por defecto, DEBUG).
- Se niega a mezclar datos ficticios con fichas no marcadas como demo.
- Todas las fichas creadas quedan con is_demo=True.
"""

from __future__ import annotations

from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Role, User
from care.models import CarePlan, DailyCareRecord, shift_for_time
from residents.models import Contact, Resident
from residents.rut import calculate_dv

DEMO_PASSWORD = "DemoEleam2026!"

DEMO_USERS = [
    {
        "email": "administracion@example.test",
        "first_name": "Andrés",
        "last_name": "Demo",
        "role": Role.ADMINISTRACION,
    },
    {
        "email": "direccion@example.test",
        "first_name": "Daniela",
        "last_name": "Demo",
        "role": Role.DIRECCION,
    },
    {
        "email": "enfermeria@example.test",
        "first_name": "Carolina",
        "last_name": "Demo",
        "role": Role.ENFERMERIA,
    },
    {
        "email": "tecnico@example.test",
        "first_name": "Tamara",
        "last_name": "Demo",
        "role": Role.TECNICO,
    },
    {
        "email": "cuidador@example.test",
        "first_name": "Camila",
        "last_name": "Demo",
        "role": Role.CUIDADOR,
    },
]

# Cuerpos de RUT ficticios. El dígito verificador se calcula al cargar.
DEMO_RESIDENTS = [
    {
        "body": "11222333",
        "first_name": "Rosa",
        "last_name": "Ficticia Pérez",
        "preferred_name": "Rosita",
        "birth_date": date(1942, 3, 12),
        "sex": Resident.Sex.FEMENINO,
        "room": "12",
        "admission_date": date(2023, 6, 14),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "Penicilina",
        "relevant_background": (
            "Hipertensión arterial, artrosis de rodilla y deterioro cognitivo leve. "
            "Usa audífono en oído derecho."
        ),
        "clinical_notes": (
            "Prefiere que le hablen de frente y despacio. Camina con apoyo; requiere "
            "supervisión en el baño. No usa barreras de contención."
        ),
        "contacts": [
            {
                "name": "María Ficticia Pérez",
                "relationship": "Hija · representante familiar",
                "phone": "+56 9 0000 0001",
                "email": "maria@example.test",
                "is_primary": True,
                "notes": "Prefiere llamadas entre 09:00 y 18:00.",
            },
            {
                "name": "Jorge Ficticio Pérez",
                "relationship": "Hijo",
                "phone": "+56 9 0000 0011",
                "email": "jorge@example.test",
                "is_primary": False,
                "notes": "Vive en otra ciudad; disponible en caso de urgencia.",
            },
        ],
    },
    {
        "body": "13456789",
        "first_name": "Juan",
        "last_name": "De Prueba Soto",
        "preferred_name": "",
        "birth_date": date(1947, 8, 21),
        "sex": Resident.Sex.MASCULINO,
        "room": "3",
        "admission_date": date(2024, 1, 10),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "",
        "relevant_background": "Diabetes tipo 2 controlada con tratamiento oral.",
        "clinical_notes": "Camina sin apoyo. Control de glicemia según indicación de Enfermería.",
        "contacts": [
            {
                "name": "Pedro De Prueba",
                "relationship": "Hermano",
                "phone": "+56 9 0000 0002",
                "email": "pedro@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "14567890",
        "first_name": "Marta",
        "last_name": "Ejemplo Rojas",
        "preferred_name": "",
        "birth_date": date(1935, 5, 2),
        "sex": Resident.Sex.FEMENINO,
        "room": "4",
        "admission_date": date(2022, 11, 3),
        "status": Resident.Status.HOSPITALIZADO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "",
        "relevant_background": "EPOC. Oxígeno domiciliario indicado por su médico tratante.",
        "clinical_notes": (
            "Hospitalizada para estudio. Mantener la ficha actualizada al regreso. "
            "No tiene contacto principal registrado."
        ),
        "contacts": [],
    },
    {
        "body": "15678901",
        "first_name": "Pedro",
        "last_name": "Muestra Díaz",
        "preferred_name": "Don Pedro",
        "birth_date": date(1950, 2, 17),
        "sex": Resident.Sex.MASCULINO,
        "room": "7",
        "admission_date": date(2023, 2, 20),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.ISAPRE,
        "allergies": "Sulfas",
        "relevant_background": "Insuficiencia cardíaca crónica. Control de peso diario.",
        "clinical_notes": "Prefiere hablar en voz alta. Usa bastón para desplazarse.",
        "contacts": [
            {
                "name": "Lucía Muestra",
                "relationship": "Esposa",
                "phone": "+56 9 0000 0004",
                "email": "lucia@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "16789012",
        "first_name": "Elena",
        "last_name": "Simulación Vera",
        "preferred_name": "",
        "birth_date": date(1938, 10, 9),
        "sex": Resident.Sex.FEMENINO,
        "room": "2",
        "admission_date": date(2024, 5, 6),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "Látex",
        "relevant_background": "Artrosis severa. Requiere apoyo para vestirse.",
        "clinical_notes": "Evitar guantes de látex en todos los procedimientos.",
        "contacts": [
            {
                "name": "Jorge Simulación",
                "relationship": "Hijo",
                "phone": "+56 9 0000 0005",
                "email": "jorge.simulacion@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "17890123",
        "first_name": "Carlos",
        "last_name": "Ficticio Muñoz",
        "preferred_name": "",
        "birth_date": date(1945, 1, 30),
        "sex": Resident.Sex.MASCULINO,
        "room": "9",
        "admission_date": date(2023, 9, 12),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.PARTICULAR,
        "allergies": "",
        "relevant_background": "Secuelas de accidente cerebrovascular leve.",
        "clinical_notes": "Terapia fonoaudiológica dos veces por semana.",
        "contacts": [
            {
                "name": "Rosa Ficticio",
                "relationship": "Hija",
                "phone": "+56 9 0000 0006",
                "email": "rosa.ficticio@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "18901234",
        "first_name": "Ana",
        "last_name": "Demostración Lagos",
        "preferred_name": "Anita",
        "birth_date": date(1953, 7, 15),
        "sex": Resident.Sex.FEMENINO,
        "room": "5",
        "admission_date": date(2024, 3, 18),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "AINEs",
        "relevant_background": "Gastritis crónica. Deterioro visual leve.",
        "clinical_notes": "Requiere letra grande en documentos impresos.",
        "contacts": [
            {
                "name": "María Demostración",
                "relationship": "Sobrina",
                "phone": "+56 9 0000 0007",
                "email": "maria.demostracion@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "19012345",
        "first_name": "Sofía",
        "last_name": "Muestra Rivas",
        "preferred_name": "",
        "birth_date": date(1936, 12, 1),
        "sex": Resident.Sex.FEMENINO,
        "room": "1",
        "admission_date": date(2021, 8, 9),
        "status": Resident.Status.EGRESADO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "",
        "relevant_background": "Ficha de ejemplo archivada.",
        "clinical_notes": "Egresó del establecimiento. Se conserva para trazabilidad.",
        "is_active": False,
        "contacts": [
            {
                "name": "Elena Muestra",
                "relationship": "Hija",
                "phone": "+56 9 0000 0009",
                "email": "elena.muestra@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
    {
        "body": "20123456",
        "first_name": "Luis",
        "last_name": "Ejemplo Fuentes",
        "preferred_name": "",
        "birth_date": date(1940, 4, 25),
        "sex": Resident.Sex.MASCULINO,
        "room": "11",
        "admission_date": date(2022, 6, 30),
        "status": Resident.Status.ACTIVO,
        "health_insurance": Resident.HealthInsurance.FONASA,
        "allergies": "",
        "relevant_background": "Hipoacusia bilateral. Usa audífonos.",
        "clinical_notes": "Hablar de frente y con voz clara.",
        "contacts": [
            {
                "name": "Carla Ejemplo",
                "relationship": "Hija",
                "phone": "+56 9 0000 0008",
                "email": "carla.ejemplo@example.test",
                "is_primary": True,
                "notes": "",
            }
        ],
    },
]

# Planes de cuidado ficticios. Se identifican por residente y título para
# mantener el comando idempotente.
DEMO_CARE_PLANS = [
    {
        "body": "11222333",
        "title": "Riesgo de caídas",
        "need": "Se levanta de noche sin apoyo y ha tenido tropiezos al caminar.",
        "objective": "Mantener desplazamientos seguros durante el día y la noche.",
        "actions": (
            "Acompañar al baño durante la noche; dejar el timbre al alcance; "
            "registrar cada salida de la cama."
        ),
        "review_in_days": 7,
    },
    {
        "body": "13456789",
        "title": "Apoyo en alimentación e hidratación",
        "need": "En algunos turnos deja parte de la ración y olvida beber agua.",
        "objective": "Mantener una ingesta suficiente y registrar lo observado.",
        "actions": (
            "Ofrecer agua entre comidas; registrar la cantidad aceptada; avisar "
            "a Enfermería si rechaza dos comidas seguidas."
        ),
        "review_in_days": 14,
    },
    {
        "body": "16789012",
        "title": "Movilidad y prevención de rigidez",
        "need": "Presenta artrosis severa y requiere apoyo para vestirse y desplazarse.",
        "objective": "Mantener movilidad según tolerancia y detectar molestias.",
        "actions": (
            "Acompañar en movilización suave; alternar descanso; registrar dolor "
            "o rechazo a moverse y avisar a Enfermería."
        ),
        "review_in_days": 10,
    },
]

# Registros ficticios de las últimas horas. Se cargan solo si no existen
# registros demo, para no duplicarlos al repetir el comando.
DEMO_CARE_RECORDS = [
    {
        "body": "11222333",
        "hours_ago": 2,
        "category": DailyCareRecord.Category.ALIMENTACION,
        "description": (
            "Aceptó el 100% de la ración servida. Permaneció sentada durante "
            "la comida y no presentó tos."
        ),
        "observations": "Se le recuerda beber agua entre comidas.",
        "requires_nursing_review": True,
        "author": "tecnico@example.test",
    },
    {
        "body": "11222333",
        "hours_ago": 6,
        "category": DailyCareRecord.Category.MOVILIDAD,
        "description": (
            "Caminó acompañada por el pasillo durante unos 10 minutos, con "
            "apoyo de andador. Sin tropiezos."
        ),
        "observations": "Se detuvo una vez a descansar. Continúa estable.",
        "author": "cuidador@example.test",
        "reviewed": True,
        "review_notes": "Se revisa con el turno; sin observaciones.",
    },
    {
        "body": "13456789",
        "hours_ago": 3,
        "category": DailyCareRecord.Category.HIDRATACION,
        "description": "Bebió 200 ml de agua durante la mañana. Aceptó sin dificultad.",
        "observations": "",
        "author": "cuidador@example.test",
    },
    {
        "body": "16789012",
        "hours_ago": 8,
        "category": DailyCareRecord.Category.HIGIENE,
        "description": (
            "Se realizó aseo parcial con apoyo. Colaboró durante el procedimiento."
        ),
        "observations": "Prefiere agua tibia.",
        "author": "tecnico@example.test",
    },
    {
        "body": "11222333",
        "hours_ago": 26,
        "category": DailyCareRecord.Category.HIDRATACION,
        "description": "Registró ingesta de 50 ml de agua en el turno.",
        "observations": "",
        "author": "tecnico@example.test",
        "correction_description": "Registró ingesta de 150 ml de agua en el turno.",
        "correction_reason": (
            "Se corrige la cantidad: la botella tenía 150 ml y no 50 ml."
        ),
    },
    {
        "body": "13456789",
        "hours_ago": 27,
        "category": DailyCareRecord.Category.SUENO,
        "description": (
            "Durmió sin interrupciones durante la noche. Se levantó una vez al "
            "baño con apoyo."
        ),
        "observations": "",
        "author": "cuidador@example.test",
    },
]


class Command(BaseCommand):
    help = "Crea usuarios y residentes ficticios para demostrar el sistema."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Permite ejecutar fuera de DEMO_MODE o con fichas no demo existentes.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]

        if not settings.DEMO_MODE and not force:
            raise CommandError(
                "DEMO_MODE está desactivado. Este comando solo carga datos ficticios "
                "en demostración. Usa --force solo si sabes lo que haces."
            )

        if Resident.objects.exclude(is_demo=True).exists() and not force:
            raise CommandError(
                "Hay fichas que no están marcadas como demo. Para evitar mezclar "
                "datos ficticios con datos reales, el comando se detuvo. "
                "No uses --force en un entorno con información real."
            )

        users_by_email = {}
        users_created = 0
        users_updated = 0
        for data in DEMO_USERS:
            user, created = User.objects.update_or_create(
                email=data["email"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "role": data["role"],
                    "is_active": True,
                },
            )
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password", "updated_at"])
            users_by_email[data["email"]] = user
            if created:
                users_created += 1
            else:
                users_updated += 1

        residents_by_body = {}
        residents_created = 0
        residents_updated = 0
        contacts_created = 0

        for data in DEMO_RESIDENTS:
            payload = dict(data)
            contacts = payload.pop("contacts")
            body = payload.pop("body")
            rut = f"{body}-{calculate_dv(body)}"
            defaults = {
                **payload,
                "rut": rut,
                "is_demo": True,
                "is_active": payload.get("is_active", True),
            }
            resident, created = Resident.objects.update_or_create(
                rut=rut,
                defaults=defaults,
            )
            residents_by_body[body] = resident
            if created:
                residents_created += 1
            else:
                residents_updated += 1

            for contact_data in contacts:
                _, contact_created = Contact.objects.update_or_create(
                    resident=resident,
                    name=contact_data["name"],
                    defaults={
                        "relationship": contact_data["relationship"],
                        "phone": contact_data["phone"],
                        "email": contact_data["email"],
                        "is_primary": contact_data["is_primary"],
                        "notes": contact_data["notes"],
                    },
                )
                if contact_created:
                    contacts_created += 1

        nurse = users_by_email["enfermeria@example.test"]
        today = timezone.localdate()
        plans_created = 0
        plans_updated = 0
        for data in DEMO_CARE_PLANS:
            resident = residents_by_body[data["body"]]
            plan, created = CarePlan.objects.update_or_create(
                resident=resident,
                title=data["title"],
                defaults={
                    "need": data["need"],
                    "objective": data["objective"],
                    "actions": data["actions"],
                    "responsible": nurse,
                    "start_date": today - timedelta(days=30),
                    "review_date": today + timedelta(days=data["review_in_days"]),
                    "status": CarePlan.Status.ACTIVO,
                },
            )
            if created:
                plan.created_by = nurse
                plan.updated_by = nurse
                plan.save(
                    update_fields=["created_by", "updated_by", "updated_at"]
                )
                plans_created += 1
            else:
                plans_updated += 1

        records_created = 0
        if not DailyCareRecord.objects.filter(resident__is_demo=True).exists():
            now = timezone.now()
            for data in DEMO_CARE_RECORDS:
                resident = residents_by_body[data["body"]]
                author = users_by_email[data["author"]]
                recorded_at = now - timedelta(hours=data["hours_ago"])
                corrected = bool(data.get("correction_description"))
                record = DailyCareRecord.objects.create(
                    resident=resident,
                    recorded_at=recorded_at,
                    shift=shift_for_time(recorded_at),
                    category=data["category"],
                    description=data["description"],
                    observations=data.get("observations", ""),
                    requires_nursing_review=data.get(
                        "requires_nursing_review", False
                    ),
                    created_by=author,
                    updated_by=author,
                    status=(
                        DailyCareRecord.Status.CORREGIDO
                        if corrected
                        else DailyCareRecord.Status.VIGENTE
                    ),
                )
                records_created += 1

                if data.get("reviewed"):
                    record.reviewed_by = nurse
                    record.reviewed_at = now - timedelta(minutes=20)
                    record.review_notes = data.get("review_notes", "")
                    record.save(
                        update_fields=[
                            "reviewed_by",
                            "reviewed_at",
                            "review_notes",
                            "updated_by",
                            "updated_at",
                        ]
                    )

                if corrected:
                    corrected_at = recorded_at + timedelta(minutes=30)
                    DailyCareRecord.objects.create(
                        resident=resident,
                        recorded_at=corrected_at,
                        shift=shift_for_time(corrected_at),
                        category=data["category"],
                        description=data["correction_description"],
                        observations=data.get("observations", ""),
                        requires_nursing_review=False,
                        created_by=author,
                        updated_by=author,
                        supersedes=record,
                        correction_reason=data["correction_reason"],
                    )
                    records_created += 1

        self.stdout.write(self.style.SUCCESS("Datos de demostración cargados."))
        self.stdout.write(
            f"Usuarios: {users_created} creados, {users_updated} actualizados. "
            f"Contraseña demo: {DEMO_PASSWORD}"
        )
        self.stdout.write(
            f"Residentes: {residents_created} creados, {residents_updated} actualizados. "
            f"Contactos nuevos: {contacts_created}."
        )
        self.stdout.write(
            f"Planes de cuidado: {plans_created} creados, {plans_updated} actualizados. "
            f"Registros de cuidado nuevos: {records_created}."
        )
        self.stdout.write(
            "Cuentas: administracion@ / direccion@ / enfermeria@ / tecnico@ / "
            "cuidador@example.test"
        )
