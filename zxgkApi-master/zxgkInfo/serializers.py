from rest_framework.serializers import ModelSerializer
from .models import *


class ShiXinSerializer(ModelSerializer):

    class Meta:
        model = ShiXin
        exclude = ('person', 'id')


class BzxrSerializer(ModelSerializer):

    class Meta:
        model = Bzxr
        exclude = ('person', 'id')


class XglSerializer(ModelSerializer):

    class Meta:
        model = Xgl
        exclude = ('person', 'id')


class ZhongBenSerializer(ModelSerializer):

    class Meta:
        model = ZhongBen
        exclude = ('person', 'id')


class PersonSerializer(ModelSerializer):
    sx = ShiXinSerializer(many=True)
    bzxr = BzxrSerializer(many=True)
    xg = XglSerializer(many=True)
    zb = ZhongBenSerializer(many=True)

    class Meta:
        model = Person
        exclude = ('addTime', 'id')

