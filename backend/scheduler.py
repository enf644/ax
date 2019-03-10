"""Scheduler using APScheduller"""
import sys
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from loguru import logger
import backend.model as ax_model

this = sys.modules[__name__]
scheduler = None


async def prn_job(message):
    """Test function"""
    print('----------------' + str(message) + '---------------------')
    return False


def init_scheduler():
    """Initiate scheduller"""
    # TODO UTC must match timezone from config
    try:
        jobstores = {
            'default': SQLAlchemyJobStore(
                engine=ax_model.engine,
                tablename='_ax_scheduler_jobs'
            )
        }

        executors = {
            'default': AsyncIOExecutor()
        }

        this.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            timezone=pytz.timezone('Europe/Moscow'))
        this.scheduler.start()
        this.scheduler.remove_all_jobs()
        dt = datetime.now() + timedelta(seconds=5)
        moscow_dt = pytz.timezone('Europe/Moscow').localize(dt, is_dst=None)
        this.scheduler.add_job(
            prn_job,
            'date',
            run_date=moscow_dt,
            args=['SCHEDULER WORKS'],
            id='prn_job'
        )
    except Exception:
        logger.exception('Error initiating scheduler module. ')
        raise
