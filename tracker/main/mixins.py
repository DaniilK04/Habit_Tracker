from .models import *
from .forms import *

class TaskFilterMixin:
    form_class = TaskFilterForm

    def get_filtered_queryset(self, base_queryset):
        form = self.form_class(self.request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            if cd.get('search'):
                base_queryset = base_queryset.filter(title__icontains=cd['search'])
            if cd.get('status'):
                base_queryset = base_queryset.filter(status=cd['status'])
            if cd.get('sort'):
                base_queryset = base_queryset.order_by(cd['sort'])
        return base_queryset
