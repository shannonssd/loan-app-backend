from django.db import models

class Loan(models.Model):
    """Database model for individual loans"""

    # Customize database table name
    class Meta:
      db_table = 'loans'

    loan_amount = models.DecimalField(max_digits=21, decimal_places=6)
    loan_term = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=21, decimal_places=6)
    loan_month = models.CharField(max_length=2)
    loan_year = models.IntegerField()
    # Automatically set the field to now when the object is first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically set the field to now every time the object is saved.
    updated_at = models.DateTimeField(auto_now=True)
  


class Repayment(models.Model):
    """Database model for loan repayment schedule"""

    # Customize database table name
    class Meta:
      db_table = 'repayments'

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    payment_no = models.IntegerField()
    date = models.DateField()
    payment_amount = models.DecimalField(max_digits=21, decimal_places=6)
    principal = models.DecimalField(max_digits=21, decimal_places=6)
    interest = models.DecimalField(max_digits=21, decimal_places=6)
    balance = models.DecimalField(max_digits=21, decimal_places=6)
    # Automatically set the field to now when the object is first created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically set the field to now every time the object is saved.
    updated_at = models.DateTimeField(auto_now=True)

    