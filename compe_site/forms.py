from django.contrib.auth.forms import AuthenticationForm,UserCreationForm# 追加
from django.core.validators import FileExtensionValidator
from django import forms

from .models import User,CSV

class LoginFrom(AuthenticationForm):
    class Meta:
        model = User

class CsvForm(forms.Form):
    file = forms.FileField(label='CSVファイル',validators=[FileExtensionValidator(['csv'])])

#formをforms.Formkらforms.ModelFormにすると、なぜかValidationエラーになりis_validを突破できない。
#modelformじゃないとupload_toを指定できない
class CsvModelForm(forms.ModelForm):
    class Meta:
        model = CSV
        fields = ['csv']

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "account_id",
            "email",
            # "first_name",
            # "last_name",
            # "birth_date",
        )