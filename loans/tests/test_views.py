from django.test import TestCase 
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from loans.models import Loan, Repayment
from loans.serializers import LoanSerializer
from django.utils.http import urlencode

class ViewTests(TestCase):
    """Test for loan views"""

    def test_loan_list(self):
        """Test happy cases for loan list retrieval: GET request"""
        
        test_cases = (
            # Test retrieval from empty db
            {
                'loan_list': [], 'expected_count': 0
            },
            # Test retrieval from db with existing loans
            {
                'loan_list': 
                [
                    {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',},
                    {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2022, 'loan_month': '01',},
                    {'loan_amount': 50000, 'loan_term': 4, 'interest_rate': 20, 'loan_year': 2024, 'loan_month': '07',},
                ], 'expected_count': 3,
            },
        )

        for test_case in test_cases:
            with self.subTest():
                
                # Add loans to Loan model
                loan_arr = []
                for loan in test_case['loan_list']:
                    new_loan = Loan(
                        loan_amount = loan['loan_amount'], 
                        loan_term = loan['loan_term'], 
                        interest_rate = loan['interest_rate'], 
                        loan_year = loan['loan_year'], 
                        loan_month = loan['loan_month'], 
                    ) 
                    loan_arr.append(new_loan)

                # Store test loan(s) in db
                Loan.objects.bulk_create(loan_arr)

                # Send GET request
                url = reverse('loans-list')
                client = APIClient()
                response = client.get(url)

                # Check if request was resolved successfully
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if endpoint response is as expected
                self.assertEqual(len(response.data), test_case['expected_count'])


    def test_loan_create(self):
        """Test happy cases for loan creation: POST request"""

        test_cases = (
            {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12', 'repayment_db_count': 600, 'repayment_response_count': 600},
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '10', 'repayment_db_count': 12, 'repayment_response_count': 12},
            {'loan_amount': 40000000, 'loan_term': 4, 'interest_rate': 20, 'loan_year': 2035, 'loan_month': '02', 'repayment_db_count': 48, 'repayment_response_count': 48},
        )

        for test_case in test_cases:
            with self.subTest():

                # Send POST request
                client = APIClient()
                url = reverse('loans-list')
                response = client.post(url, test_case)

                # Store primary key to check db
                pk = response.data['loan']['id']

                # Check if data saved in db as expected
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True) 
                self.assertEqual(Repayment.objects.filter(loan=pk).count(), test_case['repayment_db_count'])
                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if endpoint response is as expected
                self.assertEqual(response.data['loan']['loan_amount'], test_case['loan_amount'])
                self.assertEqual(response.data['loan']['loan_term'], test_case['loan_term'])
                self.assertEqual(response.data['loan']['interest_rate'], test_case['interest_rate'])
                self.assertEqual(response.data['loan']['loan_year'], test_case['loan_year'])
                self.assertEqual(response.data['loan']['loan_month'], test_case['loan_month'])
                self.assertEqual(len(response.data['repayment list']), test_case['repayment_response_count'])


    def test_loan_create_error(self):
        """Test edge cases for loan list creation: POST request"""
        
        test_cases = (
            # Non-numeric string (Decimal field) - 'loan_amount'
            {'loan_amount': 'ten thousand', 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12', 'expected_response': "[<class 'decimal.ConversionSyntax'>]"},
            # Non-numeric string (Integer field) - 'loan_term'
            {'loan_amount': 10000000, 'loan_term': 'fifty', 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12', 'expected_response': "invalid literal for int() with base 10: 'fifty'"},
            # Value out of range - 'loan_amount'
            {'loan_amount': 10000000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '01', 'expected_response': 'Loan amount is not within the acceptable range of 1000 - 100,000,000 THB.'},
            # Value out of range - 'loan_term'
            {'loan_amount': 100000, 'loan_term': 51, 'interest_rate': 20, 'loan_year': 2040, 'loan_month': '01', 'expected_response': 'Loan term is not within the acceptable range of 1 - 50 years.'},
            # Value out of range - 'interest_rate'
            {'loan_amount': 100000, 'loan_term': 50, 'interest_rate': 37, 'loan_year': 2040, 'loan_month': '01', 'expected_response': 'Interest rate is not within the acceptable range of 1 - 36%.'},
            # Value out of range - 'start date'
            {'loan_amount': 100000, 'loan_term': 50, 'interest_rate': 30, 'loan_year': 2051, 'loan_month': '01', 'expected_response': 'Loan start date is not within the acceptable range of 2017-2050.'},
            # Missing field- 'interest_rate'
            {'loan_amount': 'fifty thousand', 'loan_term': 50, 'loan_year': 2040, 'loan_month': '12', 'expected_response': 'Missing field'},
        )

        for test_case in test_cases:
            with self.subTest():
               
                # Send POST request
                url = reverse('loans-list')
                client = APIClient()
                response = client.post(url, test_case)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])


    def test_loan_retrieve(self):
        """Test happy cases for individual loan retrieval: GET request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'repayment_db_count': 600,
                'repayment_response_count': 600,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'repayment_response_count': 240,
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                post_response = client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Store pk of data to be retrieved
                pk = post_response.data['loan']['id']

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True)        
                self.assertEqual(Repayment.objects.filter(loan=pk).count(), test_case['repayment_db_count'])  

                # Send GET request
                url = reverse('loans-detail', kwargs={'pk': pk})
                response = client.get(url)

                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if correct set of data is being retrieved based on primary key (pk)
                self.assertEqual(response.data['loan']['id'], pk)
                # Check if endpoint response is as expected
                self.assertEqual(response.data['loan']['loan_amount'], test_case['test_loan']['loan_amount'])
                self.assertEqual(response.data['loan']['loan_term'], test_case['test_loan']['loan_term'])
                self.assertEqual(response.data['loan']['interest_rate'], test_case['test_loan']['interest_rate'])
                self.assertEqual(response.data['loan']['loan_year'], test_case['test_loan']['loan_year'])
                self.assertEqual(response.data['loan']['loan_month'], test_case['test_loan']['loan_month'])   
                self.assertEqual(len(response.data['repayment list']), test_case['repayment_response_count']) 


    def test_loan_retrieve_error(self):
        """Test edge cases for individual loan retrieval: GET request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                # Test pk which doesn't exist
                'non_existent_pk': 3,
                'repayment_db_count': 600,
                'expected_response': 'Loan matching query does not exist.',
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                # Test pk which doesn't exist
                'non_existent_pk': 5,
                'repayment_db_count': 240,  
                'expected_response': 'Loan matching query does not exist.',
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                url = reverse('loans-list')
                response = client.post(url, test_case['test_loan'])
                client.post(url, test_case['extra_loan'])

                # Send GET request
                # Use non-existent primary key in url path
                url = reverse('loans-detail', kwargs={'pk': test_case['non_existent_pk']})
                response = client.get(url)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])
                 


    def test_loan_destroy(self):
        """Test happy case for individual loan deletion: DELETE request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'repayment_db_count': 600,
                'expected_loan_response_length': 1,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'expected_loan_response_length': 2,
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                post_response = client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Store pk of data to be deleted
                pk = post_response.data['loan']['id']

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True)        
                self.assertEqual(Repayment.objects.filter(loan=pk).count(), test_case['repayment_db_count'])    

                # Send DELETE request
                url = reverse('loans-detail', kwargs={'pk': pk})
                response = client.delete(url)

                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if correct set of data was deleted based on primary key 
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), False)
                self.assertEqual(Repayment.objects.filter(loan=pk).exists(), False)
                # Check if response is as expected
                self.assertEqual(len(response.data), test_case['expected_loan_response_length'])


    def test_loan_destroy_error(self):
        """Test edge cases for individual loan deletion: DELETE request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'expected_db_count': 2,
                'repayment_db_count': 600,
                'non_existent_pk': 3,
                'expected_response': 'Loan matching query does not exist.',
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'expected_db_count': 4,
                'repayment_db_count': 240,
                'non_existent_pk': 5,
                'expected_response': 'Loan matching query does not exist.',
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Send DELETE request
                client = APIClient()
                # Use non-existent primary key in url path
                url = reverse('loans-detail', kwargs={'pk': test_case['non_existent_pk']})
                response = client.delete(url)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])
                # Check if any data was deleted 
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])   


    def test_loan_update(self):
        """Test happy cases for updating loan data in db: PUT request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'test_loan_new': {
                'loan_amount': 500000, 'loan_term': 25, 'interest_rate': 18, 'loan_year': 2041, 'loan_month': '1',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'repayment_db_count': 600,
                'repayment_response_count': 300,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 9, 'interest_rate': 14, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'repayment_response_count': 108,
            },
        )

        for test_case in test_cases:
            with self.subTest():
                
                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                post_response = client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Store pk of data to be modifed
                pk = post_response.data['loan']['id']

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True)        
                self.assertEqual(Repayment.objects.filter(loan=pk).count(), test_case['repayment_db_count'])


                # Send PUT request
                url = reverse('loans-detail', kwargs={'pk': pk})
                response = client.put(url, test_case['test_loan_new'])

                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if correct set of data has been updated based on primary key (pk)
                self.assertEqual(response.data['loan']['id'], pk)
                # Check if endpoint response is as expected
                self.assertEqual(response.data['loan']['loan_amount'], test_case['test_loan_new']['loan_amount'])
                self.assertEqual(response.data['loan']['loan_term'], test_case['test_loan_new']['loan_term'])
                self.assertEqual(response.data['loan']['interest_rate'], test_case['test_loan_new']['interest_rate'])
                self.assertEqual(response.data['loan']['loan_year'], test_case['test_loan_new']['loan_year'])
                self.assertEqual(response.data['loan']['loan_month'], test_case['test_loan_new']['loan_month'])
                self.assertEqual(len(response.data['repayment list']), test_case['repayment_response_count']) 


    def test_loan_update_error(self):
        """Test edge cases for updating loan data in db: PUT request"""

        test_cases = (
            {
                # Test pk which doesn't exist
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'test_loan_new': {
                'loan_amount': 500000, 'loan_term': 25, 'interest_rate': 18, 'loan_year': 2041, 'loan_month': '1',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'repayment_db_count': 600,
                'pk': 10,
                'expected_response': 'Loan matching query does not exist.',
            },
            {
                # Test non-numeric string (Decimal field) - 'loan_amount'
                'test_loan': {
                'loan_amount': 1000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'test_loan_new': {
                'loan_amount': 'ten thousand', 'loan_term': 9, 'interest_rate': 14, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': "[<class 'decimal.ConversionSyntax'>]",
            },
            {
                # Test non-numeric string (Integer field) - 'loan_term'
                'test_loan': {
                'loan_amount': 10000000, 'loan_term': 20, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 'fifty', 'interest_rate': 14, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': "invalid literal for int() with base 10: 'fifty'",
            },
            {
                # Test value out of range - 'loan_amount'
                'test_loan': {
                'loan_amount': 1000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '01',
                },
                'test_loan_new': {
                'loan_amount': 10000000000, 'loan_term': 9, 'interest_rate': 14, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': 'Loan amount is not within the acceptable range of 1000 - 100,000,000 THB.',
            },
            {
                # Test value out of range - 'loan_term'
                'test_loan': {
                'loan_amount': 100000, 'loan_term': 40, 'interest_rate': 20, 'loan_year': 2040, 'loan_month': '01',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 51, 'interest_rate': 14, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': 'Loan term is not within the acceptable range of 1 - 50 years.',
            },
            {
                # Test value out of range - 'interest_rate'
                'test_loan': {
                'loan_amount': 100000, 'loan_term': 50, 'interest_rate': 30, 'loan_year': 2040, 'loan_month': '01',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 9, 'interest_rate': 37, 'loan_year': 2024, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': 'Interest rate is not within the acceptable range of 1 - 36%.',
            },
            {
                # Test value out of range - 'start date'
                'test_loan': {
                'loan_amount': 100000, 'loan_term': 50, 'interest_rate': 30, 'loan_year': 2022, 'loan_month': '01',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 9, 'interest_rate': 14, 'loan_year': 2016, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': 'Loan start date is not within the acceptable range of 2017-2050.',
            },
            {
                # Test missing field- 'interest_rate'
                'test_loan': {
                'loan_amount': 100000, 'loan_term': 50, 'interest_rate': 14, 'loan_year': 2022, 'loan_month': '01',
                },
                'test_loan_new': {
                'loan_amount': 100000, 'loan_term': 9, 'loan_year': 2022, 'loan_month': '3',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_db_count': 240,
                'pk': '',
                'expected_response': 'Missing field',
            },
        )

        for test_case in test_cases:
            with self.subTest():
                
                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                post_response = client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                if (test_case['pk'] == ''):
                    pk = post_response.data['loan']['id']
                else:
                    pk = test_case['pk']

                # Send PUT request
                # Use non-existent primary key in url path
                url = reverse('loans-detail', kwargs={'pk': pk})
                response = client.put(url, test_case['test_loan_new'])

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])


    def test_loan_edit_data_retrieval(self):
        """Test happy cases for retrieving data for loan update: GET request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 10, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                'repayment_count': 120,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 15, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'repayment_count': 180,
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                post_response = client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Store pk of data to be retrieved
                pk = post_response.data['loan']['id']

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True)        
                self.assertEqual(Repayment.objects.filter(loan=pk).count(), test_case['repayment_count'])        

                # Send GET request
                client = APIClient()
                url = reverse('loans-edit', kwargs={'pk': pk})
                response = client.get(url)

                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if correct set of data is being retrieved based on primary key (pk)
                self.assertEqual(response.data['id'], pk)
                # Check if endpoint response is as expected
                self.assertEqual(response.data['loan_amount'], test_case['test_loan']['loan_amount'])
                self.assertEqual(response.data['loan_term'], test_case['test_loan']['loan_term'])
                self.assertEqual(response.data['interest_rate'], test_case['test_loan']['interest_rate'])
                self.assertEqual(response.data['loan_year'], test_case['test_loan']['loan_year'])
                self.assertEqual(response.data['loan_month'], test_case['test_loan']['loan_month'])   


    def test_loan_edit_data_retrieval_error(self):
        """Test edge cases for retrieving data for loan update: GET request"""

        test_cases = (
            {
                'test_loan': {
                'loan_amount': 100000000, 'loan_term': 10, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12',
                },
                'extra_loan': {
                'loan_amount': 400000, 'loan_term': 2, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '1',
                },
                # Test pk which doesn't exist
                'non_existent_pk': 3,
                'expected_response': 'Loan matching query does not exist.',
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 15, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                # Test pk which doesn't exist
                'non_existent_pk': 5,  
                'expected_response': 'Loan matching query does not exist.',
            },
        )

        for test_case in test_cases:
            with self.subTest():

                # Make post requests to add test data to db
                client = APIClient()
                post_url = reverse('loans-list')
                client.post(post_url, test_case['test_loan'])
                client.post(post_url, test_case['extra_loan'])

                # Send GET request
                # Use non-existent primary key in url path
                client = APIClient()
                url = reverse('loans-edit', kwargs={'pk': test_case['non_existent_pk']})
                response = client.get(url)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])  


    def test_loan_filter(self):
        """Test happy case for filtering loans: GET request"""

        # Loan list to test filter against
        loan_list = [
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '10', 'repayment_db_count': 12, 'repayment_response_count': 12},
            {'loan_amount': 250000, 'loan_term': 4, 'interest_rate': 20, 'loan_year': 2022, 'loan_month': '02', 'repayment_db_count': 48, 'repayment_response_count': 48},
            {'loan_amount': 5000000, 'loan_term': 12, 'interest_rate': 20, 'loan_year': 2023, 'loan_month': '02', 'repayment_db_count': 144, 'repayment_response_count': 144},
            {'loan_amount': 40000000, 'loan_term': 30, 'interest_rate': 30, 'loan_year': 2023, 'loan_month': '02', 'repayment_db_count': 360, 'repayment_response_count': 360},
            {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2025, 'loan_month': '12', 'repayment_db_count': 600, 'repayment_response_count': 600},
        ]

        test_cases = (
            {
                'query_string': [
                    {'loan_amount_lower': 'null'},
                    {'loan_amount_upper': 'null'},
                    {'loan_term_lower': 'null'},
                    {'loan_term_upper': 'null'},
                    {'interest_rate_lower': 'null'},
                    {'interest_rate_upper': 'null'},
                ],
                'expected_response_length': 5, 
            },
            {
                'query_string': [
                    {'loan_amount_lower': 5000000},
                    {'loan_amount_upper': 'null'},
                    {'loan_term_lower': 13},
                    {'loan_term_upper': 'null'},
                    {'interest_rate_lower': 'null'},
                    {'interest_rate_upper': 'null'},
                ],
                'expected_response_length': 2, 
            },
        )

        # Function to add query string to reversed url
        def custom_reverse(viewname, query_kwargs):

            url = viewname
            for x in range(0, len(query_kwargs)):
                if x == 0:
                    url = f'{viewname}?{urlencode(query_kwargs[x])}'
                else:
                    url = url + f'&{urlencode(query_kwargs[x])}'
        
            return url

        # Add loans to Loan model
        loan_arr = []
        for loan in loan_list:
            new_loan = Loan(
                loan_amount = loan['loan_amount'], 
                loan_term = loan['loan_term'], 
                interest_rate = loan['interest_rate'], 
                loan_year = loan['loan_year'], 
                loan_month = loan['loan_month'], 
            ) 
            loan_arr.append(new_loan)

        # Store test loan in db
        Loan.objects.bulk_create(loan_arr)

        for test_case in test_cases:
            with self.subTest():
     
                # Send GET request
                url = reverse('loans-filter')
                url_with_querystring = custom_reverse(url, test_case['query_string'])
                client = APIClient()
                response = client.get(url_with_querystring)

                # Check if request was resolved successfully
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if filtered results are as expected
                self.assertEqual(len(response.data), test_case['expected_response_length'])


    def test_loan_filter_error(self):
        """Test edge cases for filtering loans: GET request"""

        # Loan list to test filter against
        loan_list = [
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '10', 'repayment_db_count': 12, 'repayment_response_count': 12},
            {'loan_amount': 250000, 'loan_term': 4, 'interest_rate': 20, 'loan_year': 2022, 'loan_month': '02', 'repayment_db_count': 48, 'repayment_response_count': 48},
            {'loan_amount': 5000000, 'loan_term': 12, 'interest_rate': 20, 'loan_year': 2023, 'loan_month': '02', 'repayment_db_count': 144, 'repayment_response_count': 144},
            {'loan_amount': 40000000, 'loan_term': 30, 'interest_rate': 30, 'loan_year': 2023, 'loan_month': '02', 'repayment_db_count': 360, 'repayment_response_count': 360},
            {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2025, 'loan_month': '12', 'repayment_db_count': 600, 'repayment_response_count': 600},
        ]

        test_cases = (
            {
                # Missing field - 'loan_amount_lower'
                'query_string': [
                    {'loan_amount_upper': 'null'},
                    {'loan_term_lower': 'null'},
                    {'loan_term_upper': 'null'},
                    {'interest_rate_lower': 'null'},
                    {'interest_rate_upper': 'null'},
                ],
                'expected_response': "Missing field", 
            },
            {
                # Empty string (Integer field) - 'loan_term_lower'
                'query_string': [
                    {'loan_amount_lower': 5000000},
                    {'loan_amount_upper': 'null'},
                    {'loan_term_lower': ''},
                    {'loan_term_upper': 'null'},
                    {'interest_rate_lower': 'null'},
                    {'interest_rate_upper': 'null'},
                ],
                'expected_response': "invalid literal for int() with base 10: ''", 
            },
            {
                # Empty string (Decimal field) - 'interest_rate_upper'
                'query_string': [
                    {'loan_amount_lower': 5000000},
                    {'loan_amount_upper': 'null'},
                    {'loan_term_lower': 13},
                    {'loan_term_upper': 'null'},
                    {'interest_rate_lower': 'null'},
                    {'interest_rate_upper': ''},
                ],
                'expected_response': "[<class 'decimal.ConversionSyntax'>]", 
            },
        )

        # Function to add query string to reversed url
        def custom_reverse(viewname, query_kwargs):

            url = viewname
            for x in range(0, len(query_kwargs)):
                if x == 0:
                    url = f'{viewname}?{urlencode(query_kwargs[x])}'
                else:
                    url = url + f'&{urlencode(query_kwargs[x])}'
        
            return url

        # Add loans to Loan model
        loan_arr = []
        for loan in loan_list:
            new_loan = Loan(
                loan_amount = loan['loan_amount'], 
                loan_term = loan['loan_term'], 
                interest_rate = loan['interest_rate'], 
                loan_year = loan['loan_year'], 
                loan_month = loan['loan_month'], 
            ) 
            loan_arr.append(new_loan)

        # Store test loan in db
        Loan.objects.bulk_create(loan_arr)

        for test_case in test_cases:
            with self.subTest():
     
                # Send GET request
                url = reverse('loans-filter')
                url_with_querystring = custom_reverse(url, test_case['query_string'])
                client = APIClient()
                response = client.get(url_with_querystring)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response error message is as expected
                self.assertEqual(response.data, test_case['expected_response'])