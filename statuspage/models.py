from django.db import models
from django.utils import timezone

from model_utils.models import TimeStampedModel


SERVICE_STATUSES = (
    (0, 'Operational'),
    (1, 'Performance issues'),
    (2, 'Partial outage'),
    (3, 'Major outage'),
)


class ServiceManager(models.Manager):
    def worst_status(self):
        s = self.get_queryset().aggregate(models.Max('status'))["status__max"]
        return s


class Service(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    href = models.URLField(blank=True)
    status = models.IntegerField(choices=SERVICE_STATUSES)
    groups = models.ManyToManyField('ServiceGroup',
                                    related_name='services',
                                    related_query_name='service')
    objects = ServiceManager()

    def __str__(self):
        return self.name


class ServiceGroup(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)

    def worst_service(self):
        return self.services.all().latest('status')

    def __str__(self):
        return self.name


INCIDENT_STATUSES = (
    (0, "Investigating"),
    (1, "Identified"),
    (2, "Watching"),
    (3, "Fixed"),
)


class IncidentManager(models.Manager):
    def occurred_in_last_n_days(self, days=7):
        threshold = timezone.now() - timezone.timedelta(days=days)
        qs = self.get_queryset().filter(occurred__date__gte=threshold.date())
        return qs


class Incident(TimeStampedModel):
    name = models.CharField(max_length=255)
    service = models.ForeignKey('Service', blank=True, null=True)
    status = models.IntegerField(choices=INCIDENT_STATUSES)
    description = models.TextField()
    occurred = models.DateTimeField(default=timezone.now)
    objects = IncidentManager()

    def __str__(self):
        return self.name
