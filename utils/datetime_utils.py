from datetime import date
import calendar

MONTHS= ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

def get_convenience_date_format(date=date.today()):
    day= str(date.day)
    month= get_month(date.month)
    year= str(date.year)

    return f'{month} {day} {year}'

def get_convenience_month_and_year(date):
    month= date.split('-')[0]
    year= date.split('-')[1]

    return f'{MONTHS[int(month)-1]}, {year}'

def extract_month_and_year(date=date.today()):
    month= date.month
    year= date.year

    return f'{month}-{year}'

def extract_day_month_and_year(date=date.today()):
    # print(type(date))
    day= date.day
    month= date.month
    year= date.year

    return f'{year}-{month}-{day}'

def get_month(month_index= 0):
    global MONTHS

    return MONTHS[month_index-1]

def get_today():
    return date.today()

def get_todays_day(date=date.today()):
    return calendar.day_name[date.weekday()]

def match_month_and_year(month_year, date2=date.today()):
    month, year= month_year.split('-')

    return True if (date2.month==int(month) and date2.year==int(year)) else False