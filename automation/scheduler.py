"""
Scheduler - APScheduler setup and management
"""
import os
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Scheduler:
    """
    Task scheduler for PolyBiz AI
    Handles daily challenges, reminders, content posting, etc.
    """
    
    def __init__(self, async_mode: bool = True, db_url: str = None):
        """
        Initialize scheduler
        
        Args:
            async_mode: Use AsyncIOScheduler (for async apps) or BackgroundScheduler
            db_url: Database URL for job persistence
        """
        self.async_mode = async_mode
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///scheduler_jobs.db")
        
        # Configure job stores
        jobstores = {
            'default': SQLAlchemyJobStore(url=self.db_url)
        }
        
        # Configure executors
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(5)
        }
        
        # Job defaults
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 3600  # 1 hour grace period
        }
        
        # Create scheduler
        if async_mode:
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='Asia/Ho_Chi_Minh'
            )
        else:
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='Asia/Ho_Chi_Minh'
            )
        
        self._setup_default_jobs()
    
    def _setup_default_jobs(self):
        """Setup default scheduled jobs"""
        from .tasks import (
            generate_daily_challenge,
            send_daily_reminders,
            post_content_to_community,
            check_streaks,
            generate_weekly_report,
            cleanup_old_data
        )
        
        # Daily challenge - 6:00 AM Vietnam time
        self.add_job(
            generate_daily_challenge,
            trigger=CronTrigger(hour=6, minute=0),
            id='daily_challenge',
            name='Generate Daily Challenge',
            replace_existing=True
        )
        
        # Morning reminder - 8:00 AM
        self.add_job(
            send_daily_reminders,
            trigger=CronTrigger(hour=8, minute=0),
            id='morning_reminder',
            name='Send Morning Reminders',
            replace_existing=True
        )
        
        # Evening reminder - 8:00 PM
        self.add_job(
            send_daily_reminders,
            trigger=CronTrigger(hour=20, minute=0),
            id='evening_reminder',
            name='Send Evening Reminders',
            replace_existing=True,
            kwargs={'reminder_type': 'evening'}
        )
        
        # Content posting - 3 times a day
        for hour in [9, 14, 19]:  # 9 AM, 2 PM, 7 PM
            self.add_job(
                post_content_to_community,
                trigger=CronTrigger(hour=hour, minute=0),
                id=f'content_post_{hour}',
                name=f'Post Content at {hour}:00',
                replace_existing=True
            )
        
        # Check streaks - midnight
        self.add_job(
            check_streaks,
            trigger=CronTrigger(hour=0, minute=5),
            id='check_streaks',
            name='Check and Update Streaks',
            replace_existing=True
        )
        
        # Weekly report - Sunday 9 PM
        self.add_job(
            generate_weekly_report,
            trigger=CronTrigger(day_of_week='sun', hour=21, minute=0),
            id='weekly_report',
            name='Generate Weekly Report',
            replace_existing=True
        )
        
        # Cleanup old data - Sunday 3 AM
        self.add_job(
            cleanup_old_data,
            trigger=CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='cleanup',
            name='Cleanup Old Data',
            replace_existing=True
        )
        
        logger.info("✅ Default jobs configured")
    
    def add_job(self, func, trigger, id: str, name: str = None, **kwargs):
        """Add a job to the scheduler"""
        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=id,
            name=name or id,
            **kwargs
        )
        logger.info(f"📅 Added job: {name or id}")
    
    def remove_job(self, job_id: str):
        """Remove a job from the scheduler"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"🗑️ Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
    
    def pause_job(self, job_id: str):
        """Pause a specific job"""
        self.scheduler.pause_job(job_id)
        logger.info(f"⏸️ Paused job: {job_id}")
    
    def resume_job(self, job_id: str):
        """Resume a paused job"""
        self.scheduler.resume_job(job_id)
        logger.info(f"▶️ Resumed job: {job_id}")
    
    def run_job_now(self, job_id: str):
        """Run a job immediately"""
        job = self.scheduler.get_job(job_id)
        if job:
            job.func(*job.args, **job.kwargs)
            logger.info(f"⚡ Ran job immediately: {job_id}")
        else:
            logger.error(f"Job not found: {job_id}")
    
    def get_job_status(self) -> dict:
        """Get status of all jobs"""
        jobs = self.get_jobs()
        return {
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": str(job.next_run_time) if job.next_run_time else "Paused",
                    "trigger": str(job.trigger)
                }
                for job in jobs
            ]
        }


# Global scheduler instance
_scheduler = None

def get_scheduler(async_mode: bool = True) -> Scheduler:
    """Get or create global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler(async_mode=async_mode)
    return _scheduler
