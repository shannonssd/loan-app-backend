from rest_framework.response import Response
from .models import Repayment
from .serializers import LoanSerialzier
from datetime import datetime
from dateutil import relativedelta

def calculate_pmt(loan_amount, interest_rate, loan_term):
    """Calculate PMT amount"""

    try:
        pmt = loan_amount * (interest_rate/12) / (1 - ((1 + (interest_rate/12)) ** (-12 * loan_term)))
        return pmt
    
    except Exception as err:
        print(str(err))
        return Response(err)


def calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month, dict):
    """Calculate monthly repayment schedule"""

    monthly_interest = (interest_rate / 12) * dict['balance']
    principal = pmt - monthly_interest
    dict['balance'] = dict['balance'] - principal

    repayment = Repayment(
        loan = loan,
        payment_no = month,
        date =  datetime(loan_year, int(loan_month), 1) + relativedelta.relativedelta(months=month),
        payment_amount = pmt,
        principal = principal,
        interest = monthly_interest,
        balance = dict['balance']
    )
    return repayment


def handle_repayments(loan_amount, loan_term, interest_rate_percentage, loan_month, loan_year, loan):
    """Calculate and store loan repayment schedule in db"""

    interest_rate = interest_rate_percentage / 100
    pmt = calculate_pmt(loan_amount, interest_rate, loan_term)
    no_of_months = loan_term * 12
    dict = {
        'balance': loan_amount,
    }

    repayment_list = []
    for month in range(1, no_of_months + 1):
        monthly_repayment = calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month, dict)
        repayment_list.append(monthly_repayment)

    Repayment.objects.bulk_create(repayment_list)
    loan_serializer =  LoanSerialzier(loan).data
    pk = loan_serializer['id']
    return Response(pk)