from .models import Repayment, Loan
from django.db import transaction
from datetime import datetime
from dateutil import relativedelta
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import LoanSerialzier, RepaymentSerialzier
from django.conf import settings
from django.utils.timezone import make_aware

class LoanViewSet(viewsets.ModelViewSet):
    """Views to carry out CRUD operations on loan and repayment tables in db"""
    
    settings.TIME_ZONE
    queryset = Loan.objects.all()
    serializer_class = LoanSerialzier


    def create(self, request, *args, **kwargs):
        """Add new loan and repayment details to db"""

        try:    
            # Use database transaction to group tasks together
            with transaction.atomic():
                loan_amount_int = int(request.data['loan_amount'])
                loan_term_int = int(request.data['loan_term'])
                interest_rate_float = float(request.data['interest_rate'])
                loan_month = request.data['loan_month']
                loan_year = int(request.data['loan_year'])

                new_loan = Loan(
                    loan_amount = loan_amount_int, 
                    loan_term = loan_term_int, 
                    interest_rate = interest_rate_float, 
                    loan_year = loan_year, 
                    loan_month = loan_month,
                    ) 
                new_loan.save()

                return handle_repayments(loan_amount_int, loan_term_int, interest_rate_float, loan_month, loan_year, new_loan)

        except Exception as err:
            print(str(err))
            return Response(str(err))


    def retrieve(self, request, *args, **kwargs):
        """Retrieve loan and repayment details from db"""

        try: 
            pk = kwargs['pk']
            loan_details = Loan.objects.get(id=pk)
            loan_serializer =  LoanSerialzier(loan_details).data
            repayment_details = Repayment.objects.filter(loan_id__id = pk)
            repayments_serializer = RepaymentSerialzier(repayment_details , many=True).data

            obj = {
            'loan': loan_serializer,
            'repayment list': repayments_serializer
            }

            return Response(obj)

        except Exception as err:
            print(str(err))
            return Response(str(err))


    def destroy(self, request, *args, **kwargs):
        """Remove repayment and loan details from db"""

        try:
            # Use database transaction to group tasks together
            with transaction.atomic():
                pk = kwargs['pk']
                repayment_list = Repayment.objects.filter(loan_id__id = pk)
                repayment_list.delete()

                loan_listing = Loan.objects.get(id=pk)
                loan_listing.delete()

                # Retrieve updated list
                loan_list = Loan.objects.all()
                loan_list_serializer = LoanSerialzier(loan_list, many=True).data
                return Response(loan_list_serializer)

        except Exception as err:
            print(str(err))
            return Response(str(err))


    def update(self, request, *args, **kwargs):
        """Update repayment and loan details in db"""

        try: 
            # Use database transaction to group tasks together
            with transaction.atomic():
                pk = kwargs['pk']
                # Remove previous repayment entries from db
                repayment_list = Repayment.objects.filter(loan_id__id = pk)
                repayment_list.delete()

                # Retrieve and update loan info
                loan_amount_int = int(request.data['loan_amount'])
                loan_term_int = int(request.data['loan_term'])
                interest_rate_float = float(request.data['interest_rate'])
                loan_month = request.data['loan_month']
                loan_year = int(request.data['loan_year'])

                Loan.objects.filter(id=pk).update(
                    loan_amount = loan_amount_int, 
                    loan_term = loan_term_int, 
                    interest_rate = interest_rate_float, 
                    loan_year = loan_year, 
                    loan_month = loan_month,
                    updated_at = make_aware(datetime.now())
                    )
                loan_details = Loan.objects.get(id=pk)

                # Calculate and update repayment details in db
                return handle_repayments(loan_amount_int, loan_term_int, interest_rate_float, loan_month, loan_year, loan_details)
        
        except Exception as err:
            print(str(err))
            return Response(str(err))


    @action(detail=True, methods=['GET'])
    def edit(self, request, *args, **kwargs):
        """Retrieve loan data to fill form for loan editing"""

        try:
            pk = kwargs['pk']
            queryset = Loan.objects.get(id=pk)
            loan_serializer =  LoanSerialzier(queryset).data
            return Response(loan_serializer)

        except Exception as err:
            print(str(err))
            return Response(str(err))


    @action(detail=False, methods=['GET'])
    def filter(self, request, *args, **kwargs):
        """Filter loans"""

        try:
            if request.GET['loan_amount_lower'] == 'null':
                loan_amount_lower = 1000 
            else:
                loan_amount_lower = int(request.GET['loan_amount_lower'])

            if request.GET['loan_amount_upper'] == 'null':
                loan_amount_upper = 100000000 
            else:
                loan_amount_upper = int(request.GET['loan_amount_upper'])

            if request.GET['loan_term_lower'] == 'null':
                loan_term_lower = 1 
            else:
                loan_term_lower = int(request.GET['loan_term_lower'])

            if request.GET['loan_term_upper'] == 'null':
                loan_term_upper = 50 
            else:
                loan_term_upper = int(request.GET['loan_term_upper'])

            if request.GET['interest_rate_lower'] == 'null':
                interest_rate_lower = 1.0
            else:
                interest_rate_lower = float(request.GET['interest_rate_lower'])

            if request.GET['interest_rate_upper'] == 'null':
                interest_rate_upper = 36.0
            else:
                interest_rate_upper = float(request.GET['interest_rate_upper'])

            filtered_list = Loan.objects.filter(
                loan_amount__gte=loan_amount_lower, 
                loan_amount__lte=loan_amount_upper, 
                loan_term__gte=loan_term_lower, 
                loan_term__lte=loan_term_upper, 
                interest_rate__gte=interest_rate_lower, 
                interest_rate__lte=interest_rate_upper, 
                )

            filtered_loans_serializer =  LoanSerialzier(filtered_list, many=True).data
            return Response(filtered_loans_serializer)

        except Exception as err:
                    print(str(err))
                    return Response(str(err))
    

def handle_repayments(loan_amount, loan_term, interest_rate_percentage, loan_month, loan_year, loan):
    """Calculate and store loan repayment schedule in db"""

    interest_rate = interest_rate_percentage / 100
    pmt = loan_amount * (interest_rate/12) / (1 - ((1 + (interest_rate/12)) ** (-12 * loan_term)))
    no_of_months = loan_term * 12
    global balance
    balance = loan_amount

    repayment_list = []
    for month in range(1, no_of_months + 1):
        monthly_repayment = calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month)
        repayment_list.append(monthly_repayment)

    Repayment.objects.bulk_create(repayment_list)
    loan_serializer =  LoanSerialzier(loan).data
    pk = loan_serializer['id']
    return Response(pk)

def calculate_repayment(interest_rate, pmt, loan, loan_month, loan_year, month):
    """Calculate monthly repayment schedule"""
    global balance
    monthly_interest = (interest_rate / 12) * balance
    principal = pmt - monthly_interest
    balance = balance - principal

    repayment = Repayment(
        loan = loan,
        payment_no = month,
        date =  datetime(loan_year, int(loan_month), 1) + relativedelta.relativedelta(months=month),
        payment_amount = pmt,
        principal = principal,
        interest = monthly_interest,
        balance = balance
    )
    return repayment