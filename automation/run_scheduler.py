"""
Run the scheduler as a standalone service
"""
import signal
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from automation import get_scheduler


def main():
    """Run the scheduler"""
    print("=" * 60)
    print("PolyBiz AI - Task Scheduler")
    print("=" * 60)
    
    # Initialize scheduler
    scheduler = get_scheduler(async_mode=False)  # Use sync mode for standalone
    
    # Display scheduled jobs
    print("\n📅 Scheduled Jobs:")
    status = scheduler.get_job_status()
    for job in status["jobs"]:
        print(f"  • {job['name']}")
        print(f"    Next run: {job['next_run']}")
        print(f"    Trigger: {job['trigger']}")
        print()
    
    # Handle shutdown gracefully
    def shutdown(signum, frame):
        print("\n🛑 Shutting down scheduler...")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    
    # Start scheduler
    print("🚀 Starting scheduler...")
    scheduler.start()
    
    print("✅ Scheduler is running. Press Ctrl+C to stop.")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    main()
