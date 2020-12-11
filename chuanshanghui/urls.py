#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.urls import path
import chuanshanghui.views as views
from django.conf import settings
from django.conf.urls.static import static

app_name = "chuanshanghui"
urlpatterns = [
    path('login/', views.login, name='login'),  # 登录（用于跳转的时候）
    path('index/', views.index, name='index'),  # 首页
    path('index_banner/', views.index_banner.as_view(), name='index_banner'),
    path('index_dp_details/', views.index_dp_details, name='index_dp_details'),
    path('logout/', views.logout, name='logout'),  # 登出
    path('userInfo/', views.userInfoView.as_view(), name='userInfo'),  # 个人中心
    path('info_changePassword/', views.info_changePassword, name='changePwd'),  # 个人中心-修改密码
    path('info_changeInfo/', views.info_changeInfo, name='changeInfo'),  # 个人中心-修改信息
    path('fund_apply/', views.fund_apply, name="fund_apply"),
    path('fund_apply/_fundapply_check', views.fundapply_check, name='fund_apply_state_create'),
    path('fund_apply_list/', views.fund_apply_list, name='fund_apply_list'),
    path('fund_apply_list/fund_apply_state/', views.fund_apply_state, name="fund_apply_state"),
    path('fund_apply_list/fund_apply_singleDel/', views.fund_apply_singleDel, name='fund_apply_singleDel'),
    path('fund_apply_list/fund_apply_AllDel/', views.fund_apply_AllDel, name='fund_apply_AllDel'),
    path('fund_apply_list/queryByName/',views.queryByName, name='queryByName'),
    path("fund_apply_list/banggongshi_checkFundApply/",views.banggongshi_checkFundApply, name='banggongshi_checkFundApply'),
    path('admin_list/', views.admin_list, name="admin_list"),
    path('admin_add/', views.admin_add, name="admin_add"),
    path('money_add/', views.money_add, name='money_add'),
    path('money_list/', views.money_list, name="money_list"),
    # 2020-12-07 辜丽娟
    path('money_look/', views.money_look, name='money_look'),
    path('money_apply/', views.money_apply, name='money_apply'),
    path('money_list/', views.money_list, name="money_list"),
    path('classroom_list/', views.classroom_list, name="classroom_list"),
    path('classroom_apply/', views.classroom_apply, name="classroom_apply"),
    path('classroom_apply_check/', views.classroomapply_check, name="classroom_apply_check"),
    # 部门成员信息
    path('dpmembers_list/', views.dpmembers_list, name="dpmembers_list"),  # 列表展示
    path('dpmembers_add/', views.dpmembers_add, name="dpmembers_add"),  # 新增
    # 部门
    path('dpmembers_list/', views.dpmembers_list, name="dpmembers_list"),  # 部门成员信息列表展示
    path('dpmembers_add/', views.dpmembers_add, name="dpmembers_add"),  # 新增
    path('a_success/', views.a_success, name="a_success"),  # 提交成功
    path('dpmembers_del/', views.dpmembers_del),  # 删除
    path('dpmembers_edit/', views.dpmembers_edit),  # 编辑
    path('dpmembers_read/', views.dpmembers_read),  # 详情
    path('export_excel/', views.export_excel, name="export_excel"),  # 导出Excel
    path('dp_list/', views.dp_list, name="dp_list"),  # 部门信息列表展示
    path('dp_edit/', views.dp_edit, name="dp_edit"),  # 部门介绍修改
    # path('dp_leaders/', views.dp_leaders, name="dp_leaders"),  # 部长信息展示# 活动信息
    path('article_list/', views.article_list.as_view(), name="article_list"),
    path('article_delete/', views.ArticleDeleteView.as_view(), name="article_delete"),
    path('artilce_detail/<int:article_num>', views.ArticleUpdateView.as_view(), name='article_detail'),
    path('article_add/', views.ArticleAddView.as_view(), name='article_add'),
    path('article_reget/', views.ArticleRegetView.as_view(), name='article_reget'),
    path('article_read/', views.article_read, name='article_read'),
    # 部门对接
    path('cooperation_alist/', views.cooperation_alist, name="cooperation_alist"),  # 部门对接列表展示发布任务
    path('cooperation_blist/', views.cooperation_blist, name="cooperation_blist"),  # 部门对接列表展示接收任务
    path('cooperation-add/', views.cooperation_add, name="cooperation_add"),  # 新增部门对接任务
    path('cooperation_read/', views.cooperation_read, name="cooperation_read")  # 展开部门对接任务详细信息]
]
