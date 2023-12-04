"""hello_world URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from hello_world.core import views as core_views

urlpatterns = [
    path("", core_views.index),
    # 启动搜索任务
    path("api/RunSearchApi", core_views.RunSearchApi),
    # 停止搜索任务
    path("api/StopSearchApi", core_views.StopSearchApi),
    # 获取搜索任务列表
    path("api/GetSearchListApi", core_views.GetSearchListApi),
    # 获取搜索任务对应的搜索数据
    path("api/GetSearchqueryApi", core_views.GetSearchqueryApi),
    # 基于es的uuid查询数据
    path("api/SearchEsdataApi", core_views.EsDataApi),
    # 下一次搜索不需要requests_save
    path("api/JudgmentApi", core_views.JudgmentApi),
    # 获取全部未研判的数据
    path("api/GetAllJudgmentApi", core_views.GetJudgmentDataApi),
    # 获取某条需要研判的数据es的uuid
    path("api/GetJudgmentApi", core_views.GetJudgmentEsUuidApi),
    path("admin/", admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
]
