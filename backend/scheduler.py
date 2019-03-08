"""Scheduler using APScheduller"""
import sys
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor


this = sys.modules[__name__]
scheduler = None

executors = {
    'default': AsyncIOExecutor()
}
# TODO add UTC  https://apscheduler.readthedocs.io/en/latest/userguide.html


async def tick():
    """Test function"""
    print('Tick! The time is: %s' % datetime.now())
    return False


def init_scheduler():
    """Initiate scheduller"""
    this.scheduler = AsyncIOScheduler(executors=executors)
    # this.scheduler = BackgroundScheduler()
    # this.scheduler.add_job(tick, 'interval', seconds=3)
    this.scheduler.start()
