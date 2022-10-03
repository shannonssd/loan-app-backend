from loans.helper_functions import calculate_pmt
import pytest 


@pytest.mark.parametrize(
    "loan_amount,interest_rate,loan_term,expected_pmt",
    [
        (10000, 0.1, 1, 879.158872),
        (10000, 0.2, 2, 508.958026),
        (100000, 0.36, 10, 3088.991758),
    ]
)
def test_pmt_calculation(loan_amount, interest_rate, loan_term, expected_pmt):
    test_pmt = calculate_pmt(loan_amount, interest_rate, loan_term)
    test_pmt_rounded = round(test_pmt, 6)
    
    assert test_pmt_rounded == expected_pmt

