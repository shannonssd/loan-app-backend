from django.db import models

class LoanList(models.Model):
    """Database model for individual loans"""
    
    loan_amount = models.DecimalField(max_digits=21, decimal_places=6)
    loan_term = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=21, decimal_places=6)
    loan_month = models.CharField(max_length=2)
    loan_year = models.IntegerField()
    # Automatically set the field to now when the object is first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically set the field to now every time the object is saved.
    updated_at = models.DateTimeField(auto_now=True)

    # Check if values are valid for individual fields
    class Meta:
        constraints = [
          models.CheckConstraint(
            check = models.Q(loan_amount__gte=1000) & models.Q(loan_amount__lte=100000000),
            name="Loan amount is valid between 1000 and 100,000,000 THB",
          ), 
          models.CheckConstraint(
            check = models.Q(loan_term__gte=1) & models.Q(loan_term__lte=50),
            name="Loan term is valid between 1 and 50 years",
          ), 
          models.CheckConstraint(
            check = models.Q(loan_year__gte=2017) & models.Q(loan_year__lte=2050),
            name="Start date is valid between Jan 2017 - Dec 2050",
          ), 
          models.CheckConstraint(
            check = models.Q(interest_rate__gte=1) & models.Q(interest_rate__lte=36),
            name="Interest rate is valid between 1 and 36 percent",
          ),
        ]

class RepaymentSchedule(models.Model):
    """Database model for loan repayment schedule"""

    loan = models.ForeignKey(LoanList, on_delete=models.CASCADE)
    payment_no = models.IntegerField()
    date = models.DateTimeField()
    payment_amount = models.DecimalField(max_digits=21, decimal_places=6)
    principal = models.DecimalField(max_digits=21, decimal_places=6)
    interest = models.DecimalField(max_digits=21, decimal_places=6)
    balance = models.DecimalField(max_digits=21, decimal_places=6)
    # Automatically set the field to now when the object is first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically set the field to now every time the object is saved.
    updated_at = models.DateTimeField(auto_now=True)

