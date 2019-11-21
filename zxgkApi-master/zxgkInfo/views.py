import os
from datetime import timedelta
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from django.db.models import Q
from .serializers import *
from .filters import *
from .models import Person
from django_filters.rest_framework import DjangoFilterBackend
from .zxgk import get_captche_id, zxgk_list


class PersonViewSet(GenericViewSet, ListModelMixin):
    serializer_class = PersonSerializer
    filter_class = PersonFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        sign = self.spider()
        if sign == '1':
            return Person.objects.all()

    def spider(self):
        today = date.today()
        pname = self.request.query_params.get('pname')
        cardnum = self.request.query_params.get('cardnum')

        if os.path.exists('captcha.jpg'):
            os.remove('captcha.jpg')

        if not pname:
            pname = '无'

        if Person.objects.filter(Q(cardNum=cardnum) & Q(iname=pname)) and \
                today - Person.objects.filter(cardNum=cardnum)[0].addTime < \
                timedelta(days=15):

            return '1'
        else:
            Person.objects.update_or_create(cardNum=cardnum, iname=pname, defaults={"addTime":today})
            captcheid = get_captche_id()
            zxgk_list(cardnum, captcheid)

            return '1'
