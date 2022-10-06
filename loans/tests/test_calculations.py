from django.test import TestCase 
from loans.helper_functions import calculate_pmt, calculate_repayment
from loans.serializers import LoanSerializer
from loans.models import Loan
from datetime import datetime


class CalculationTests(TestCase):
    """Tests for calculations"""


    def test_calculate_pmt(self):
        """Test happy cases for PMT calculation"""

        test_cases = (
            {'loan_amount': 10000, 'interest_rate': 0.1, 'loan_term': 1, 'expected_pmt': 879.158872},
            {'loan_amount': 10000, 'interest_rate': 0.2, 'loan_term': 2, 'expected_pmt': 508.958026},
            {'loan_amount': 100000, 'interest_rate': 0.36, 'loan_term': 10, 'expected_pmt': 3088.991758},
        )

        for test_case in test_cases:
            with self.subTest():
                test_pmt = calculate_pmt(test_case['loan_amount'], test_case['interest_rate'], test_case['loan_term'])
        
                # Check if calculated value is as expected
                self.assertEqual(test_pmt, test_case['expected_pmt'])


    def test_calculate_pmt_error(self):
        """Test edge cases for PMT calculation"""

        test_cases = (
            # Non-numeric string - 'loan_amount'
            {'loan_amount': '10 thousand', 'interest_rate': 0.1, 'loan_term': 1, 'expected_pmt': 879.158872},
            # Empty string - 'loan_term'
            {'loan_amount': 10000, 'interest_rate': 0.1, 'loan_term': '', 'expected_pmt': 508.958026},
            # Missing field - 'interest_rate'
            {'loan_amount': 100000, 'loan_term': 10, 'expected_pmt': 3088.991758},
        )

        for test_case in test_cases:
            with self.subTest():
                # Check if error is raised as expected
                with self.assertRaises(Exception):
                    calculate_pmt(test_case['loan_amount'], test_case['interest_rate'], test_case['loan_term'])


    def test_calculate_repayment(self):
        """Test happy cases for repayment calculation"""
  
        # Add test loan to db
        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = '01',
            )   
        new_loan.save()

        # Serialize loan to pass to calculate_repayment function
        serialized_loan = LoanSerializer(new_loan).data

        test_cases = (
            {
                # 1 / 12 repayment
                'interest_rate': 0.1, 'pmt': 879.158872, 'serialized_loan': serialized_loan, 'loan_month': '01', 'loan_year': 2022, 'month': 1, 'dict': {'balance': 10000}, 'no_of_months': 12, 
                'expected_repayment': {
                    'loan': serialized_loan,
                    'payment_no': 1,
                    'date':  datetime(2022, 2, 1),
                    'payment_amount': 879.158872,
                    'principal': 795.825539,
                    'interest': 83.333333,
                    'balance': 9204.174461,
                }
            },
            {
                # 2 / 12 repayment
                'interest_rate': 0.1, 'pmt': 879.158872, 'serialized_loan': serialized_loan, 'loan_month': '01', 'loan_year': 2022, 'month': 2, 'dict': {'balance': 9204.174461}, 'no_of_months': 12, 
                'expected_repayment': {
                    'loan': serialized_loan,
                    'payment_no': 2,
                    'date':  datetime(2022, 3, 1),
                    'payment_amount': 879.158872,
                    'principal': 802.457418,
                    'interest': 76.701454,
                    'balance': 8401.717043,
                }
            },
        )

        for test_case in test_cases:
            with self.subTest():
                test_repayment = calculate_repayment(test_case['interest_rate'], test_case['pmt'], test_case['serialized_loan'], test_case['loan_month'], test_case['loan_year'], test_case['month'], test_case['dict'], test_case['no_of_months'])
        
                # Check if calculated value is as expected
                self.assertEqual(test_repayment, test_case['expected_repayment'])
    

    def test_calculate_repayment_error(self):
        """Test edge cases for repayment calculation"""
  
        # Add test loan to db
        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = '01',
            )   
        new_loan.save()

        # Serialize loan to pass to calculate_repayment function
        serialized_loan = LoanSerializer(new_loan).data

        test_cases = (
            # Missing field - 'loan_month'
            { 'interest_rate': 0.1, 'pmt': 879.158872, 'serialized_loan': serialized_loan, 'loan_year': 2022, 'month': 1, 'dict': {'balance': 10000}, 'no_of_months': 12 },
            # TypeError: string instead of integer - 'interest_rate'
            { 'interest_rate': '0.1', 'pmt': 879.158872, 'serialized_loan': serialized_loan, 'loan_month': '01', 'loan_year': 2022, 'month': 2, 'dict': {'balance': 9204.174461}, 'no_of_months': 12, }
        )

        for test_case in test_cases:
            with self.subTest():
                # Check if error is raised as expected
                with self.assertRaises(Exception):
                    calculate_repayment(test_case['interest_rate'], test_case['pmt'], test_case['serialized_loan'], test_case['loan_month'], test_case['loan_year'], test_case['month'], test_case['dict'], test_case['no_of_months'])
