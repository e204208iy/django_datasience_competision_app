from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView,CreateView
from .forms import LoginFrom
from django.contrib.auth.views import LoginView as BaseLoginView, LogoutView as BaseLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
import pandas as pd
from .forms import CsvForm,SignUpForm,CsvModelForm
from .models import Ranking
from django.conf import settings
import datetime
from sklearn.metrics import accuracy_score
import os

class IndexView(LoginRequiredMixin,TemplateView):
    template_name = "compe_site/ranking.html"
    login_url = '/login/'

def RankingView(request):
    top_rankings = Ranking.objects.order_by('-score')[:20]  # スコアが高い順に10件取得
    context = {'top_rankings': top_rankings}
    print(context)
    return render(request, 'compe_site/ranking.html',context)

class SignupView(CreateView):
    """ ユーザー登録用ビュー """
    form_class = SignUpForm # 作成した登録用フォームを設定
    template_name = "compe_site/signup.html" 
    success_url = reverse_lazy("compe_site:index") # ユーザー作成後のリダイレクト先ページ

    def form_valid(self, form):
        # ユーザー作成後にそのままログイン状態にする設定
        response = super().form_valid(form)
        account_id = form.cleaned_data.get("account_id")
        password = form.cleaned_data.get("password1")
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response

class LoginView(BaseLoginView):
    form_class = LoginFrom
    template_name = "compe_site/login.html"

class LogoutView(BaseLogoutView):
    success_url = reverse_lazy("compe_site:index")

csv_folder_path = f"{settings.MEDIA_ROOT}/compe_site/users_csv"  # フォルダのパスを指定

def upload_result(request):
    #正解データを用意
    ture_df = pd.read_csv(f"{settings.MEDIA_ROOT}/correct_data/result.csv")
    true = ture_df["answer"].values.astype("int8") [:10] 
    if request.method == 'POST':
        form = CsvForm(request.POST,request.FILES)
        # form = CsvModelForm(request.POST,request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            pred_df = pd.read_csv(csv_file)
            user_csv_folder_path = os.path.join(csv_folder_path,request.user.account_id)

            if not os.path.exists(user_csv_folder_path):
                os.makedirs(user_csv_folder_path)
                pred_df.to_csv(f'{user_csv_folder_path}/{request.user.account_id}_{datetime.datetime.now()}.csv')
            else:
                print(f'{user_csv_folder_path}/{request.user.account_id}_{datetime.datetime.now()}.csv')
                pred_df.to_csv(f'{user_csv_folder_path}/{request.user.account_id}_{datetime.datetime.now()}.csv')

            pred = pred_df["answer"].values.astype("int8") [:10] 
            #numpy配列が空の場合accuracy_scoreが計算できない
            if pred.size == 0:
                print("空でした")
                return redirect('compe_site:ranking')  
            else:
                score = accuracy_score(true, pred) #実際のスコアの計算

            new_score = score * 100

            # Rankingモデルに存在する学籍番号を取得
            existing_student = Ranking.objects.filter(account_id=request.user.account_id).first()
            print(existing_student)
            # Rankingモデルにデータがある場合はScoreが大き方を保存、ない場合は追加
            if existing_student:
                if existing_student.score < new_score:
                    existing_student.score = new_score
                    existing_student.save()
                else:
                    # 既存の成績が大きい場合は新しいデータを無視
                    print('既存の成績が高いため、新しいデータを追加しませんでした。')
            else:
                # 学籍番号が存在しない場合は新しいデータを追加
                new_account = Ranking(account_id=request.user.account_id, score=new_score)
                new_account.save()
            
            return redirect('compe_site:ranking')  # ランキングページにリダイレクト
        else:
           print(form.errors.as_data())
           print("ダメです")
    else:
        form = CsvForm()

    return render(request, 'compe_site/post_result.html', {'form': form})