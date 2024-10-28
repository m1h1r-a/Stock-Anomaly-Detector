from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.db import connection
from .forms import LoginForm, RegistrationForm
from django.http import JsonResponse
from .models import Portfolio, StockTransaction

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
                login(request, user)
                with connection.cursor() as cursor:
                    cursor.execute("""insert into test values (1)""")
                return render(request, "users/dashboard.html")
            
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


def user_logout(request):
    logout(request)  # Logs out the user
    return render(request, "users/home.html")  # Response message after logout


def portfolio_view(request):
    user_id = request.user.id

    # Raw SQL to fetch stock symbols in the user's portfolio
    with connection.cursor() as cursor:
        cursor.execute("SELECT stock_symbol FROM portfolio WHERE user_id = %s", [user_id])
        symbols = [row[0] for row in cursor.fetchall()]
    return render(request, 'users/portfolio.html', {'symbols': symbols})

# View to fetch transactions for a specific stock symbol
def transactions_view(request, stock_symbol):
    user_id = request.user.id

    # Raw SQL to fetch transactions based on stock symbol and user
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT transaction_id, purchase_type, price, quantity, transaction_date 
            FROM stock_transactions 
            WHERE user_id = %s AND stock_symbol = %s
        """, [user_id, stock_symbol])
        transactions = cursor.fetchall()

    # Structure transactions as JSON data
    transactions_data = [
        {
            'transaction_id': row[0],
            'purchase_type': row[1],
            'price': float(row[2]),
            'quantity': row[3],
            'transaction_date': row[4].strftime('%Y-%m-%d') if row[4] else None,
        }
        for row in transactions
    ]

    return JsonResponse(transactions_data, safe=False)