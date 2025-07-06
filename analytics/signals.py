from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DataSet, Analysis
from .tasks import process_dataset, run_analysis
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DataSet)
def process_dataset_signal(sender, instance, created, **kwargs):
    """
    Process dataset after upload
    """
    if created:
        logger.info(f"Processing dataset: {instance.name}")
        # Queue dataset processing task
        process_dataset.delay(instance.id)


@receiver(post_save, sender=Analysis)
def run_analysis_signal(sender, instance, created, **kwargs):
    """
    Run analysis after creation
    """
    if created and instance.status == 'queued':
        logger.info(f"Running analysis: {instance.name}")
        # Queue analysis task
        run_analysis.delay(instance.id)


@receiver(post_delete, sender=DataSet)
def cleanup_dataset_files(sender, instance, **kwargs):
    """
    Clean up files when dataset is deleted
    """
    if instance.file:
        try:
            instance.file.delete(save=False)
            logger.info(f"Deleted file for dataset: {instance.name}")
        except Exception as e:
            logger.error(f"Error deleting file for dataset {instance.name}: {e}")


@receiver(post_delete, sender=Analysis)
def cleanup_analysis_data(sender, instance, **kwargs):
    """
    Clean up analysis data when analysis is deleted
    """
    logger.info(f"Cleaning up analysis: {instance.name}")
    # Additional cleanup logic can be added here
