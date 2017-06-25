import calendar
from django import template
from numpy import histogram

register = template.Library()


@register.filter
def sparkcounts(counts, bins=80):
    if len(counts) > bins:
        counts, edges = histogram(counts, bins=bins)

    return ",".join(map(str, counts))
