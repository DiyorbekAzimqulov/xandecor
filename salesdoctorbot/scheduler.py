from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events
import logging
import time
from salesdoctorbot.report_tasks import (
    daily_shipping_report,
    daily_redistribute_report,
    daily_forgotten_shipments,
    daily_discount_event
)

logger = logging.getLogger(__name__)

def start():
    try:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        """Reports for the current day"""
        # Schedule the daily shipping report
        scheduler.add_job(
            daily_shipping_report,
            trigger=CronTrigger(hour=7, minute=00),  # Runs daily at 7:00 AM
            id="Daily Shipping Report",
            max_instances=1,
            replace_existing=True,
        )

        # Schedule the daily redistribute report
        scheduler.add_job(
            daily_redistribute_report,
            trigger=CronTrigger(hour=7, minute=10),  # Runs daily at 8:00 AM
            id="Daily Redistribute Report",
            max_instances=1,
            replace_existing=True,
        )

        # Schedule the daily forgotten shipments report
        scheduler.add_job(
            daily_forgotten_shipments,
            trigger=CronTrigger(hour=7, minute=15),  # Runs daily at 9:00 AM
            id="Daily Forgotten Shipments",
            max_instances=1,
            replace_existing=True,
        )
        """Reports for the next day"""
        # Schedule shipping report for the next day
        scheduler.add_job(
            daily_shipping_report,
            trigger=CronTrigger(hour=21, minute=5),  # Runs daily at 21:05 PM
            id="Daily Shipping Report 2 for the next day",
            max_instances=1,
            replace_existing=True,
        )

        # Schedule the daily redistribute report
        scheduler.add_job(
            daily_redistribute_report,
            trigger=CronTrigger(hour=21, minute=10),  # Runs daily at 21:10 PM
            id="Daily Redistribute Report 2 for the next day",
            max_instances=1,
            replace_existing=True,
        )

        # Schedule the daily forgotten shipments report
        scheduler.add_job(
            daily_forgotten_shipments,
            trigger=CronTrigger(hour=21, minute=15),  # Runs daily at 21:15 PM
            id="Daily Forgotten Shipments 2 for the next day",
            max_instances=1,
            replace_existing=True,
        )

        """Discount events"""
        # Schedule the daily discount morning event
        scheduler.add_job(
            daily_discount_event,
            trigger=CronTrigger(hour=10, minute=00),  # Runs daily at 10:00 AM
            id="Daily Discount Morning Event",
            max_instances=1,
            replace_existing=True,
        )
        
        # Schedule the daily discount afternoon event
        scheduler.add_job(
            daily_discount_event,
            trigger=CronTrigger(hour=14, minute=0),  # Runs daily at 2:00 PM
            id="Daily Discount Afternoon Event",
            max_instances=1,
            replace_existing=True,
        )

        register_events(scheduler)
        scheduler.start()
        logger.info("Scheduler started successfully.")
        
        while True:
            time.sleep(1)
    except Exception as e:
        logger.error("Failed to start scheduler: %s", e)
