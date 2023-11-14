from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def replace_prefix(field, prefix):
    html_output = field.field.widget.render(field.html_name, field.value(), attrs=field.field.widget.attrs).replace('__prefix__', str(prefix))
    return mark_safe(html_output)
