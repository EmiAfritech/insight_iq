from celery import shared_task
from django.core.files.storage import default_storage
from django.utils import timezone
import pandas as pd
import numpy as np
import json
import logging
from .models import DataSet, Analysis, Chart, Insight
from .utils import DataProcessor, AnalysisEngine, ChartGenerator, InsightGenerator

logger = logging.getLogger(__name__)


@shared_task
def process_dataset(dataset_id):
    """
    Process uploaded dataset
    """
    try:
        dataset = DataSet.objects.get(id=dataset_id)
        dataset.status = 'processing'
        dataset.save()
        
        # Process the file
        processor = DataProcessor()
        result = processor.process_file(dataset.file.path)
        
        # Update dataset with processed information
        dataset.total_rows = result['total_rows']
        dataset.total_columns = result['total_columns']
        dataset.columns_info = result['columns_info']
        dataset.status = 'ready'
        dataset.save()
        
        logger.info(f"Successfully processed dataset: {dataset.name}")
        return f"Dataset {dataset.name} processed successfully"
        
    except DataSet.DoesNotExist:
        logger.error(f"Dataset with id {dataset_id} not found")
        return f"Dataset with id {dataset_id} not found"
    except Exception as e:
        logger.error(f"Error processing dataset {dataset_id}: {str(e)}")
        try:
            dataset = DataSet.objects.get(id=dataset_id)
            dataset.status = 'error'
            dataset.error_message = str(e)
            dataset.save()
        except:
            pass
        return f"Error processing dataset: {str(e)}"


@shared_task
def run_analysis(analysis_id):
    """
    Run analysis on dataset
    """
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'running'
        analysis.save()
        
        start_time = timezone.now()
        
        # Load dataset
        dataset = analysis.dataset
        processor = DataProcessor()
        df = processor.load_dataset(dataset.file.path)
        
        # Run analysis
        engine = AnalysisEngine()
        results = engine.run_analysis(
            df, 
            analysis.analysis_type, 
            analysis.configuration,
            analysis.selected_columns
        )
        
        # Generate charts
        chart_generator = ChartGenerator()
        charts = chart_generator.generate_charts(
            df, 
            analysis.analysis_type, 
            results,
            analysis.selected_columns
        )
        
        # Generate insights
        insight_generator = InsightGenerator()
        insights = insight_generator.generate_insights(
            df,
            analysis.analysis_type,
            results,
            charts
        )
        
        # Save results
        analysis.results = results
        analysis.charts = charts
        analysis.insights = insights
        analysis.status = 'completed'
        analysis.execution_time = (timezone.now() - start_time).total_seconds()
        analysis.save()
        
        # Create chart objects
        for chart_data in charts:
            Chart.objects.create(
                analysis=analysis,
                name=chart_data['name'],
                description=chart_data.get('description', ''),
                chart_type=chart_data['type'],
                data=chart_data['data'],
                configuration=chart_data.get('config', {})
            )
        
        # Create insight objects
        for insight_data in insights:
            Insight.objects.create(
                analysis=analysis,
                title=insight_data['title'],
                description=insight_data['description'],
                insight_type=insight_data['type'],
                confidence_score=insight_data.get('confidence', 0.0),
                importance_score=insight_data.get('importance', 0.0),
                supporting_data=insight_data.get('data', {})
            )
        
        # Generate AI summary and recommendations
        generate_ai_insights.delay(analysis_id)
        
        logger.info(f"Successfully completed analysis: {analysis.name}")
        return f"Analysis {analysis.name} completed successfully"
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis with id {analysis_id} not found")
        return f"Analysis with id {analysis_id} not found"
    except Exception as e:
        logger.error(f"Error running analysis {analysis_id}: {str(e)}")
        try:
            analysis = Analysis.objects.get(id=analysis_id)
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.save()
        except:
            pass
        return f"Error running analysis: {str(e)}"


