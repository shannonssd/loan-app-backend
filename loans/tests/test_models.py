from django.test import TestCase 
from loans.models import Loan
from loans.serializers import LoanSerialzier

class ModelTests(TestCase):
    """Test for loan models"""

    def test_create_loan(self):
        """Test for adding new loan to db"""

        ### Is there a way to test multiple cases? ###
        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = '01',
            ) 
        new_loan.save()
        serializer = LoanSerialzier(new_loan).data

        # Check if data is successfully saved in db and if values are correct
        self.assertEqual(Loan.objects.count(), 1)        
        self.assertEqual(serializer['loan_amount'], '10000.000000')
        self.assertEqual(serializer['loan_term'], 1)