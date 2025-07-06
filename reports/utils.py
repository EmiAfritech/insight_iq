from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from celery import shared_task
import os
import json
import tempfile
import uuid
from datetime import datetime, timedelta
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

# Import libraries for report generation
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    from reportlab.lib import colors
    import xlsxwriter
    from weasyprint import HTML, CSS
    HAS_REPORTING_LIBS = True
except ImportError:
    HAS_REPORTING_LIBS = False
    logger.warning("Reporting libraries not installed. Some features may not work.")


@shared_task
def generate_report(report_id):
    """
    Celery task to generate a report asynchronously
    """
    from .models import Report
    
    try:
        report = Report.objects.get(id=report_id)
        report.status = 'generating'
        report.save()
        
        # Generate the report content
        success = _generate_report_content(report)
        
        if success:
            report.status = 'completed'
            report.generated_at = timezone.now()
            
            # Schedule next generation if needed
            if report.is_scheduled:
                report.next_generation = _calculate_next_generation(report)
        else:
            report.status = 'failed'
        
        report.save()
        
        return {'status': 'success', 'report_id': str(report_id)}
    
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        return {'status': 'error', 'message': 'Report not found'}
    except Exception as e:
        logger.error(f"Error generating report {report_id}: {str(e)}")
        try:
            report = Report.objects.get(id=report_id)
            report.status = 'failed'
            report.save()
        except:
            pass
        return {'status': 'error', 'message': str(e)}


def _generate_report_content(report):
    """
    Generate the actual report content based on its configuration
    """
    if not HAS_REPORTING_LIBS:
        logger.error("Reporting libraries not available")
        return False
    
    try:
        # Collect data from dashboards and analyses
        data = _collect_report_data(report)
        
        # Generate visualizations
        charts = _generate_report_charts(report, data)
        
        # Create report content structure
        content = {
            'title': report.title,
            'description': report.description,
            'executive_summary': report.executive_summary,
            'generated_at': timezone.now().isoformat(),
            'data': data,
            'charts': charts,
            'recommendations': report.recommendations,
            'sections': []
        }
        
        # Generate sections
        for section in report.sections.filter(is_visible=True).order_by('order'):
            section_content = _generate_section_content(section, data, charts)
            content['sections'].append(section_content)
        
        # Generate key insights using AI if available
        if hasattr(report, 'ai_insights_enabled') and report.ai_insights_enabled:
            content['key_insights'] = _generate_ai_insights(data)
        
        # Save content to report
        report.content = content
        report.save()
        
        # Generate file if needed
        if report.format != 'html':
            file_path = _generate_report_file(report, content)
            report.file_path = file_path
            
            # Calculate file size
            if os.path.exists(file_path):
                report.file_size = os.path.getsize(file_path)
            
            report.save()
        
        return True
    
    except Exception as e:
        logger.error(f"Error generating report content: {str(e)}")
        return False


def _collect_report_data(report):
    """
    Collect data from associated dashboards and analyses
    """
    data = {
        'dashboards': [],
        'analyses': [],
        'datasets': []
    }
    
    # Collect dashboard data
    for dashboard in report.dashboards.all():
        dashboard_data = {
            'id': str(dashboard.id),
            'name': dashboard.name,
            'description': dashboard.description,
            'widgets': []
        }
        
        # Collect widget data
        for widget in dashboard.widgets.all():
            widget_data = {
                'id': str(widget.id),
                'name': widget.name,
                'type': widget.widget_type,
                'config': widget.config,
                'data': widget.data
            }
            dashboard_data['widgets'].append(widget_data)
        
        data['dashboards'].append(dashboard_data)
    
    # Collect analysis data
    for analysis in report.analyses.all():
        analysis_data = {
            'id': str(analysis.id),
            'name': analysis.name,
            'description': analysis.description,
            'type': analysis.analysis_type,
            'results': analysis.results,
            'insights': analysis.insights
        }
        data['analyses'].append(analysis_data)
    
    return data


