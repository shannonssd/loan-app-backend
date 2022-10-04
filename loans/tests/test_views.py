from django.test import TestCase 
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from loans.models import Loan
from loans.serializers import LoanSerialzier

class ViewTests(TestCase):
    """Test for loan views"""

    def test_loan_list_happy_case(self):
        """Test happy case for loan list retrieval: GET request"""

        url = reverse('loans-list')
        client = APIClient()
        response = client.get(url)

        # Test if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_loan_create_happy_case(self):
        """Test happy case for loan creation: POST request"""

        url = reverse('loans-list')
        data = {
            'loan_amount': '10000',
            'loan_term': '1',
            'interest_rate': '10',
            'loan_month': '02',
            'loan_year': '2022'
        }
        client = APIClient()
        response = client.post(url, data)

        # Check if data is successfully saved in db, if values are correct and if request was resolved successfully
        self.assertEqual(Loan.objects.count(), 1)        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Loan.objects.get().loan_amount, 10000)
        self.assertEqual(Loan.objects.get().loan_term, 1)

    def test_loan_retrieve_happy_case(self):
        """Test happy case for individual loan retrieval: GET request"""

        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = 1,
            )   
        new_loan.save()
        pk = LoanSerialzier(new_loan).data['id']

        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)    

        client = APIClient()
        url = reverse('loans-detail', kwargs={'pk': pk})
        response = client.get(url)

        # Check if values are correct and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan']['loan_amount'], '10000.000000')        

    def test_loan_destroy_happy_case(self):
        """Test happy case for individual loan deletion: DELETE request"""

        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = 1,
            )   
        new_loan.save()
        pk = LoanSerialzier(new_loan).data['id']

        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)        

        client = APIClient()
        url = reverse('loans-detail', kwargs={'pk': pk})
        response = client.delete(url)

        # Check if data was successfully deleted from db and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Loan.objects.count(), 0)        


    def test_loan_update_happy_case(self):
        """Test happy case for updating loan data in db: PUT request"""

        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = 1,
            )   
        new_loan.save()
        pk = LoanSerialzier(new_loan).data['id']
        
        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)        

        data = {
            'loan_amount': '20000',
            'loan_term': '2',
            'interest_rate': '20',
            'loan_month': '12',
            'loan_year': '2020'
        }

        client = APIClient()
        url = reverse('loans-detail', kwargs={'pk': pk})
        response = client.put(url, data)

        # Check if values are correct and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan']['loan_amount'], '20000.000000')          
        self.assertEqual(response.data['loan']['loan_term'], 2)  

    def test_loan_edit_retrieval_happy_case(self):
        """Test happy case for retrieving data for loan update: GET request"""

        new_loan = Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = 1,
            )   
        new_loan.save()
        pk = LoanSerialzier(new_loan).data['id']
        
        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)        

        client = APIClient()
        url = reverse('loans-edit', kwargs={'pk': pk})
        response = client.get(url)

        # Check if values are correct and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_amount'], '10000.000000')          
        self.assertEqual(response.data['loan_term'], 1)  


    def test_loan_filter_happy_case(self):
        """Test happy case for filtering loans: GET request"""

        loan_list = [
            Loan(
            loan_amount = 10000, 
            loan_term = 1, 
            interest_rate = 0.1, 
            loan_year = 2022, 
            loan_month = 1,
            ),   
            Loan(
            loan_amount = 2000, 
            loan_term = 2, 
            interest_rate = 0.4, 
            loan_year = 2022, 
            loan_month = 1,
            ),   
            Loan(
            loan_amount = 30000, 
            loan_term = 1, 
            interest_rate = 0.3, 
            loan_year = 2022, 
            loan_month = 1,
            ),   
        ]
        Loan.objects.bulk_create(loan_list)
        
        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 3)        

        client = APIClient()
        
        ### Not sure how to pass request query parameters into reverse function ###
        url = reverse('loans-filter')

        # response = client.get(url)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
      