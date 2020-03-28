#This script is called daily by a cronjob to apply scheduled transactions.

from app.main.scheduled_tasks import apply_scheduled_trans

apply_scheduled_trans()