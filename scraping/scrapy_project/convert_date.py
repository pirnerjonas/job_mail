from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def convert_date(text_input, asString=True):
    """ Converts the date from a relative timespan to a date.
        Linkedin shows information about when they posted the job (e.g. Vor 20 Stunden).
    """
    try:
        now = datetime.now()
        # 4 hours ago to ['4','hours','ago']
        time_list = text_input.split()
        # go through all found cases; maybe there are some that I havent considered
        # find() results in -1 if it doesnt find a result
        if time_list[2].lower().find('minute')!=-1:
            diff = timedelta(minutes=int(time_list[1]))
        elif time_list[2].lower().find('sekunde')!=-1:
            diff = timedelta(seconds=int(time_list[1]))
        elif time_list[2].lower().find('stunde')!=-1:
            diff = timedelta(hours=int(time_list[1]))
        elif time_list[2].lower().find('tag')!=-1:
            diff = timedelta(days=int(time_list[1]))
        elif time_list[2].lower().find('woche')!=-1:
            diff = timedelta(weeks=int(time_list[1]))
        elif time_list[2].lower().find('monat')!=-1:
            diff = relativedelta(months=int(time_list[1]))
        # actual time minus the the time passed is the post date
        date = now - diff 

        if asString==True:
            return str(date)
        else:
            return date

    # if conversion fails
    except:
        return None