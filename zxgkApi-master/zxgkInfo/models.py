from django.db import models
from datetime import date


class Person(models.Model):
    cardNum = models.CharField(max_length=20)
    iname = models.CharField(max_length=8)
    addTime = models.DateField(default=date.today)

    class Meta:
        unique_together = ['cardNum', 'iname']


class ShiXin(models.Model):
    person = models.ForeignKey(Person, null=True, related_name='sx', on_delete=models.SET_NULL)
    areaName = models.CharField(max_length=32)
    sexy = models.CharField(max_length=8)
    caseCode = models.CharField(max_length=64)
    courtName = models.CharField(max_length=32)
    disruptTypeName = models.CharField(max_length=64)
    duty = models.TextField()
    gistId = models.CharField(max_length=32)
    gistUnit = models.CharField(max_length=32)
    performance = models.CharField(max_length=32)
    publishDate = models.CharField(max_length=32)
    regDate = models.CharField(max_length=32)


class Bzxr(models.Model):
    person = models.ForeignKey(Person, null=True, related_name='bzxr', on_delete=models.SET_NULL)
    courtName = models.CharField(max_length=32)
    sexy = models.CharField(max_length=8)
    regDate = models.CharField(max_length=32)
    caseCode = models.CharField(max_length=64)
    execMoney = models.CharField(max_length=16)


class Xgl(models.Model):
    person = models.ForeignKey(Person, null=True, related_name='xg', on_delete=models.SET_NULL)
    courtName = models.CharField(max_length=32)
    sexy = models.CharField(max_length=8)
    regDate = models.CharField(max_length=32)
    caseCode = models.CharField(max_length=64)
    areaName = models.CharField(max_length=32)


class ZhongBen(models.Model):
    person = models.ForeignKey(Person, null=True, related_name='zb', on_delete=models.SET_NULL)
    caseCode = models.CharField(max_length=64)
    sexy = models.CharField(max_length=8)
    regDate = models.CharField(max_length=32)
    courtName = models.CharField(max_length=32)
    execMoney = models.CharField(max_length=16)
    finalDate = models.CharField(max_length=32)
    unperformMoney = models.CharField(max_length=16)
