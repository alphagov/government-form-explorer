import calendar
from django import template

register = template.Library()


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
