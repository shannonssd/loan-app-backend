from django.test import TestCase 
from loans.helper_functions import calculate_pmt


class CalculationTests(TestCase):
    """Test for calculations"""

    def test_pmt_calculation(self):
        """Test happy case for PMT calculation"""

        ### Is there a way to test multiple cases? ###
        loan_amount = 10000
        interest_rate = 0.1
        loan_term =  1
        expected_pmt = 879.158872

        test_pmt = calculate_pmt(loan_amount, interest_rate, loan_term)
        test_pmt_rounded = round(test_pmt, 6)
        
        # Check if calculated value is expected
        self.assertEqual(test_pmt_rounded, expected_pmt)


    

    