def _generate_report_charts(report, data):
    """
    Generate chart images for the report
    """
    charts = []
    
    if not report.include_charts:
        return charts
    
    try:
        # Set up matplotlib for non-interactive use
        plt.switch_backend('Agg')
        
        # Generate charts from dashboard widgets
        for dashboard_data in data['dashboards']:
            for widget_data in dashboard_data['widgets']:
                if widget_data['type'] in ['chart', 'graph', 'plot']:
                    chart_path = _generate_widget_chart(widget_data, report)
                    if chart_path:
                        charts.append({
                            'title': widget_data['name'],
                            'type': widget_data['type'],
                            'path': chart_path,
                            'source': f"Dashboard: {dashboard_data['name']}"
                        })
        
        # Generate charts from analysis results
        for analysis_data in data['analyses']:
            if analysis_data['results']:
                chart_path = _generate_analysis_chart(analysis_data, report)
                if chart_path:
                    charts.append({
                        'title': analysis_data['name'],
                        'type': 'analysis',
                        'path': chart_path,
                        'source': f"Analysis: {analysis_data['name']}"
                    })
    
    except Exception as e:
        logger.error(f"Error generating charts: {str(e)}")
    
    return charts


def _generate_widget_chart(widget_data, report):
    """
    Generate a chart from widget data
    """
    try:
        # Create a temporary file for the chart
        chart_filename = f"chart_{uuid.uuid4()}.png"
        chart_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'charts', chart_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        
        # Generate chart based on widget type and data
        plt.figure(figsize=(10, 6))
        
        # This is a simplified chart generation - you would implement
        # specific chart types based on your widget configurations
        if widget_data.get('data'):
            # Example: Generate a simple bar chart
            data = widget_data['data']
            if isinstance(data, dict) and 'labels' in data and 'values' in data:
                plt.bar(data['labels'], data['values'])
                plt.title(widget_data['name'])
                plt.xticks(rotation=45)
                plt.tight_layout()
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    except Exception as e:
        logger.error(f"Error generating widget chart: {str(e)}")
        return None


def _generate_analysis_chart(analysis_data, report):
    """
    Generate a chart from analysis results
    """
    try:
        # Create a temporary file for the chart
        chart_filename = f"analysis_{uuid.uuid4()}.png"
        chart_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'charts', chart_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(chart_path), exist_ok=True)
        
        # Generate chart based on analysis results
        plt.figure(figsize=(10, 6))
        
        # This is a simplified implementation - you would implement
        # specific chart types based on your analysis results
        results = analysis_data.get('results', {})
        if results:
            # Example: Generate a simple plot
            plt.plot(range(len(results)), list(results.values()) if isinstance(results, dict) else [])
            plt.title(analysis_data['name'])
            plt.tight_layout()
        
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    except Exception as e:
        logger.error(f"Error generating analysis chart: {str(e)}")
        return None


def _generate_section_content(section, data, charts):
    """
    Generate content for a specific report section
    """
    section_content = {
        'id': str(section.id),
        'title': section.title,
        'type': section.section_type,
        'content': section.content,
        'order': section.order
    }
    
    # Add specific content based on section type
    if section.section_type == 'chart':
        # Find relevant charts for this section
        relevant_charts = [c for c in charts if c['title'].lower() in section.title.lower()]
        section_content['charts'] = relevant_charts
    
    elif section.section_type == 'table':
        # Generate table data
        section_content['table_data'] = _generate_table_data(section, data)
    
    elif section.section_type == 'insights':
        # Generate insights
        section_content['insights'] = _generate_section_insights(section, data)
    
    return section_content


def _generate_table_data(section, data):
    """
    Generate table data for a section
    """
    # This is a placeholder - implement based on your data structure
    return {
        'headers': ['Metric', 'Value', 'Change'],
        'rows': [
            ['Revenue', '$1,000,000', '+15%'],
            ['Profit', '$200,000', '+10%'],
            ['Customers', '5,000', '+25%']
        ]
    }


def _generate_section_insights(section, data):
    """
    Generate insights for a section
    """
    # This is a placeholder - implement AI-based insights generation
    return [
        "Revenue has increased by 15% compared to last quarter",
        "Customer acquisition rate is trending upward",
        "Profit margins have improved by 2 percentage points"
    ]


