from rest_framework import serializers
from .models import Loan, Repayment

class LoanSerialzier(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for loan list data"""

    class Meta:
        model = Loan
        fields = '__all__'


class RepaymentSerialzier(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for repayment schedule data"""
    
    class Meta:
        model = Repayment
        fields = '__all__'