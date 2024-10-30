from django import forms
from django.contrib.auth.models import User

from .models import StockTransaction


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",  # Bootstrap classes
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Password"}
        )
    )


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Password"}
        )
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Confirm Password"}
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control mb-3", "placeholder": "Username"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control mb-3", "placeholder": "Email"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")


class AddStockTransactionForm(forms.Form):
    purchase_type = forms.ChoiceField(
        choices=[("BUY", "Buy"), ("SELL", "Sell")], label="Purchase Type"
    )
    price = forms.DecimalField(max_digits=10, decimal_places=2, label="Price")
    quantity = forms.IntegerField(label="Quantity")
    stock_symbol = forms.CharField(max_length=30, label="Stock Symbol")
    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}), label="Transaction Date"
    )
