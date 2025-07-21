from apscheduler.schedulers.background import BackgroundScheduler
from logger import logger

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Example scheduled job
def scheduled_report():
    logger.info('Scheduled report generated!')

# Add the job to the scheduler (runs every day at 8:00 AM)
scheduler.add_job(scheduled_report, 'cron', hour=8, minute=0)

def start_scheduler():
    """
    Starts the background scheduler.
    """
    scheduler.start() 