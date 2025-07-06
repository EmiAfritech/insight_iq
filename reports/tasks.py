from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Report, ReportShare, ReportExport
from .utils import generate_report, export_report, cleanup_old_report_files, schedule_report_generation
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_report_task(report_id):
    """
    Wrapper task for report generation
    """
    return generate_report(report_id)


@shared_task
def send_report_share_notification(share_id):
    """
    Send email notification when a report is shared
    """
    try:
        share = ReportShare.objects.get(id=share_id)
        
        # Prepare email content
        subject = f"Report Shared: {share.report.title}"
        
        context = {
            'share': share,
            'report': share.report,
            'shared_by': share.shared_by,
            'shared_with': share.shared_with_email,
            'message': share.message,
            'access_url': f"{settings.SITE_URL}/reports/shared/{share.report.share_token}/"
        }
        
        # Render email templates
        html_message = render_to_string('reports/emails/report_shared.html', context)
        text_message = render_to_string('reports/emails/report_shared.txt', context)
        
        # Send email
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[share.shared_with_email],
            fail_silently=False
        )
        
        logger.info(f"Report share notification sent to {share.shared_with_email}")
        return {'status': 'success', 'email': share.shared_with_email}
        
    except ReportShare.DoesNotExist:
        logger.error(f"ReportShare {share_id} not found")
        return {'status': 'error', 'message': 'Share not found'}
    except Exception as e:
        logger.error(f"Error sending report share notification: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def send_report_generation_notification(report_id):
    """
    Send notification when report generation is complete
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # Only send notification if report generation was successful
        if report.status != 'completed':
            return {'status': 'skipped', 'reason': 'Report not completed'}
        
        # Prepare email content
        subject = f"Report Generated: {report.title}"
        
        context = {
            'report': report,
            'user': report.created_by,
            'report_url': f"{settings.SITE_URL}/reports/{report.id}/"
        }
        
        # Render email templates
        html_message = render_to_string('reports/emails/report_generated.html', context)
        text_message = render_to_string('reports/emails/report_generated.txt', context)
        
        # Send email to report creator
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[report.created_by.email],
            fail_silently=False
        )
        
        logger.info(f"Report generation notification sent to {report.created_by.email}")
        return {'status': 'success', 'email': report.created_by.email}
        
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}
    except Exception as e:
        logger.error(f"Error sending report generation notification: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def export_report_task(report_id, format_type, user_id):
    """
    Export a report in the specified format
    """
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        report = Report.objects.get(id=report_id)
        user = User.objects.get(id=user_id)
        
        # Generate export file
        file_path = export_report(report, format_type)
        
        if file_path:
            # Create export record
            export_record = ReportExport.objects.create(
                report=report,
                exported_by=user,
                format=format_type,
                file_path=file_path
            )
            
            # Calculate file size
            import os
            if os.path.exists(file_path):
                export_record.file_size = os.path.getsize(file_path)
                export_record.save()
            
            logger.info(f"Report exported successfully: {file_path}")
            return {
                'status': 'success',
                'file_path': file_path,
                'export_id': str(export_record.id)
            }
        else:
            return {'status': 'error', 'message': 'Export failed'}
            
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def cleanup_expired_shares():
    """
    Clean up expired report shares
    """
    try:
        now = timezone.now()
        expired_shares = ReportShare.objects.filter(
            expires_at__lt=now
        ).exclude(expires_at__isnull=True)
        
        count = expired_shares.count()
        expired_shares.delete()
        
        logger.info(f"Cleaned up {count} expired report shares")
        return {'status': 'success', 'cleaned_count': count}
        
    except Exception as e:
        logger.error(f"Error cleaning up expired shares: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def generate_scheduled_reports():
    """
    Generate all scheduled reports that are due
    """
    return schedule_report_generation()


@shared_task
def cleanup_old_reports():
    """
    Clean up old report files
    """
    return cleanup_old_report_files()


@shared_task
def send_report_digest(tenant_id):
    """
    Send a digest of recent reports to tenant administrators
    """
    try:
        from tenants.models import Tenant
        from datetime import timedelta
        
        tenant = Tenant.objects.get(id=tenant_id)
        
        # Get reports from the last week
        week_ago = timezone.now() - timedelta(days=7)
        recent_reports = Report.objects.filter(
            tenant=tenant,
            created_at__gte=week_ago
        ).order_by('-created_at')
        
        if not recent_reports.exists():
            logger.info(f"No recent reports for tenant {tenant.name}")
            return {'status': 'skipped', 'reason': 'No recent reports'}
        
        # Get tenant administrators
        admin_users = tenant.users.filter(
            role__in=['admin', 'owner']
        )
        
        if not admin_users.exists():
            logger.info(f"No admin users for tenant {tenant.name}")
            return {'status': 'skipped', 'reason': 'No admin users'}
        
        # Prepare email content
        subject = f"Weekly Report Digest - {tenant.name}"
        
        context = {
            'tenant': tenant,
            'reports': recent_reports,
            'report_count': recent_reports.count(),
            'week_start': week_ago.strftime('%Y-%m-%d'),
            'week_end': timezone.now().strftime('%Y-%m-%d')
        }
        
        # Render email templates
        html_message = render_to_string('reports/emails/report_digest.html', context)
        text_message = render_to_string('reports/emails/report_digest.txt', context)
        
        # Send email to all administrators
        admin_emails = [user.email for user in admin_users if user.email]
        
        if admin_emails:
            send_mail(
                subject=subject,
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False
            )
            
            logger.info(f"Report digest sent to {len(admin_emails)} administrators")
            return {'status': 'success', 'sent_to': len(admin_emails)}
        else:
            return {'status': 'skipped', 'reason': 'No admin emails'}
            
    except Tenant.DoesNotExist:
        logger.error(f"Tenant {tenant_id} not found")
        return {'status': 'error', 'message': 'Tenant not found'}
    except Exception as e:
        logger.error(f"Error sending report digest: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def process_report_comments(report_id):
    """
    Process new comments on a report and send notifications
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # Get recent comments (last 5 minutes)
        from datetime import timedelta
        recent_cutoff = timezone.now() - timedelta(minutes=5)
        
        recent_comments = report.comments.filter(
            created_at__gte=recent_cutoff
        ).exclude(author=report.created_by)
        
        if not recent_comments.exists():
            return {'status': 'skipped', 'reason': 'No recent comments'}
        
        # Notify report creator if there are new comments
        if report.created_by.email:
            subject = f"New Comments on Report: {report.title}"
            
            context = {
                'report': report,
                'comments': recent_comments,
                'comment_count': recent_comments.count(),
                'report_url': f"{settings.SITE_URL}/reports/{report.id}/"
            }
            
            # Render email templates
            html_message = render_to_string('reports/emails/new_comments.html', context)
            text_message = render_to_string('reports/emails/new_comments.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=text_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[report.created_by.email],
                fail_silently=False
            )
            
            logger.info(f"Comment notification sent to {report.created_by.email}")
            return {'status': 'success', 'email': report.created_by.email}
        
        return {'status': 'skipped', 'reason': 'No email for report creator'}
        
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}
    except Exception as e:
        logger.error(f"Error processing report comments: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def update_report_analytics(report_id):
    """
    Update analytics data for a report
    """
    try:
        report = Report.objects.get(id=report_id)
        
        # Calculate analytics data
        analytics = {
            'total_views': report.shares.aggregate(
                total_views=models.Sum('access_count')
            )['total_views'] or 0,
            'total_shares': report.shares.count(),
            'total_exports': report.exports.count(),
            'total_comments': report.comments.count(),
            'last_accessed': report.shares.aggregate(
                last_accessed=models.Max('accessed_at')
            )['last_accessed'],
            'updated_at': timezone.now().isoformat()
        }
        
        # Update report content with analytics
        if not report.content:
            report.content = {}
        
        report.content['analytics'] = analytics
        report.save()
        
        logger.info(f"Analytics updated for report {report.id}")
        return {'status': 'success', 'analytics': analytics}
        
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}
    except Exception as e:
        logger.error(f"Error updating report analytics: {str(e)}")
        return {'status': 'error', 'message': str(e)}
