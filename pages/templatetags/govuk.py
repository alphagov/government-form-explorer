import calendar
from django import template

register = template.Library()


@register.filter(is_safe=False)
def govuk_date(date):
    print(date)
    year = date[:4]
    month = date[4:6]
    name = calendar.month_name[int(month)][:3]
    return '<time datetime="%s-%s">%s %s</time>' % (year, month, name, year)
