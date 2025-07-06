from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create initial tenant for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domain name for the tenant'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Default Tenant',
            help='Tenant name'
        )
        parser.add_argument(
            '--schema',
            type=str,
            default='public',
            help='Database schema name'
        )

    def handle(self, *args, **options):
        domain_name = options['domain']
        tenant_name = options['name']
        schema_name = options['schema']

        try:
            with transaction.atomic():
                # Check if tenant already exists
                if Tenant.objects.filter(schema_name=schema_name).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Tenant with schema "{schema_name}" already exists')
                    )
                    return

                # Create tenant
                tenant = Tenant.objects.create(
                    schema_name=schema_name,
                    name=tenant_name,
                    company_name=tenant_name,
                    contact_email='admin@localhost',
                    is_active=True
                )

                # Check if domain already exists
                if Domain.objects.filter(domain=domain_name).exists():
                    self.stdout.write(
                        self.style.WARNING(f'Domain "{domain_name}" already exists')
                    )
                    return

                # Create domain
                domain = Domain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=True
                )

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created tenant "{tenant_name}" with domain "{domain_name}"')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating tenant: {str(e)}')
            )
