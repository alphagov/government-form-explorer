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


def humansize(num):
    for unit in ['Bytes', 'Kilobytes', 'Megabytes', 'Gigabytes', 'Terabytes', 'Petabytes']:
        if abs(num) < 1024.0:
            return ("%3.1f" % num, unit)
        num /= 1024.0
    return ("%.1f%s" % num, unit[-1])


@register.filter
def humansize_value(num):
    return humansize(num)[0]


@register.filter
def humansize_unit(num):
    return humansize(num)[1]
