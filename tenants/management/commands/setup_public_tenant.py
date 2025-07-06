from django.core.management.base import BaseCommand
from django.conf import settings
from tenants.models import Tenant, Domain


class Command(BaseCommand):
    help = 'Create a public tenant for the landing page'

    def handle(self, *args, **options):
        # Create public tenant
        tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public',
                'company_name': 'InsightIQ',
                'company_description': 'AI-Powered Business Intelligence Platform',
                'contact_email': 'admin@insightiq.com',
                'is_active': True,
                'subscription_plan': 'public',
                'max_users': 1000,
                'max_storage_gb': 1000,
                'max_monthly_uploads': 10000,
                'ai_insights_enabled': True,
                'advanced_analytics_enabled': True,
                'custom_branding_enabled': True,
                'api_access_enabled': True,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created public tenant: {tenant.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Public tenant already exists: {tenant.name}')
            )

        # Create domain for localhost
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            defaults={
                'tenant': tenant,
                'is_primary': True,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created domain: {domain.domain}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Domain already exists: {domain.domain}')
            )

        # Create domain for 127.0.0.1
        domain_ip, created = Domain.objects.get_or_create(
            domain='127.0.0.1:8000',
            defaults={
                'tenant': tenant,
                'is_primary': False,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created domain: {domain_ip.domain}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Domain already exists: {domain_ip.domain}')
            )

        # Create domain for localhost:8000
        domain_port, created = Domain.objects.get_or_create(
            domain='localhost:8000',
            defaults={
                'tenant': tenant,
                'is_primary': False,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created domain: {domain_port.domain}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Domain already exists: {domain_port.domain}')
            )

        self.stdout.write(
            self.style.SUCCESS('Public tenant setup completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now access the landing page at http://localhost:8000/')
        )
