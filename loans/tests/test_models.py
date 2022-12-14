from django.test import TestCase 
from loans.models import Loan, Repayment
from loans.serializers import LoanSerializer, RepaymentSerializer
from decimal import Decimal


class ModelTests(TestCase):
    """Test for loan models"""


    def test_create_loan(self):
        """Test for adding new loan to db"""

        test_cases = (
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2022, 'loan_month': '01',},
            {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',},
        )

        for test_case in test_cases:
            with self.subTest():

                new_loan = Loan(
                    loan_amount = test_case['loan_amount'], 
                    loan_term = test_case['loan_term'], 
                    interest_rate = test_case['interest_rate'], 
                    loan_year = test_case['loan_year'], 
                    loan_month = test_case['loan_month'],
                ) 
                new_loan.save()
                serializer = LoanSerializer(new_loan).data

                # Check if values are as expected
                self.assertEqual(serializer['loan_amount'], test_case['loan_amount'])
                self.assertEqual(serializer['loan_term'], test_case['loan_term'])
                self.assertEqual(serializer['interest_rate'], test_case['interest_rate'])
                self.assertEqual(serializer['loan_year'], test_case['loan_year'])
                self.assertEqual(serializer['loan_month'], test_case['loan_month'])


    def test_create_repayment(self):
        """Test for adding repayments to db"""

        test_cases = (
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2022, 'loan_month': '01', 'payment_no': 1, 'date': '2022-2-1', 'payment_amount': round(Decimal(879.158872), 6), 'principal': round(Decimal(795.825539), 6), 'interest': round(Decimal(83.333333), 6), 'balance': round(Decimal(9204.174461), 6), 'expected_db_count': 1,},
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2022, 'loan_month': '01', 'payment_no': 2, 'date': '2022-3-1', 'payment_amount': round(Decimal(879.158872), 6), 'principal': round(Decimal(802.457418), 6), 'interest': round(Decimal(76.701454), 6), 'balance': round(Decimal(8401.717043), 6), 'expected_db_count': 2,},
        )

        for test_case in test_cases:
            with self.subTest():
                
                # Add test loan to db
                new_loan = Loan(
                    loan_amount = test_case['loan_amount'], 
                    loan_term = test_case['loan_term'], 
                    interest_rate = test_case['interest_rate'], 
                    loan_year = test_case['loan_year'], 
                    loan_month = test_case['loan_month'],
                    ) 
                new_loan.save()
                serializer = LoanSerializer(new_loan).data

                new_repayment = Repayment(
                    loan = new_loan,
                    payment_no = test_case['payment_no'],
                    date = test_case['date'],
                    payment_amount = test_case['payment_amount'],
                    principal = test_case['principal'],
                    interest = test_case['interest'],
                    balance = test_case['balance'],
                )
                new_repayment.save()
                repayment_serializer = RepaymentSerializer(new_repayment).data

                # Check if data is successfully saved in db 
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])        
                # Check if foreign key value is as expected
                self.assertEqual(repayment_serializer['loan'], serializer['id'] )
                # Check if values are as expected
                self.assertEqual(repayment_serializer['payment_no'], test_case['payment_no'])
                self.assertEqual(repayment_serializer['date'], test_case['date'])
                self.assertEqual(repayment_serializer['payment_amount'], test_case['payment_amount'])
                self.assertEqual(repayment_serializer['principal'], test_case['principal'])
                self.assertEqual(repayment_serializer['interest'], test_case['interest'])
                self.assertEqual(repayment_serializer['balance'], test_case['balance'])