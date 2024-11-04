from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .forms import AddStockTransactionForm, LoginForm, RegistrationForm
from .models import Portfolio, StockTransaction
from datetime import datetime
import requests

# Create your views here.
def user_login(request):
    error_message = None

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(
                request, username=data["username"], password=data["password"]
            )
            if user is not None:
                login(request, user)  # with connection.cursor() as cursor:
                # cursor.execute("""insert into test values (1)""")
                return redirect("portfolio")

            else:
                error_message = "Invalid username or password."  # Set the error message

    else:
        form = LoginForm()

    return render(
        request, "users/login.html", {"form": form, "error_message": error_message}
    )


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")  # Redirect to login page after registration
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")


@login_required
def analytics(request):
    return render(request, "users/analytics.html")


def home(request):
    return render(request, "users/home.html")


@login_required
def user_logout(request):
    logout(request)  
    return render(request, "users/home.html")  


@login_required
def portfolio_view(request):
    user_id = request.user.id

   
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT stock_symbol FROM portfolio WHERE user_id = %s", [user_id]
        )
        symbols = [row[0] for row in cursor.fetchall()]
    return render(request, "users/portfolio.html", {"symbols": symbols})




@login_required
def transactions_view(request, stock_symbol):
    user_id = request.user.id

    
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT transaction_id, purchase_type, price, quantity, transaction_date 
            FROM stock_transactions 
            WHERE user_id = %s AND stock_symbol = %s
        """,
            [user_id, stock_symbol],
        )
        transactions = cursor.fetchall()

    transactions_data = [
        {
            "transaction_id": row[0],
            "purchase_type": row[1],
            "price": float(row[2]),
            "quantity": row[3],
            "transaction_date": row[4].strftime("%Y-%m-%d") if row[4] else None,
        }
        for row in transactions
    ]

    return JsonResponse(transactions_data, safe=False)


@login_required
def add_stock_transaction(request):
    if request.method == "POST":
        form = AddStockTransactionForm(request.POST)
        if form.is_valid():
            print("form is valid")
            try:
                data = form.cleaned_data
                user_id = request.user.id

                # First, add to stock_transactions table
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO stock_transactions 
                        (user_id, purchase_type, price, quantity, stock_symbol, transaction_date) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            user_id,
                            data["purchase_type"],
                            data["price"],
                            data["quantity"],
                            data["stock_symbol"],
                            data["transaction_date"],
                        ],
                    )

                messages.success(request, "Stock transaction added successfully.")
                return redirect("portfolio")

            except Exception as e:
                messages.error(request, "Error adding transaction. Please try again.")
    else:
        form = AddStockTransactionForm()

    return render(request, "users/add_stocks.html", {"form": form})


def get_stock_data(symbol):
    api_key = 'KMSX2N60VHYWHGYR'  
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    try:
        price = float(data['Global Quote']['05. price'])
        change = float(data['Global Quote']['09. change'])
        change_percent = float(data['Global Quote']['10. change percent'].replace('%', ''))
    except (KeyError, ValueError):
        price, change, change_percent = 0.0, 0.0, 0.0  # Fallback values

    # Return formatted data
    return {
        'symbol': symbol,
        'price': price,
        'change': change,
        'change_percent': change_percent
    }

    # return {
    #     'symbol': symbol,
    #     'price': data,
    #     'change': data,
    #     'change_percent': data
    # }

def stock_data_api(request):
    print(222)
    user_id = request.user.id
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT stock_symbol FROM portfolio WHERE user_id = %s", [user_id]
        )

        symbols = [row[0] for row in cursor.fetchall()]
    stock_data = [get_stock_data(symbol) for symbol in symbols]
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({"stock_data": stock_data})

    print(symbols)
    stock_data = [get_stock_data(symbol) for symbol in symbols]
    return render(request, "users/analytics.html", {"stock_data": stock_data})
    #return JsonResponse(stock_data, safe=False)





