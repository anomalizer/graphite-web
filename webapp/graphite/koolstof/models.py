from django.db import models
from djorm_pgarray.fields import ArrayField
from djorm_expressions.models import ExpressionManager


class KoolstofMetricRegistry(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=-1)
    created_on = models.DateTimeField()
    active = models.BooleanField()
    step_in_seconds = models.IntegerField()

    class Meta:
        db_table = 'koolstof_metric_registry'
        managed = False


class KoolstofTimeseries(models.Model):
    metric_registry = models.ForeignKey(KoolstofMetricRegistry, primary_key=True)
    field_slots = models.IntegerField(db_column='_slots')  # Field renamed because it started with '_'.
    step_in_seconds = models.IntegerField(null=True, blank=True)
    field_version = models.IntegerField(db_column='_version')  # Field renamed because it started with '_'.
    tail_time = models.BigIntegerField()
    tail_ptr = models.IntegerField()
    measurements = ArrayField(dbtype="int", dimension=1)
    objects = ExpressionManager()

    class Meta:
        db_table = 'koolstof_timeseries'
        managed = False


class KoolstofFs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    parent = models.ForeignKey(''self'')
    depth = models.SmallIntegerField()
    path = models.CharField(max_length=-1)
    metric_registry = models.ForeignKey('KoolstofMetricRegistry', null=True, blank=True)
    class Meta:
        db_table = 'koolstof_fs'
