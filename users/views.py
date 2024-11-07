import json
from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

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
    api_key = "KMSX2N60VHYWHGYR"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    try:
        price = float(data["Global Quote"]["05. price"])
        change = float(data["Global Quote"]["09. change"])
        change_percent = float(
            data["Global Quote"]["10. change percent"].replace("%", "")
        )
    except (KeyError, ValueError):
        price, change, change_percent = 0.0, 0.0, 0.0  # Fallback values

    # Return formatted data
    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_percent": change_percent,
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
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"stock_data": stock_data})

    print(symbols)
    stock_data = [get_stock_data(symbol) for symbol in symbols]
    return render(request, "users/analytics.html", {"stock_data": stock_data})
    #return JsonResponse(stock_data, safe=False)


@login_required
@require_POST
def delete_stock(request, stock_symbol):
    user_id = request.user.id
    try:
        with connection.cursor() as cursor:
            # First delete all transactions for this stock
            cursor.execute(
                """
                DELETE FROM stock_transactions 
                WHERE user_id = %s AND stock_symbol = %s
            """,
                [user_id, stock_symbol],
            )

            # Then delete the stock from portfolio
            cursor.execute(
                """
                DELETE FROM portfolio 
                WHERE user_id = %s AND stock_symbol = %s
            """,
                [user_id, stock_symbol],
            )

        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_POST
def update_transaction(request, transaction_id):
    try:
        data = json.loads(request.body)
        user_id = request.user.id

        with connection.cursor() as cursor:
            # First get the stock symbol and verify ownership
            cursor.execute(
                """
                SELECT stock_symbol 
                FROM stock_transactions 
                WHERE transaction_id = %s AND user_id = %s
                """,
                [transaction_id, user_id],
            )
            result = cursor.fetchone()
            if not result:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Transaction not found or unauthorized",
                    },
                    status=404,
                )

            stock_symbol = result[0]

            # Perform update
            cursor.execute(
                """
                UPDATE stock_transactions 
                SET purchase_type = %s,
                    price = %s,
                    quantity = %s,
                    transaction_date = %s
                WHERE transaction_id = %s AND user_id = %s
                """,
                [
                    data["purchase_type"],
                    data["price"],
                    data["quantity"],
                    data["transaction_date"],
                    transaction_id,
                    user_id,
                ],
            )

        return JsonResponse(
            {
                "status": "success",
                "symbol": stock_symbol,
                "message": "Transaction updated successfully",
            }
        )

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@login_required
def portfolio_analytics(request):
    user_id = request.user.id

    # Initialize the list to hold profit/loss details for each stock
    profit_loss_list = []

    # Query 1: Calculate total quantity, average buy price, and average sell price per stock
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT stock_symbol,
                   SUM(CASE WHEN purchase_type = 'BUY' THEN quantity ELSE -quantity END) AS total_quantity,
                   AVG(CASE WHEN purchase_type = 'BUY' THEN price END) AS avg_buy_price,
                   AVG(CASE WHEN purchase_type = 'SELL' THEN price END) AS avg_sell_price
            FROM stock_transactions
            WHERE user_id = %s
            GROUP BY stock_symbol
        """, [user_id])

        stock_analytics = [
            {
                "stock_symbol": row[0],
                "total_quantity": row[1],
                "avg_buy_price": row[2] if row[2] else 0.0,
                "avg_sell_price": row[3] if row[3] else 0.0,
            }
            for row in cursor.fetchall()
        ]

    # Query 2: Nested query to identify top traded stocks by frequency
    min_trades = 5  # Set the minimum trade count threshold
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT stock_symbol, trade_count
            FROM (
                SELECT stock_symbol, COUNT(*) AS trade_count
                FROM stock_transactions
                WHERE user_id = %s
                GROUP BY stock_symbol
            ) AS stock_trades
            WHERE trade_count >= %s
            ORDER BY trade_count DESC
        """, [user_id, min_trades])

        top_traded_stocks = [
            {
                "stock_symbol": row[0],
                "trade_count": row[1],
            }
            for row in cursor.fetchall()
        ]

    # Get all unique stock symbols for the user
    share_name = StockTransaction.objects.filter(user_id=user_id).values_list('stock_symbol', flat=True).distinct()

    for sname in share_name:  # For each unique stock symbol
        # Initialize counters
        qty_sold = 0
        total_sell_price = 0
        costprice = 0
        remaining_qty_to_sell = 0

        # Get all transactions for this stock symbol
        transactions = StockTransaction.objects.filter(user_id=user_id, stock_symbol=sname)

        # Calculate total quantity sold and total sell price
        for transaction in transactions.filter(purchase_type='SELL'):
            qty_sold += transaction.quantity
            total_sell_price += transaction.price * transaction.quantity
            remaining_qty_to_sell = qty_sold

        # Calculate the cost price based on FIFO
        for transaction in transactions.filter(purchase_type='BUY'):
            if remaining_qty_to_sell > 0:
                quantity = transaction.quantity
                price = transaction.price
                if remaining_qty_to_sell < quantity:
                    costprice += remaining_qty_to_sell * price
                    remaining_qty_to_sell = 0
                else:
                    costprice += quantity * price
                    remaining_qty_to_sell -= quantity

        # Calculate profit or loss if any shares were sold
        if qty_sold > 0:
            avg_sell_price = total_sell_price / qty_sold  # Average sell price
            total_price = qty_sold * avg_sell_price  # Total revenue from selling
            profit_loss = total_price - costprice  # Profit/Loss from the sale

            # Add the results to the profit_loss_list
            profit_loss_list.append({
                "stock_symbol": sname,
                "total_sell_price": total_sell_price,
                "total_cost_price": costprice,
                "realized_profit_loss": profit_loss,
                "qty_sold": qty_sold
            })

    # Combine all context data
    context = {
        "stock_analytics": stock_analytics,
        "top_traded_stocks": top_traded_stocks,
        "profit_loss_list": profit_loss_list,
    }

    return render(request, "users/portfolio_analytics.html", context)