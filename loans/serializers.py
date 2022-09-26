from rest_framework import serializers
from .models import LoanList, RepaymentSchedule

class LoanListSerialzier(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for loan list data"""

    class Meta:
        model = LoanList
        fields = '__all__'


class RepaymentScheduleSerialzier(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for repayment schedule data"""
    
    class Meta:
        model = RepaymentSchedule
        fields = '__all__'