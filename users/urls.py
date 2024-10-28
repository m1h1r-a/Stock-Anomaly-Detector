from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("", views.home, name="home"),
    path("dashbaord/", views.dashboard, name="dashboard"),
    path("analytics/", views.analytics, name="analytics"),
    path('portfolio/', views.portfolio_view, name='portfolio'),
    path('transactions/<str:stock_symbol>/', views.transactions_view, name='transactions'),
]
