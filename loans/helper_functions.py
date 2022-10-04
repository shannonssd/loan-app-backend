from rest_framework.response import Response
from datetime import datetime
from dateutil import relativedelta

def calculate_pmt(loan_amount, interest_rate, loan_term):
    """Calculate PMT amount"""

    pmt = loan_amount * (interest_rate/12) / (1 - ((1 + (interest_rate/12)) ** (-12 * loan_term)))
    return pmt



def calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month, dict):
    """Calculate monthly repayment schedule"""

    monthly_interest = (interest_rate / 12) * dict['balance']
    principal = pmt - monthly_interest
    dict['balance'] = dict['balance'] - principal

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