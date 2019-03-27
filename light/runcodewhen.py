import datetime
from datetime import datetime

import os
def DaysInMonth():
    from calendar import monthrange    
    year = datetime.now().strftime('%Y')
    month = datetime.now().strftime('%m').strip('0')
    days_in_month = monthrange(int(year), int(month))
    return days_in_month[1]

rebootday = datetime.now().strftime('%d %I:%M %p'))
days_in_month = str(DaysInMonth())
if rebootday == days_in_month+' 12:00 AM':
    os.system('sudo reboot')
