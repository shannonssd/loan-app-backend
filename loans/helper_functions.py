from rest_framework.response import Response
from datetime import datetime
from dateutil import relativedelta

def calculate_pmt(loan_amount, interest_rate, loan_term):
    """Calculate PMT amount"""

    pmt = round(loan_amount * (interest_rate/12) / (1 - ((1 + (interest_rate/12)) ** (-12 * loan_term))), 6)
    return pmt



def calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month, dict, total_no_months):
    """Calculate monthly repayment schedule"""

    monthly_interest = round((interest_rate / 12) * dict['balance'], 6)
    principal = round(pmt - monthly_interest, 6)
    if (month != total_no_months):
        dict['balance'] = round(dict['balance'] - principal, 6)
    else:
        dict['balance'] = 0


    repayment = {
        'loan': loan,
        'payment_no': month,
        'date':  datetime(loan_year, int(loan_month), 1) + relativedelta.relativedelta(months=month),
        'payment_amount': pmt,
        'principal': principal,
        'interest': monthly_interest,
        'balance': dict['balance']
    }
    return repayment