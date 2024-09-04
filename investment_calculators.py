import streamlit as st
import numpy as np
import pandas as pd

def indian_format(number):
    number = int(number)  # Convert to integer to remove decimal part
    s = f"{number:,}".split(",")
    if len(s) > 4:
        return f'{",".join(s[:-3])},{s[-3]},{s[-2]},{s[-1]}'
    elif len(s) == 4:
        return f'{s[0]},{s[1]},{s[2]},{s[3]}'
    elif len(s) == 3:
        return f'{s[0]},{s[1]},{s[2]}'
    return f'{s[0]},{s[1]}' if len(s) == 2 else s[0]

def amount_in_words(amount):
    amount = int(amount)  # Convert to integer to remove decimal part
    if amount >= 10000000:
        return f"₹{indian_format(amount)} ({amount//10000000} Crore)"
    elif amount >= 100000:
        return f"₹{indian_format(amount)} ({amount//100000} Lakh)"
    elif amount >= 1000:
        return f"₹{indian_format(amount)} ({amount//1000} Thousand)"
    else:
        return f"₹{indian_format(amount)}"

def calculate_capital_gains(initial_investment, years, annual_investment, inflation_rate, expected_return):
    total_investment = initial_investment
    current_value = initial_investment
    data = [(0, initial_investment, current_value)]
    for year in range(1, years + 1):
        total_investment += annual_investment
        current_value = (current_value + annual_investment) * (1 + expected_return)
        annual_investment *= (1 + inflation_rate)
        data.append((year, int(total_investment), int(current_value)))
    gain = int(current_value - total_investment)
    return int(total_investment), int(current_value), gain, data

def calculate_loan_emi(principal, rate, time):
    rate = rate / (12 * 100)  # monthly interest rate
    time = time * 12  # total number of months
    emi = (principal * rate * (1 + rate)**time) / ((1 + rate)**time - 1)
    total_payment = emi * time
    total_interest = total_payment - principal
    data = [(0, principal, 0)]
    remaining_principal = principal
    for month in range(1, time + 1):
        interest_paid = remaining_principal * rate
        principal_paid = emi - interest_paid
        remaining_principal -= principal_paid
        total_interest_paid = principal - remaining_principal
        data.append((month, int(remaining_principal), int(total_interest_paid)))
    return int(emi), int(total_payment), int(total_interest), data

def calculate_swp(initial_investment, withdrawal_rate, years, expected_return):
    monthly_rate = (1 + expected_return)**(1/12) - 1
    monthly_withdrawal = initial_investment * (withdrawal_rate / 12)
    balance = [initial_investment]
    for _ in range(years * 12):
        new_balance = (balance[-1] * (1 + monthly_rate)) - monthly_withdrawal
        balance.append(max(0, new_balance))
        if new_balance <= 0:
            break
    return [int(b) for b in balance]

st.title('Indian Investment Calculators')

calculator = st.selectbox(
    'Select a calculator:',
    ('Capital Gains', 'Loan EMI', 'Systematic Withdrawal Plan (SWP)')
)

if calculator == 'Capital Gains':
    st.header('Capital Gains Calculator')
    initial_investment = st.slider('Initial investment (₹)', min_value=0, max_value=100000000, value=1000000, step=100000, format='%d')
    years = st.slider('Number of years', min_value=1, max_value=30, value=10)
    annual_investment = st.slider('Annual investment (₹)', min_value=0, max_value=10000000, value=100000, step=10000, format='%d')
    inflation_rate = st.slider('Inflation rate (%)', min_value=0.0, max_value=15.0, value=5.0, step=0.1) / 100
    expected_return = st.slider('Expected annual return (%)', min_value=0.0, max_value=30.0, value=10.0, step=0.1) / 100
    
    if st.button('Calculate Capital Gains'):
        total_investment, current_value, gain, data = calculate_capital_gains(initial_investment, years, annual_investment, inflation_rate, expected_return)
        st.success(f'Total Investment: {amount_in_words(total_investment)}')
        st.success(f'Current Value: {amount_in_words(current_value)}')
        st.success(f'Capital Gain: {amount_in_words(gain)}')
        
        df = pd.DataFrame(data, columns=['Year', 'Total Investment', 'Current Value'])
        st.line_chart(df.set_index('Year'))

elif calculator == 'Loan EMI':
    st.header('Loan EMI Calculator')
    principal = st.slider('Loan amount (₹)', min_value=10000, max_value=10000000, value=1000000, step=10000, format='%d')
    rate = st.slider('Annual interest rate (%)', min_value=1.0, max_value=20.0, value=8.0, step=0.1)
    time = st.slider('Loan tenure (years)', min_value=1, max_value=30, value=20)
    
    if st.button('Calculate EMI'):
        emi, total_payment, total_interest, data = calculate_loan_emi(principal, rate, time)
        st.success(f'Monthly EMI: {amount_in_words(emi)}')
        st.success(f'Total Payment: {amount_in_words(total_payment)}')
        st.success(f'Total Interest: {amount_in_words(total_interest)}')
        
        df = pd.DataFrame(data, columns=['Month', 'Remaining Principal', 'Interest Paid'])
        df['Year'] = df['Month'] / 12  # Convert to years for better visualization
        st.line_chart(df.set_index('Year')[['Remaining Principal', 'Interest Paid']])

elif calculator == 'Systematic Withdrawal Plan (SWP)':
    st.header('Systematic Withdrawal Plan (SWP) Calculator')
    initial_investment = st.slider('Initial investment (₹)', min_value=100000, max_value=100000000, value=1000000, step=100000, format='%d')
    withdrawal_rate = st.slider('Annual withdrawal rate (%)', min_value=1.0, max_value=20.0, value=4.0, step=0.1) / 100
    years = st.slider('Number of years', min_value=1, max_value=30, value=20)
    expected_return = st.slider('Expected annual return (%)', min_value=0.0, max_value=20.0, value=8.0, step=0.1) / 100
    
    if st.button('Calculate SWP'):
        balance = calculate_swp(initial_investment, withdrawal_rate, years, expected_return)
        final_balance = balance[-1]
        monthly_withdrawal = int(initial_investment * withdrawal_rate / 12)
        st.success(f'Initial Investment: {amount_in_words(initial_investment)}')
        st.success(f'Monthly Withdrawal: {amount_in_words(monthly_withdrawal)}')
        st.success(f'Final Balance after {years} years: {amount_in_words(final_balance)}')
        
        df = pd.DataFrame({
            'Month': range(len(balance)),
            'Balance': balance
        })
        df['Year'] = df['Month'] / 12
        st.line_chart(df.set_index('Year')['Balance'])

st.sidebar.info('All calculations are in Indian Rupees (₹)')