def _generate_ai_insights(data):
    """
    Generate AI-powered insights from the data
    """
    # This is a placeholder - implement AI insights generation
    # You would use your AI models here to analyze the data
    return [
        "Key trend: Revenue growth is accelerating",
        "Opportunity: Customer retention can be improved",
        "Risk: High customer acquisition costs"
    ]


def _generate_report_file(report, content):
    """
    Generate a file for the report in the specified format
    """
    if report.format == 'pdf':
        return _generate_pdf_report(report, content)
    elif report.format == 'excel':
        return _generate_excel_report(report, content)
    elif report.format == 'csv':
        return _generate_csv_report(report, content)
    elif report.format == 'powerpoint':
        return _generate_powerpoint_report(report, content)
    else:
        return _generate_html_report(report, content)


def _generate_pdf_report(report, content):
    """
    Generate a PDF report using ReportLab
    """
    if not HAS_REPORTING_LIBS:
        return None
    
    try:
        # Create filename
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2E86AB'),
            alignment=1  # Center alignment
        )
        story.append(Paragraph(content['title'], title_style))
        story.append(Spacer(1, 12))
        
        # Description
        if content.get('description'):
            story.append(Paragraph(content['description'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Executive Summary
        if content.get('executive_summary'):
            story.append(Paragraph('Executive Summary', styles['Heading2']))
            story.append(Paragraph(content['executive_summary'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Add sections
        for section in content.get('sections', []):
            # Section title
            story.append(Paragraph(section['title'], styles['Heading3']))
            
            # Section content based on type
            if section['type'] == 'chart' and section.get('charts'):
                for chart in section['charts']:
                    if os.path.exists(chart['path']):
                        # Add chart image
                        img = Image(chart['path'], width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 6))
            
            elif section['type'] == 'table' and section.get('table_data'):
                # Add table
                table_data = section['table_data']
                table = Table([table_data['headers']] + table_data['rows'])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                story.append(Spacer(1, 12))
            
            elif section['type'] == 'text' and section.get('content'):
                # Add text content
                if isinstance(section['content'], dict) and 'text' in section['content']:
                    story.append(Paragraph(section['content']['text'], styles['Normal']))
                    story.append(Spacer(1, 12))
        
        # Recommendations
        if content.get('recommendations'):
            story.append(Paragraph('Recommendations', styles['Heading2']))
            story.append(Paragraph(content['recommendations'], styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return file_path
    
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        return None


def _generate_excel_report(report, content):
    """
    Generate an Excel report
    """
    if not HAS_REPORTING_LIBS:
        return None
    
    try:
        # Create filename
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create Excel workbook
        workbook = xlsxwriter.Workbook(file_path)
        worksheet = workbook.add_worksheet('Report')
        
        # Add formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'bg_color': '#D3D3D3'
        })
        
        # Write title
        worksheet.write(0, 0, content['title'], title_format)
        
        # Write description
        if content.get('description'):
            worksheet.write(2, 0, 'Description:')
            worksheet.write(3, 0, content['description'])
        
        # Write executive summary
        if content.get('executive_summary'):
            worksheet.write(5, 0, 'Executive Summary:')
            worksheet.write(6, 0, content['executive_summary'])
        
        # Add data tables
        row = 8
        for section in content.get('sections', []):
            if section['type'] == 'table' and section.get('table_data'):
                table_data = section['table_data']
                
                # Write section title
                worksheet.write(row, 0, section['title'], header_format)
                row += 1
                
                # Write headers
                for col, header in enumerate(table_data['headers']):
                    worksheet.write(row, col, header, header_format)
                row += 1
                
                # Write data rows
                for data_row in table_data['rows']:
                    for col, value in enumerate(data_row):
                        worksheet.write(row, col, value)
                    row += 1
                
                row += 2  # Add space between tables
        
        workbook.close()
        
        return file_path
    
    except Exception as e:
        logger.error(f"Error generating Excel report: {str(e)}")
        return None


def _generate_csv_report(report, content):
    """
    Generate a CSV report
    """
    try:
        # Create filename
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Create CSV content
        csv_content = []
        
        # Add title and description
        csv_content.append([content['title']])
        if content.get('description'):
            csv_content.append(['Description:', content['description']])
        csv_content.append([])  # Empty row
        
        # Add table data from sections
        for section in content.get('sections', []):
            if section['type'] == 'table' and section.get('table_data'):
                table_data = section['table_data']
                
                # Add section title
                csv_content.append([section['title']])
                
                # Add headers
                csv_content.append(table_data['headers'])
                
                # Add data rows
                for row in table_data['rows']:
                    csv_content.append(row)
                
                csv_content.append([])  # Empty row
        
        # Write to file
        import csv
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_content)
        
        return file_path
    
    except Exception as e:
        logger.error(f"Error generating CSV report: {str(e)}")
        return None


def _generate_html_report(report, content):
    """
    Generate an HTML report
    """
    try:
        # Create filename
        filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = os.path.join(settings.MEDIA_ROOT, 'reports', 'exports', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Generate HTML content using Django template
        html_content = render_to_string('reports/report_template.html', {
            'report': report,
            'content': content
        })
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return file_path
    
    except Exception as e:
        logger.error(f"Error generating HTML report: {str(e)}")
        return None


def _generate_powerpoint_report(report, content):
    """
    Generate a PowerPoint report
    """
    # This would require python-pptx library
    # For now, return None as it's not implemented
    logger.warning("PowerPoint export not implemented")
    return None


def _calculate_next_generation(report):
    """
    Calculate the next generation time for a scheduled report
    """
    if not report.schedule_frequency:
        return None
    
    now = timezone.now()
    
    if report.schedule_frequency == 'daily':
        return now + timedelta(days=1)
    elif report.schedule_frequency == 'weekly':
        return now + timedelta(weeks=1)
    elif report.schedule_frequency == 'monthly':
        return now + timedelta(days=30)
    elif report.schedule_frequency == 'quarterly':
        return now + timedelta(days=90)
    elif report.schedule_frequency == 'annually':
        return now + timedelta(days=365)
    
    return None


def export_report(report, format_type):
    """
    Export a report in the specified format
    """
    if not report.content:
        raise ValueError("Report content not available")
    
    if format_type == 'pdf':
        return _generate_pdf_report(report, report.content)
    elif format_type == 'excel':
        return _generate_excel_report(report, report.content)
    elif format_type == 'csv':
        return _generate_csv_report(report, report.content)
    elif format_type == 'html':
        return _generate_html_report(report, report.content)
    elif format_type == 'powerpoint':
        return _generate_powerpoint_report(report, report.content)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


@shared_task
def cleanup_old_report_files():
    """
    Clean up old report files to save disk space
    """
    from .models import ReportExport
    
    # Delete export files older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    old_exports = ReportExport.objects.filter(created_at__lt=cutoff_date)
    
    for export in old_exports:
        if export.file_path and os.path.exists(export.file_path):
            try:
                os.remove(export.file_path)
                logger.info(f"Deleted old report file: {export.file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {export.file_path}: {str(e)}")
    
    # Delete the export records
    deleted_count = old_exports.delete()[0]
    logger.info(f"Cleaned up {deleted_count} old report exports")
    
    return {'deleted_count': deleted_count}


@shared_task
def schedule_report_generation():
    """
    Check for scheduled reports and generate them
    """
    from .models import Report
    
    # Find reports that are scheduled and due for generation
    now = timezone.now()
    due_reports = Report.objects.filter(
        is_scheduled=True,
        next_generation__lte=now,
        status__in=['completed', 'draft']
    )
    
    generated_count = 0
    for report in due_reports:
        try:
            generate_report.delay(report.id)
            generated_count += 1
            logger.info(f"Scheduled generation for report: {report.title}")
        except Exception as e:
            logger.error(f"Error scheduling report {report.id}: {str(e)}")
    
    return {'generated_count': generated_count}
