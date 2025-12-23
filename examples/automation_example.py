"""
Example: How to use the automation system
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automation import get_scheduler, generate_daily_challenge


def example_view_jobs():
    """View all scheduled jobs"""
    scheduler = get_scheduler(async_mode=False)
    
    print("\n📅 Scheduled Jobs:")
    status = scheduler.get_job_status()
    
    print(f"Total jobs: {status['total_jobs']}\n")
    
    for job in status["jobs"]:
        print(f"📌 {job['name']}")
        print(f"   ID: {job['id']}")
        print(f"   Next run: {job['next_run']}")
        print(f"   Trigger: {job['trigger']}")
        print()


def example_run_job_manually():
    """Run a job manually"""
    scheduler = get_scheduler(async_mode=False)
    
    print("\n⚡ Running daily challenge job manually...")
    
    # Run the job
    asyncio.run(generate_daily_challenge(language="en"))
    
    print("✅ Job completed!")


def example_add_custom_job():
    """Add a custom job"""
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = get_scheduler(async_mode=False)
    
    def my_custom_task():
        print("🔔 Custom task executed!")
    
    # Add job that runs every 30 minutes
    scheduler.add_job(
        my_custom_task,
        trigger=IntervalTrigger(minutes=30),
        id='custom_task',
        name='My Custom Task',
        replace_existing=True
    )
    
    print("✅ Custom job added!")


def example_pause_resume_job():
    """Pause and resume a job"""
    scheduler = get_scheduler(async_mode=False)
    
    # Pause
    print("\n⏸️ Pausing morning reminder...")
    scheduler.pause_job('morning_reminder')
    
    # Check status
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id == 'morning_reminder':
            print(f"   Status: {'Paused' if job.next_run_time is None else 'Active'}")
    
    # Resume
    print("\n▶️ Resuming morning reminder...")
    scheduler.resume_job('morning_reminder')


if __name__ == "__main__":
    print("=" * 60)
    print("PolyBiz AI - Automation Examples")
    print("=" * 60)
    
    print("\n1️⃣ Viewing scheduled jobs...")
    example_view_jobs()
    
    print("\n2️⃣ Adding custom job...")
    example_add_custom_job()
    
    print("\n3️⃣ Pause/Resume example...")
    example_pause_resume_job()
    
    print("\n4️⃣ Running job manually...")
    # Uncomment to test (requires AI API keys)
    # example_run_job_manually()
    
    print("\n" + "=" * 60)
    print("✅ Examples complete!")
    print("=" * 60)
