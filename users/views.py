from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .forms import AddStockTransactionForm, LoginForm, RegistrationForm
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
    logout(request)  # Logs out the user
    return render(request, "users/home.html")  # Response message after logout


@login_required
def portfolio_view(request):
    user_id = request.user.id

    # Raw SQL to fetch stock symbols in the user's portfolio
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT stock_symbol FROM portfolio WHERE user_id = %s", [user_id]
        )
        symbols = [row[0] for row in cursor.fetchall()]
    return render(request, "users/portfolio.html", {"symbols": symbols})


# View to fetch transactions for a specific stock symbol


@login_required
def transactions_view(request, stock_symbol):
    user_id = request.user.id

    # Raw SQL to fetch transactions based on stock symbol and user
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

    # Structure transactions as JSON data
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

                    # # Then, update or insert into portfolio table
                    # cursor.execute(
                    #     """
                    #     INSERT INTO portfolio (user_id, stock_symbol, total_quantity)
                    #     VALUES (%s, %s, %s)
                    #     ON CONFLICT (user_id, stock_symbol) 
                    #     DO UPDATE SET total_quantity = portfolio.total_quantity + %s
                    #     """,
                    #     [
                    #         user_id,
                    #         data["stock_symbol"],
                    #         (
                    #             data["quantity"]
                    #             if data["purchase_type"] == "BUY"
                    #             else -data["quantity"]
                    #         ),
                    #         (
                    #             data["quantity"]
                    #             if data["purchase_type"] == "BUY"
                    #             else -data["quantity"]
                    #         ),
                    #     ],
                    # )

                messages.success(request, "Stock transaction added successfully.")
                return redirect("portfolio")

            except Exception as e:
                messages.error(request, "Error adding transaction. Please try again.")
    else:
        form = AddStockTransactionForm()

    return render(request, "users/add_stocks.html", {"form": form})

