# Generated by Django 4.2.8 on 2025-07-06 20:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriptionPlan",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "billing_period",
                    models.CharField(
                        choices=[
                            ("monthly", "Monthly"),
                            ("yearly", "Yearly"),
                            ("lifetime", "Lifetime"),
                        ],
                        max_length=20,
                    ),
                ),
                ("max_users", models.IntegerField()),
                ("max_storage_gb", models.IntegerField()),
                ("max_monthly_uploads", models.IntegerField()),
                ("ai_insights_enabled", models.BooleanField(default=True)),
                ("advanced_analytics_enabled", models.BooleanField(default=False)),
                ("custom_branding_enabled", models.BooleanField(default=False)),
                ("api_access_enabled", models.BooleanField(default=False)),
                ("priority_support", models.BooleanField(default=False)),
                ("stripe_price_id", models.CharField(blank=True, max_length=100)),
                ("is_active", models.BooleanField(default=True)),
                ("is_popular", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "subscriptions_subscriptionplan",
                "ordering": ["price"],
            },
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("canceled", "Canceled"),
                            ("expired", "Expired"),
                            ("suspended", "Suspended"),
                            ("trial", "Trial"),
                        ],
                        default="trial",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateTimeField()),
                ("end_date", models.DateTimeField()),
                ("trial_end_date", models.DateTimeField(blank=True, null=True)),
                (
                    "stripe_subscription_id",
                    models.CharField(blank=True, max_length=100),
                ),
                ("stripe_customer_id", models.CharField(blank=True, max_length=100)),
                ("current_users", models.IntegerField(default=0)),
                ("current_storage_gb", models.FloatField(default=0)),
                ("current_monthly_uploads", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="subscriptions.subscriptionplan",
                    ),
                ),
                (
                    "tenant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="subscription",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "subscriptions_subscription",
            },
        ),
        migrations.CreateModel(
            name="SubscriptionUsage",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("users_count", models.IntegerField(default=0)),
                ("storage_gb", models.FloatField(default=0)),
                ("monthly_uploads", models.IntegerField(default=0)),
                ("api_calls", models.IntegerField(default=0)),
                ("usage_date", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "subscription",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="usage_records",
                        to="subscriptions.subscription",
                    ),
                ),
            ],
            options={
                "db_table": "subscriptions_subscriptionusage",
                "unique_together": {("subscription", "usage_date")},
            },
        ),
    ]
