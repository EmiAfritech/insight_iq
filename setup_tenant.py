#!/usr/bin/env python
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, '/workspaces/insight_iq')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight_iq.settings')
django.setup()

from tenants.models import Tenant, Domain

def create_public_tenant():
    """Create a public tenant for the landing page"""
    try:
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
            print(f'✓ Created public tenant: {tenant.name}')
        else:
            print(f'✓ Public tenant already exists: {tenant.name}')

        # Create domains
        domains_to_create = [
            ('localhost', True),
            ('localhost:8000', False),
            ('127.0.0.1', False),
            ('127.0.0.1:8000', False),
        ]

        for domain_name, is_primary in domains_to_create:
            domain, created = Domain.objects.get_or_create(
                domain=domain_name,
                defaults={
                    'tenant': tenant,
                    'is_primary': is_primary,
                }
            )

            if created:
                print(f'✓ Created domain: {domain.domain}')
            else:
                print(f'✓ Domain already exists: {domain.domain}')

        print('\n🎉 Public tenant setup completed successfully!')
        print('You can now access the landing page at http://localhost:8000/')
        
        return True

    except Exception as e:
        print(f'❌ Error creating public tenant: {e}')
        return False

if __name__ == '__main__':
    success = create_public_tenant()
    sys.exit(0 if success else 1)
