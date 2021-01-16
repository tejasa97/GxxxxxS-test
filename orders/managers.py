from django.db.models import Manager


class AscendingOrderManager(Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('order_id')