@shared_task
def generate_ai_insights(analysis_id):
    """
    Generate AI-powered insights and recommendations
    """
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        
        # Generate AI summary
        insight_generator = InsightGenerator()
        ai_summary = insight_generator.generate_ai_summary(analysis)
        ai_insights = insight_generator.generate_ai_insights(analysis)
        ai_recommendations = insight_generator.generate_ai_recommendations(analysis)
        
        # Update analysis with AI content
        analysis.ai_summary = ai_summary
        analysis.ai_insights = ai_insights
        analysis.ai_recommendations = ai_recommendations
        analysis.save()
        
        logger.info(f"Generated AI insights for analysis: {analysis.name}")
        return f"AI insights generated for analysis {analysis.name}"
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis with id {analysis_id} not found")
        return f"Analysis with id {analysis_id} not found"
    except Exception as e:
        logger.error(f"Error generating AI insights for analysis {analysis_id}: {str(e)}")
        return f"Error generating AI insights: {str(e)}"


@shared_task
def cleanup_old_datasets():
    """
    Clean up old datasets and analyses
    """
    try:
        # Delete datasets older than 90 days (configurable)
        cutoff_date = timezone.now() - timezone.timedelta(days=90)
        old_datasets = DataSet.objects.filter(created_at__lt=cutoff_date)
        
        count = 0
        for dataset in old_datasets:
            # Delete associated file
            if dataset.file:
                try:
                    dataset.file.delete(save=False)
                except:
                    pass
            dataset.delete()
            count += 1
        
        logger.info(f"Cleaned up {count} old datasets")
        return f"Cleaned up {count} old datasets"
        
    except Exception as e:
        logger.error(f"Error cleaning up old datasets: {str(e)}")
        return f"Error cleaning up old datasets: {str(e)}"


@shared_task
def generate_dataset_sample(dataset_id, sample_size=1000):
    """
    Generate sample data for dataset preview
    """
    try:
        dataset = DataSet.objects.get(id=dataset_id)
        
        processor = DataProcessor()
        df = processor.load_dataset(dataset.file.path)
        
        # Generate sample
        sample_df = df.head(sample_size)
        sample_data = sample_df.to_dict('records')
        
        # Store sample in cache or database
        # Implementation depends on caching strategy
        
        logger.info(f"Generated sample for dataset: {dataset.name}")
        return f"Sample generated for dataset {dataset.name}"
        
    except DataSet.DoesNotExist:
        logger.error(f"Dataset with id {dataset_id} not found")
        return f"Dataset with id {dataset_id} not found"
    except Exception as e:
        logger.error(f"Error generating sample for dataset {dataset_id}: {str(e)}")
        return f"Error generating sample: {str(e)}"


@shared_task
def export_analysis_results(analysis_id, export_format='json'):
    """
    Export analysis results to various formats
    """
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        
        # Prepare export data
        export_data = {
            'analysis': {
                'name': analysis.name,
                'type': analysis.analysis_type,
                'created_at': analysis.created_at.isoformat(),
                'execution_time': analysis.execution_time,
            },
            'dataset': {
                'name': analysis.dataset.name,
                'rows': analysis.dataset.total_rows,
                'columns': analysis.dataset.total_columns,
            },
            'results': analysis.results,
            'charts': analysis.charts,
            'insights': analysis.insights,
            'ai_summary': analysis.ai_summary,
            'ai_insights': analysis.ai_insights,
            'ai_recommendations': analysis.ai_recommendations,
        }
        
        # Export based on format
        if export_format == 'json':
            filename = f"analysis_{analysis.id}.json"
            with open(f'/tmp/{filename}', 'w') as f:
                json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported analysis results: {analysis.name}")
        return f"Analysis results exported: {filename}"
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis with id {analysis_id} not found")
        return f"Analysis with id {analysis_id} not found"
    except Exception as e:
        logger.error(f"Error exporting analysis results {analysis_id}: {str(e)}")
        return f"Error exporting analysis results: {str(e)}"
