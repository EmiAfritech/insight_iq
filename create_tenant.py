#!/usr/bin/env python
import os
import sys
import django

# Add the project path to Python path
sys.path.insert(0, '/workspaces/insight_iq')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight_iq.settings')
django.setup()

from tenants.models import Tenant, Domain
from django.db import transaction

def create_initial_tenant():
    try:
        with transaction.atomic():
            # Check if tenant already exists
            if Tenant.objects.filter(schema_name='public').exists():
                print("Tenant already exists")
                tenant = Tenant.objects.get(schema_name='public')
            else:
                # Create tenant
                tenant = Tenant.objects.create(
                    schema_name='public',
                    name='Default Tenant',
                    company_name='Default Company',
                    contact_email='admin@localhost',
                    is_active=True
                )
                print(f"Created tenant: {tenant.name}")

            # Check if domain already exists
            if Domain.objects.filter(domain='localhost').exists():
                print("Domain already exists")
            else:
                # Create domain
                domain = Domain.objects.create(
                    domain='localhost',
                    tenant=tenant,
                    is_primary=True
                )
                print(f"Created domain: {domain.domain}")

            print("Setup completed successfully!")
            print(f"Tenants: {Tenant.objects.count()}")
            print(f"Domains: {Domain.objects.count()}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_initial_tenant()
