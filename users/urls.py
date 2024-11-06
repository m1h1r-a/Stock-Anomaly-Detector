from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("analytics/", views.stock_data_api, name="stock_data_api"),
    path("portfolio/", views.portfolio_view, name="portfolio"),
    path(
        "transactions/<str:stock_symbol>/", views.transactions_view, name="transactions"
    ),
    path("delete-stock/<str:stock_symbol>/", views.delete_stock, name="delete_stock"),
    path(
        "portfolio/add-stocks/",
        views.add_stock_transaction,
        name="add_stock_transaction",
    ),
    # path('api/stock-data/', views.stock_data_api, name='stock_data_api'),
]
