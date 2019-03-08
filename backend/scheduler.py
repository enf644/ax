"""Scheduler using APScheduller"""
import sys
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

this = sys.modules[__name__]
scheduler = None

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///ax_sqllite.db')
}
# TODO make different stores for differents databases
# SQLAlchemyJobStore('mysql://root@localhost/mygola?charset=utf8&use_unicode=0')

executors = {
    'default': AsyncIOExecutor()
}

# TODO UTC must match timezone from config


async def tick_job():
    """Test function"""
    print('Tick! The time is: %s' % datetime.now())
    return False


async def prn_job(message):
    """Test function"""
    print('\n\n\n\n' + str(message) + '\n\n\n\n\n')
    return False


def init_scheduler():
    """Initiate scheduller"""
    this.scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        timezone=pytz.timezone('Europe/Moscow'))
    # this.scheduler.add_job(tick_job, 'interval', seconds=3, id='tick_job')
    this.scheduler.start()
    this.scheduler.remove_all_jobs()
    # moscow_dt = pytz.timezone(
    # 'Europe/Moscow').localize(datetime(2019, 3, 8, 23, 34, 0), is_dst=None)
    # this.scheduler.add_job(prn_job, 'date', run_date=moscow_dt, args=[
    #                        'text'], id='prn_job')
