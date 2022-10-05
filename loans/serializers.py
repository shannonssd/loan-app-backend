from rest_framework import serializers
from .models import Loan, Repayment

class LoanSerializer(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for loan list data"""

    class Meta:
        model = Loan
        fields = '__all__'

    def validate(self, data):
        """Validate fields before adding or modifying loans"""

        # Validate loan amount
        if (data.get('loan_amount') < 1000 or data.get('loan_amount') > 100000000):
            raise serializers.ValidationError(
            'Loan amount is not within the acceptable range of 1000 - 100,000,000 THB.'
            )

        # Validate loan term
        if (data.get('loan_term') < 1 or data.get('loan_term') > 50):
            raise serializers.ValidationError(
            'Loan term is not within the acceptable range of 1 - 50 years.'
            )

        # Validate interest rate
        if (data.get('interest_rate') < 1 or data.get('interest_rate') > 36):
            raise serializers.ValidationError(
            'Interest rate is not within the acceptable range of 1 - 36%.'
            )

        # Validate loan start date
        if (data.get('loan_year') < 2017 or data.get('loan_year') > 2050):
            raise serializers.ValidationError(
            'Loan start date is not within the acceptable range of 2017-2050.'
            )

        return data


class RepaymentSerializer(serializers.ModelSerializer):
    """Convert data between queryset and python dictionary data type for repayment schedule data"""
    
    class Meta:
        model = Repayment
        fields = '__all__'