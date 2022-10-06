from django.test import TestCase 
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from loans.models import Loan, Repayment
from loans.serializers import LoanSerializer


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
            {'loan_amount': 100000000, 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12', 'repayment_db_count': 600, 'loan_db_count': 1, 'repayment_response_count': 600},
            {'loan_amount': 10000, 'loan_term': 1, 'interest_rate': 10, 'loan_year': 2020, 'loan_month': '10', 'repayment_db_count': 612, 'loan_db_count': 2, 'repayment_response_count': 12},
            {'loan_amount': 40000000, 'loan_term': 4, 'interest_rate': 20, 'loan_year': 2035, 'loan_month': '02', 'repayment_db_count': 660, 'loan_db_count': 3, 'repayment_response_count': 48},
        )


        for test_case in test_cases:
            with self.subTest():

                # Send POST request
                url = reverse('loans-list')
                client = APIClient()
                response = client.post(url, test_case)
                
                # Check if data saved in db as expected
                self.assertEqual(Loan.objects.count(), test_case['loan_db_count'])   
                self.assertEqual(Repayment.objects.count(), test_case['repayment_db_count'])
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
            # Non-numeric string - 'loan_amount'
            {'loan_amount': '10 thousand', 'loan_term': 50, 'interest_rate': 36, 'loan_year': 2040, 'loan_month': '12', 'expected_response': "[<class 'decimal.ConversionSyntax'>]"},
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
                # Check if response message is as expected
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
                'expected_db_count': 2,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'expected_db_count': 4,
            },
        )

        for test_case in test_cases:
            with self.subTest():

                new_loan = Loan(
                    loan_amount = test_case['test_loan']['loan_amount'], 
                    loan_term = test_case['test_loan']['loan_term'], 
                    interest_rate = test_case['test_loan']['interest_rate'], 
                    loan_year = test_case['test_loan']['loan_year'], 
                    loan_month = test_case['test_loan']['loan_month'], 
                )   
                new_loan.save()
                pk = LoanSerializer(new_loan).data['id']

                # Add extra data to test db
                new_loan = Loan(
                    loan_amount = test_case['extra_loan']['loan_amount'], 
                    loan_term = test_case['extra_loan']['loan_term'], 
                    interest_rate = test_case['extra_loan']['interest_rate'], 
                    loan_year = test_case['extra_loan']['loan_year'], 
                    loan_month = test_case['extra_loan']['loan_month'], 
                    )   
                new_loan.save()

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])    

                # Send GET request
                client = APIClient()
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
                'expected_db_count': 2,
                # Test pk which doesn't exist
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
                # Test pk which doesn't exist
                'non_existent_pk': 5,
                'expected_response': 'Loan matching query does not exist.',
            },
        )

        for test_case in test_cases:
            with self.subTest():

                new_loan = Loan(
                    loan_amount = test_case['test_loan']['loan_amount'], 
                    loan_term = test_case['test_loan']['loan_term'], 
                    interest_rate = test_case['test_loan']['interest_rate'], 
                    loan_year = test_case['test_loan']['loan_year'], 
                    loan_month = test_case['test_loan']['loan_month'], 
                )   
                new_loan.save()
                pk = LoanSerializer(new_loan).data['id']

                # Add extra data to test db
                new_loan = Loan(
                    loan_amount = test_case['extra_loan']['loan_amount'], 
                    loan_term = test_case['extra_loan']['loan_term'], 
                    interest_rate = test_case['extra_loan']['interest_rate'], 
                    loan_year = test_case['extra_loan']['loan_year'], 
                    loan_month = test_case['extra_loan']['loan_month'], 
                    )   
                new_loan.save()

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])    

                # Send GET request
                client = APIClient()
                # Use non-existent primary key in url path
                url = reverse('loans-detail', kwargs={'pk': test_case['non_existent_pk']})
                response = client.get(url)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response message is as expected
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
                'expected_db_count': 2,
                'expected_db_count_after_delete': 1,
            },
            {
                'test_loan': {
                'loan_amount': 25000000, 'loan_term': 20, 'interest_rate': 29, 'loan_year': 2023, 'loan_month': '2',
                },
                'extra_loan': {
                'loan_amount': 55000, 'loan_term': 4, 'interest_rate': 9, 'loan_year': 2023, 'loan_month': '4',
                },
                'expected_db_count': 3,
                'expected_db_count_after_delete': 2,
            },
        )

        for test_case in test_cases:
            with self.subTest():

                new_loan = Loan(
                    loan_amount = test_case['test_loan']['loan_amount'], 
                    loan_term = test_case['test_loan']['loan_term'], 
                    interest_rate = test_case['test_loan']['interest_rate'], 
                    loan_year = test_case['test_loan']['loan_year'], 
                    loan_month = test_case['test_loan']['loan_month'], 
                )   
                new_loan.save()
                pk = LoanSerializer(new_loan).data['id']

                # Add extra data to test db
                new_loan = Loan(
                    loan_amount = test_case['extra_loan']['loan_amount'], 
                    loan_term = test_case['extra_loan']['loan_term'], 
                    interest_rate = test_case['extra_loan']['interest_rate'], 
                    loan_year = test_case['extra_loan']['loan_year'], 
                    loan_month = test_case['extra_loan']['loan_month'], 
                    )   
                new_loan.save()

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])   
                # Check if data to be deleted is in db
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), True)  

                # Send DELETE request
                client = APIClient()
                url = reverse('loans-detail', kwargs={'pk': pk})
                response = client.delete(url)

                # Check if request was resolved successfully     
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                # Check if a set of data was deleted succuessfully
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count_after_delete'])        
                # Check if correct set of data was deleted based on primary key 
                self.assertEqual(Loan.objects.filter(pk=pk).exists(), False)


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
                'non_existent_pk': 5,
                'expected_response': 'Loan matching query does not exist.',
            },
        )

        for test_case in test_cases:
            with self.subTest():

                new_loan = Loan(
                    loan_amount = test_case['test_loan']['loan_amount'], 
                    loan_term = test_case['test_loan']['loan_term'], 
                    interest_rate = test_case['test_loan']['interest_rate'], 
                    loan_year = test_case['test_loan']['loan_year'], 
                    loan_month = test_case['test_loan']['loan_month'], 
                )   
                new_loan.save()

                # Add extra data to test db
                new_loan = Loan(
                    loan_amount = test_case['extra_loan']['loan_amount'], 
                    loan_term = test_case['extra_loan']['loan_term'], 
                    interest_rate = test_case['extra_loan']['interest_rate'], 
                    loan_year = test_case['extra_loan']['loan_year'], 
                    loan_month = test_case['extra_loan']['loan_month'], 
                    )   
                new_loan.save()

                # Check if data is saved successfully in db
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])   

                # Send DELETE request
                client = APIClient()
                # Use non-existent primary key in url path
                url = reverse('loans-detail', kwargs={'pk': test_case['non_existent_pk']})
                response = client.delete(url)

                # Check if request was resolved as expected    
                self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
                # Check if response message is as expected
                self.assertEqual(response.data, test_case['expected_response'])
                # Check if any data was deleted 
                self.assertEqual(Loan.objects.count(), test_case['expected_db_count'])   


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
        pk = LoanSerializer(new_loan).data['id']
        
        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)        

        data = {
            'loan_amount': '20000',
            'loan_term': '2',
            'interest_rate': '20',
            'loan_month': '12',
            'loan_year': '2020'
        }

        # Send PUT request
        client = APIClient()
        url = reverse('loans-detail', kwargs={'pk': pk})
        response = client.put(url, data)

        # Check if values are correct and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan']['loan_amount'], 20000.000000)          
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
        pk = LoanSerializer(new_loan).data['id']
        
        # Check if data is saved successfully in db
        self.assertEqual(Loan.objects.count(), 1)        

        # Send GET request
        client = APIClient()
        url = reverse('loans-edit', kwargs={'pk': pk})
        response = client.get(url)

        # Check if values are correct and if request was resolved successfully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_amount'], 10000.000000)          
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
      