from django.urls import path

from . import views

app_name = "compe_site"

urlpatterns = [
    path("", views.RankingView, name="index"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path("ranking/",views.RankingView,name="ranking"),
    path("postresult/",views.upload_result,name="post_result"),
]