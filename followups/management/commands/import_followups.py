import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from followups.models import FollowUp


class Command(BaseCommand):
    help = "Import followups from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            required=True,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username who owns the imported followups'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']
        username = options['username']

        # Validate user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR("User does not exist"))
            return

        # Validate UserProfile
        try:
            clinic = user.userprofile.clinic
        except Exception:
            self.stderr.write(
                self.style.ERROR("UserProfile or Clinic not found for user")
            )
            return

        created_count = 0
        skipped_count = 0

        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                required_fields = [
                    'patient_name',
                    'phone',
                    'language',
                    'due_date'
                ]

                for row_number, row in enumerate(reader, start=2):
                    # Validate required fields
                    if not all(row.get(field) for field in required_fields):
                        skipped_count += 1
                        continue

                    # Validate language
                    if row['language'] not in ['en', 'hi']:
                        skipped_count += 1
                        continue

                    # Validate due_date
                    try:
                        due_date = datetime.strptime(
                            row['due_date'],
                            '%Y-%m-%d'
                        ).date()
                    except ValueError:
                        skipped_count += 1
                        continue

                    # Create FollowUp
                    FollowUp.objects.create(
                        clinic=clinic,
                        created_by=user,
                        patient_name=row['patient_name'],
                        phone=row['phone'],
                        language=row['language'],
                        notes=row.get('notes', ''),
                        due_date=due_date
                    )

                    created_count += 1

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("CSV file not found"))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed: {created_count} created, {skipped_count} skipped"
            )
        )
