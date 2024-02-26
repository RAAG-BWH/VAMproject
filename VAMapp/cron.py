from django.utils import timezone
from .models import User

def clean_blacklist():
    present_datetime = timezone.now()
    DAYS_IN_BLACKLIST = 2
    datetime_threshold = present_datetime - timezone.timedelta(days=DAYS_IN_BLACKLIST)

    # get the records that are at least 2 days old
    records = User.objects.filter(last_date_connected__lt=datetime_threshold)

    # remove the old records from the blacklist
    records.delete()