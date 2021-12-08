from django.views.generic.detail import SingleObjectMixin
from .models import Category


class CategoryDetailMixin(SingleObjectMixin):  # SingleObjectMixin - father of all views

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.get_categoties_for_sidebar()
        return context
