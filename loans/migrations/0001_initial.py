# Generated by Django 4.1.1 on 2022-09-30 03:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_amount', models.DecimalField(decimal_places=6, max_digits=21)),
                ('loan_term', models.IntegerField()),
                ('interest_rate', models.DecimalField(decimal_places=6, max_digits=21)),
                ('loan_month', models.CharField(max_length=2)),
                ('loan_year', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'loans',
            },
        ),
        migrations.CreateModel(
            name='Repayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_no', models.IntegerField()),
                ('date', models.DateField()),
                ('payment_amount', models.DecimalField(decimal_places=6, max_digits=21)),
                ('principal', models.DecimalField(decimal_places=6, max_digits=21)),
                ('interest', models.DecimalField(decimal_places=6, max_digits=21)),
                ('balance', models.DecimalField(decimal_places=6, max_digits=21)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loans.loan')),
            ],
            options={
                'db_table': 'repayments',
            },
        ),
    ]
