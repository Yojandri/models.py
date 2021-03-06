#!/usr/bin/python
# -*- coding: utf-8 -*-
# Create your views here.
import json

from django.core.serializers import serialize
from django.db.models import F, Q
from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from chuanshanghui.models import FundRecord, Reimbursement, DpMembers, ActivityInfo, People, Department,Goodslist, Cooperation, Article, ClassroomRecord, Classroom
from datetime import datetime, timedelta
from django import forms
from django.conf import settings
from utils import pagination

from utils import constants
from utils import json_res
from utils.json_res import json_response, Code
from .form import changeInfoForm, changePwdForm, ArticleForm

from django.core.files.storage import FileSystemStorage
import os,re

# Django 自带的分页功能不满足需求，所以选择自定义分页功能，将下面两行代码注释掉
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
# from django.views.generic import ListView
from django.core.files.uploadedfile import SimpleUploadedFile

import pymysql

from io import BytesIO    # 2.实现在内存中读写bytes
import xlwt
# ——————————————————————————————————设置命名空间—————————————————————————————————————————————————
name = "chuanshanghui"


def login(request):#登录
    if request.session.get('is_login', None):
        return redirect("/chuanshanghui/index/")

    if request.method == "GET":
        if 'usernum' in request.COOKIES and 'password' in request.COOKIES:
            usernum =request.COOKIES.get('usernum')
            password =request.COOKIES.get('password')
            checked = 'checked'
        else:
            usernum = ''
            checked = ''
            password=''
        return render(request,
                      'login.html',
                      {'usernum': usernum, 'checked': checked, 'password': password})

    elif request.method == "POST":
        usernum = request.POST.get('usernum')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        people = People.objects.filter(stu_num=usernum)

        if not people.exists():
            message = '账户不存在'
            return render(request, 'login.html', {'message': message, })


        person=people.last()

        if person.password == password:
            request.session['is_login'] = True
            request.session['person_num'] = person.stu_num
            request.session['person_name'] = person.stu_name
            response = redirect('/chuanshanghui/index/')
            if remember == 'on':
                response.set_cookie('usernum',usernum, expires=datetime.now() + timedelta(days=14))
                response.set_cookie('password',password,expires=datetime.now() + timedelta(days=14))
            return response
        else:
            message='密码错误'
            return render(request,'login.html',{'message': message,})


def index(request):#首页
    if not request.session.get('is_login', None):
        return render(request, '404.html')
    else:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        # 获取当前页码数
        if request.GET.get('page'):
            apage_num = int(request.GET.get('page'))
        else:
            # 如果没有指明页码数，默认为第一页（首页）
            apage_num = 1
        # 计算当前页面需要展示的数据量，以及位置（第几个-第几个）
        adata_start = (apage_num - 1) * 6
        adata_end = apage_num * 6
        # 计算总体数据量
        atotal_count = Article.objects.all().count()
        # 说明一页展示多少个数据
        aper_page = 6
        # 展示需要的总页数以及是否有剩余
        atotal_page, aplus = divmod(atotal_count, aper_page)
        if aplus:
            atotal_page += 1
        # 页面最多展示页码数（1、2、3；2、3、4）
        amax_page = 3
        ahalf_max_page = amax_page // 2
        # 页面上展示的页码的开始页
        apage_start = apage_num - ahalf_max_page
        # 页面上展示的页码的结束页
        apage_end = apage_num + ahalf_max_page
        if apage_start <= 1:
            apage_start = 1
            apage_end = amax_page
        if apage_end > atotal_page:
            apage_end = atotal_page
            apage_start = atotal_page - amax_page + 1
        if apage_start<=1:
            apage_start = 1
        news = Article.objects.only('article_num', 'article_name', 'article_release_time').filter(
            article_is_delete=False).order_by('-article_release_time')[adata_start:adata_end]
        ahtml_list = []
        for i in range(apage_start, apage_end + 1):
            tmp = '<a href="/chuanshanghui/index/?page={0}">{0}</a><span> <span>'.format(i)
            ahtml_list.append(tmp)
        apage_html = "".join(ahtml_list)
        #获取当前页码数
        if request.GET.get('dppage'):
            dppage_num = int(request.GET.get('dppage'))
        else:
            #如果没有指明页码数，默认为第一页（首页）
            dppage_num = 1
        #计算当前页面需要展示的数据量，以及位置（第几个-第几个）
        dpdata_start = (dppage_num - 1) * 4
        dpdata_end = dppage_num * 4
        # 计算总体数据量
        dptotal_count = Department.objects.all().count()
        #说明一页展示多少个数据
        dpper_page = 4
        #展示需要的总页数以及是否有剩余（14/4=3页，余2个）
        dptotal_page, dpplus = divmod(dptotal_count, dpper_page)
        if dpplus:
            dptotal_page += 1
        #页面最多展示页码数（1、2、3；2、3、4）
        dpmax_page = 3
        dphalf_max_page = dpmax_page//2
        # 页面上展示的页码的开始页
        dppage_start = dppage_num - dphalf_max_page
        # 页面上展示的页码的结束页
        dppage_end = dppage_num + dphalf_max_page
        if dppage_start <= 1:
            dppage_start = 1
            dppage_end = dpmax_page
        if dppage_end > dptotal_page:
            dppage_end = dptotal_page
            dppage_start = dptotal_page - dpmax_page +1
        if dppage_start <=1:
            dppage_start = 1
        dpintro = Department.objects.all()[dpdata_start:dpdata_end]
        dphtml_list = []
        for i in range(dppage_start, dppage_end + 1):
            tmp = '<a href="/chuanshanghui/index/?dppage={0}">{0}</a><span> <span>'.format(i)
            dphtml_list.append(tmp)
        dppage_html = "".join(dphtml_list)
        return render(request,'index.html',{'person':person,'news':news,
                                            'apage_html':apage_html,
                                            'dpintro':dpintro,'dppage_html':dppage_html,
                                            'dptotal_page':dptotal_page, 'atotal_page':atotal_page,
                                            'apage_num':apage_num, 'dppage_num':dppage_num})

def index_dp_details(request):#部门展示
    if not request.session.get('is_login', None):
        return render(request,'404.html')
    else:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        dpintro = Department.objects.only('dp_num','dp_name','dp_image', 'dp_presentetion').order_by('dp_num')
        return render(request,'index_dp_details.html',{'person':person,'dpintro':dpintro})

class index_banner(View):
    def get(self,request):
        banners = Article.objects.values('article_image','article_num','article_name').annotate(
            article_title=F('article_name')).filter(article_is_delete=False).filter(~Q(article_image='')).order_by('-article_release_time')[:constants.SHOW_BANNER_COUNT]
        data = {'banners':list(banners)}
        return json_res.json_response(data=data)

def article_read(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()
    article_num = request.GET.get('article_num')
    article = Article.objects.get(article_num=article_num)
    dpmembers = DpMembers.objects.get(stu_num=article.stu_num)
    department = Department.objects.filter(dp_num=dpmembers.dp_num.dp_num).first()
    hitcount = article.article_hit
    hitcount += 1
    article.article_hit = hitcount
    article.save()
    return render(request, 'article_read.html', {'article' : article,'person': person, 'department' : department})


def logout(request):#退出
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    request.session.flush()
    return redirect("/chuanshanghui/login/")


class userInfoView(View):#显示个人信息
    def get(self,request):
        if not request.session.get('is_login', None):
            return render(request, '404.html')
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        dpmember = (DpMembers.objects.filter(stu_num=usernum)).last()
        dpnum = dpmember.dp_num_id
        department = (Department.objects.filter(dp_num=dpnum)).last()
        return render(request,'info_user.html',{'person':person, 'dpmember':dpmember,'department':department})


def info_changePassword(request):#修改密码
    if not request.session.get('is_login', None):
        return render(request,'404.html')

    if request.method == 'POST':
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        changePwd_form = changePwdForm(request.POST)
        if changePwd_form.is_valid():
            changePwd_cd = changePwd_form.cleaned_data
            print(changePwd_cd['password'],person.password,changePwd_cd['new_password'],changePwd_cd['renew_password'])
            if changePwd_cd['password'] == person.password:
                if changePwd_cd['new_password'] == changePwd_cd['renew_password']:
                    if changePwd_cd['new_password'] != changePwd_cd['password']:
                        person.password = changePwd_cd['new_password']
                        person.save()
                        return HttpResponse('修改成功！')

                    else:
                        return render(request,'info_changePassword.html',{'message':'新密码应与旧密码不同！'})
                else:
                    return render(request,'info_changePassword.html',{'message':'两次输入密码不一致！'})
            else:
                return render(request,'info_changePassword.html',{'message':'原密码错误，请重新输入！'})
        else:
            return render(request,'info_changePassword.html',{'message':'表单无效，请重新输入！'})
    else:
        return render(request,'info_changePassword.html')


def info_changeInfo(request):  # 修改个人信息
    if not request.session.get('is_login', None):
        return render(request, '404.html')

    if request.method == 'POST':
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        changeInfo_form = changeInfoForm(request.POST)
        if changeInfo_form.is_valid():
            changeInfo_cd = changeInfo_form.cleaned_data
            if changeInfo_cd['renew_stucollege'] != '':
                person.stu_college = changeInfo_cd['renew_stucollege']
            if changeInfo_cd['renew_stumajor'] != '':
                person.stu_major = changeInfo_cd['renew_stumajor']
            person.stu_class = changeInfo_cd['renew_stuclass']
            person.stu_phone = changeInfo_cd['renew_stuphone']
            person.stu_qq = changeInfo_cd['renew_stuqq']
            person.stu_email = changeInfo_cd['renew_stuemail']
            person.save()
            return HttpResponse('修改成功')
        else:
            return render(request,'info_changeInfo.html',{'message': '修改失败'})
    else:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        return render(request, 'info_changeInfo.html', {'person': person})


# ————————————————————————————————————————资金管理————————————————————————————————————————————
def fundapply_check(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")

    # 如果检验通过，则运行下面的代码
    try:
        if request.method == "POST":
            # 获取前端POST过来的数据
            # 处理上传的文件
            invoice = request.FILES.get('fund_apply_file')
            reim_to = request.POST.get("reim_to")
            fund_for_dp = request.POST.get("fund_for_dp")
            fund_for_act = request.POST.get("fund_for_act")
            fund_pincharge = request.POST.get("fund_pincharge")
            stu_name = request.POST.get("stu_name")
            reim_amount = request.POST.get("reim_amount")
            fund_for_matt = request.POST.get("fund_for_matt")  # 如何获取多个值2020-12-13
            fund_for_matt_plus = request.POST.get('fund_for_matt_plus')
            print(fund_for_matt_plus)
            fund_for_matt = fund_for_matt + '、' + fund_for_matt_plus
            try:
                # 实例化报账对象
                reimbursement = Reimbursement()
                reim_to_ = Department(dp_num=reim_to)
                # 处理reim_to字段
                reimbursement.reim_to = reim_to_
                # 处理fund_pincharge字段
                reimbursement.fund_pinchrage = fund_pincharge
                # 处理reim_state字段
                reimbursement.reim_state = "未审核"
                reim_state = reimbursement.reim_state

                reimbursement.invo_appendix = invoice
                print(reimbursement.invo_appendix)

                # 保存一个reimbursement记录
                reimbursement.save()

                # 实例化资金对象
                fundrecord = FundRecord()

                # 处理fund_for_dp字段
                # Department实例
                fund_for_dp_ = Department(dp_num=fund_for_dp)
                fundrecord.fund_for_dp = fund_for_dp_

                # 处理fund_for_act字段
                fund_for_act_ = ActivityInfo(act_num=fund_for_act)
                fundrecord.fund_for_act = fund_for_act_

                # 处理fund_for_matt字段
                fundrecord.fund_for_matt = fund_for_matt

                # 处理fund_amount字段
                fundrecord.fund_amount = reim_amount

                # 处理reim_to字段
                reim_to_ = Department(dp_num=reim_to)

                # 处理reim_num字段
                reim_num = reimbursement.reim_num
                fundrecord.reim_num_id = reim_num

                # 保存一条fundrecord记录
                fundrecord.save()

                ff_act = ActivityInfo.objects.get(act_num=fund_for_act)
                fund_for_act = ff_act.act_name
                dp = Department.objects.get(dp_num=fund_for_dp)
                fund_for_dp = dp.dp_name

                reim_to_dp = Department.objects.get(dp_num=reim_to)
                reim_to = reim_to_dp.dp_name

                dp_member = People.objects.get(stu_num=fund_pincharge)

                if dp_member.stu_name == stu_name:
                    return render(request, "_fundapply_check.html", {"reim_to": reim_to,
                                                                     "fund_for_dp": fund_for_dp,
                                                                     "fund_for_act": fund_for_act,
                                                                     "fund_pincharge": fund_pincharge,
                                                                     "stu_name": stu_name,
                                                                     "reim_amount": reim_amount,
                                                                     "fund_for_matt": fund_for_matt,
                                                                     'person': person,
                                                                     'reim_state':reim_state
                                                                     })
                else:
                    return HttpResponse("部门成员身份验证不通过，请联系系统管理员进行身份验证。")
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("页面找不到了 404")
    except:
        HttpResponse('''数据保存出错！''')


# 从审核列表点击查看单个报账申请的状态
def fund_apply_state(request):
    nid = request.GET.get("nid")
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union',
                           charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM chuanshanghui_fundrecord WHERE fund_num = %s", [nid])
    fundrecord = cursor.fetchall()
    reim_num = fundrecord[0]['reim_num_id']
    act_num = fundrecord[0]['fund_for_act_id']
    fund_for_dp_id = fundrecord[0]['fund_for_dp_id']

    cursor.execute("SELECT * FROM chuanshanghui_reimbursement WHERE reim_num = %s", [reim_num])
    reimbursement = cursor.fetchall()
    reim_to = reimbursement[0]['reim_to_id']
    fundpincharge = reimbursement[0]['fund_pinchrage']

    cursor.close()
    conn.close()
    fundrecord = FundRecord.objects.get(fund_num=fundrecord[0]['fund_num'])
    stu = People.objects.get(stu_num=fundpincharge)
    act = ActivityInfo.objects.get(act_num=act_num)
    adp = Department.objects.get(dp_num=fund_for_dp_id)
    bdp = Department.objects.get(dp_num=reim_to)
    if reimbursement[0]['reim_state'] == '未审核':
        color = 'red'
    elif reimbursement[0]['reim_state'] == '已审核，已通过':
        color = 'green'
    else:
        color = 'blue'
    return render(request, "_fundapply_check_ok.html", {'fundrecord': fundrecord,
                                                        'reimbursement': reimbursement[0],
                                                        'stu': stu,
                                                        'act': act,
                                                        'adp': adp,
                                                        'bdp': bdp,
                                                        'color': color
                                                        })


def fund_apply(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    else:
        dp_bangongshi = Department.objects.filter(dp_num='08')
        dp_fundfor = Department.objects.all()
        activity = ActivityInfo.objects.all()
        fund_pincharge = DpMembers.objects.filter()
        goodslist = Goodslist.objects.all()

        return render(request, "fund_apply.html", {'person': person,
                                                   'dp_banggongshi': dp_bangongshi,
                                                   'dp_fundfor': dp_fundfor,
                                                   'activity': activity,
                                                   'goodslist':goodslist
                                                   })


def fund_apply_list(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    # 连接数据库，利用SQL查询语句获取后端数据库
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262",db='student_union', charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("""
    select DISTINCT 
    adp.dp_name as fund_for_dp, 
    bdp.dp_name as reim_to, 
    Fr.fund_num as fund_num,
    Fr.fund_for_matt as fund_for_matt, 
    Fr.fund_amount as fund_amount , 
    ai.act_name as fund_for_act, 
    Reim.reim_num as reim_num,
    Reim.fund_pinchrage as fund_pincharge, 
    Reim.apply_time as apply_time,
    pp.stu_name as stu_name,
    Reim.reim_state as reim_state
    from 
    chuanshanghui_fundrecord as Fr,
    chuanshanghui_department as adp,
    chuanshanghui_department as bdp,
    chuanshanghui_activityinfo as ai,
    chuanshanghui_reimbursement as Reim,
    chuanshanghui_dpmembers as dm,
    chuanshanghui_people as pp
    where
    # 连接Reimbursement和FundRecord表 Reim、Fr
    Reim.reim_num = Fr.reim_num_id
    AND
    # 连接ActivityInfo表 ai
    Fr.fund_for_act_id = ai.act_num
    AND
    # 连接存放发送申请部门信息的表 adp
    adp.dp_num = Fr.fund_for_dp_id
    AND
    # 连接存放接收申请部门信息的表 bdp
    bdp.dp_num = reim_to_id
    AND
    # 连接存放负责人信息的表 pp
    Reim.fund_pinchrage = pp.stu_num
    ORDER BY Reim.apply_time
    """)
    fundapplylist = cursor.fetchall()
    cursor.close()
    conn.close()

    page_info = pagination.PageInfo(request.GET.get("page"), len(fundapplylist), 5, 5, 'http://127.0.0.1:8000/chuanshanghui/fund_apply_list/')
    count = len(fundapplylist)
    print(count)
    fundapplylist = fundapplylist[page_info.start():page_info.end()]
    return render(request, "fund_apply_list.html", {'fundapplylist': fundapplylist, 'count': count, 'page_info': page_info})


def queryByName(request):  # 2020-12-05 创建该函数
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    try:
        if request.method == 'GET':
            dp_Name = request.GET.get("dp_Name")
            # 连接数据库，利用SQL查询语句获取后端数据库
            conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union',
                                   charset='utf8')
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute("""
                select DISTINCT 
                adp.dp_name as fund_for_dp, 
                bdp.dp_name as reim_to, 
                Fr.fund_num as fund_num,
                Fr.fund_for_matt as fund_for_matt, 
                Fr.fund_amount as fund_amount , 
                ai.act_name as fund_for_act, 
                Reim.reim_num as reim_num,
                Reim.fund_pinchrage as fund_pincharge, 
                Reim.apply_time as apply_time,
                pp.stu_name as stu_name,
                Reim.reim_state as reim_state
                from 
                chuanshanghui_fundrecord as Fr,
                chuanshanghui_department as adp,
                chuanshanghui_department as bdp,
                chuanshanghui_activityinfo as ai,
                chuanshanghui_reimbursement as Reim,
                chuanshanghui_dpmembers as dm,
                chuanshanghui_people as pp
                where
                # 连接Reimbursement和FundRecord表 Reim、Fr
                Reim.reim_num = Fr.reim_num_id
                AND
                # 连接ActivityInfo表 ai
                Fr.fund_for_act_id = ai.act_num
                AND
                # 连接存放发送申请部门信息的表 adp
                adp.dp_num = Fr.fund_for_dp_id
                AND
                # 连接存放接收申请部门信息的表 bdp
                bdp.dp_num = reim_to_id
                AND
                # 连接存放负责人信息的表 pp
                Reim.fund_pinchrage = pp.stu_num
                AND 
                pp.stu_name = %s
                ORDER BY Reim.apply_time
                """, [dp_Name])
            fundapplylist = cursor.fetchall()
            cursor.close()
            conn.close()
            from utils import pagination_query
            page_info = pagination_query.PageInfo(request.GET.get("page"), len(fundapplylist), 3, 5,
                                            'http://127.0.0.1:8000/chuanshanghui/fund_apply_list/queryByName/', dp_Name, 'dp_Name')
            count = len(fundapplylist)
            print(count)
            fundapplylist = fundapplylist[page_info.start():page_info.end()]
            return render(request, 'fund_apply_list.html', {'fundapplylist': fundapplylist, 'count': count, 'page_info': page_info})
        else:
            return HttpResponse("请重新输入查询词！")
    except:
        return HttpResponse("查询出错了，请检查你输入的查询词！")


def queryByDp(request):  # 2020-12-05 创建该函数
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    try:
        if request.method == 'GET':
            dp = request.GET.get("dp")
            # 连接数据库，利用SQL查询语句获取后端数据库
            conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union',
                                   charset='utf8')
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
            cursor.execute("""
                select DISTINCT 
                adp.dp_name as fund_for_dp, 
                bdp.dp_name as reim_to, 
                Fr.fund_num as fund_num,
                Fr.fund_for_matt as fund_for_matt, 
                Fr.fund_amount as fund_amount , 
                ai.act_name as fund_for_act, 
                Reim.reim_num as reim_num,
                Reim.fund_pinchrage as fund_pincharge, 
                Reim.apply_time as apply_time,
                pp.stu_name as stu_name,
                Reim.reim_state as reim_state
                from 
                chuanshanghui_fundrecord as Fr,
                chuanshanghui_department as adp,
                chuanshanghui_department as bdp,
                chuanshanghui_activityinfo as ai,
                chuanshanghui_reimbursement as Reim,
                chuanshanghui_dpmembers as dm,
                chuanshanghui_people as pp
                where
                # 连接Reimbursement和FundRecord表 Reim、Fr
                Reim.reim_num = Fr.reim_num_id
                AND
                # 连接ActivityInfo表 ai
                Fr.fund_for_act_id = ai.act_num
                AND
                # 连接存放发送申请部门信息的表 adp
                adp.dp_num = Fr.fund_for_dp_id
                AND
                # 连接存放接收申请部门信息的表 bdp
                bdp.dp_num = reim_to_id
                AND
                # 连接存放负责人信息的表 pp
                Reim.fund_pinchrage = pp.stu_num
                AND 
                adp.dp_name = %s
                ORDER BY Reim.apply_time
                """, [dp])
            fundapplylist = cursor.fetchall()
            cursor.close()
            conn.close()
            from utils import pagination_query
            page_info = pagination_query.PageInfo(request.GET.get("page"), len(fundapplylist), 3, 5,
                                            'http://127.0.0.1:8000/chuanshanghui/fund_apply_list/queryByDp/', dp, 'dp')
            count = len(fundapplylist)
            print(count)
            fundapplylist = fundapplylist[page_info.start():page_info.end()]
            return render(request, 'fund_apply_list.html', {'fundapplylist': fundapplylist, 'count': count, 'page_info': page_info})
        else:
            return HttpResponse("请重新输入查询词！")
    except:
        return HttpResponse("查询出错了，请检查你输入的查询词！")


def fund_apply_singleDel(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    try:
        if request.method == "GET" and request.GET:
            nid = request.GET.get("nid")
            conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union_',
                                   charset='utf8')
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

            cursor.execute("select * from chuanshanghui_fundrecord WHERE fund_num = %s", [nid])
            Onefundrecord = cursor.fetchall()
            cursor.close()
            conn.close()
            reim_num_id = Onefundrecord[0]['reim_num_id']
            FundRecord.objects.get(pk=nid).delete()
            Reimbursement.objects.get(pk=reim_num_id).delete()
            return redirect('chuanshanghui:fund_apply_list')
    except:
        print('''删除数据出错！''')


def fund_apply_AllDel(request):  # 批量删除
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()

    # 检验登陆状态
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    try:
        if request.method == 'GET' and request.GET:
            count = request.GET.get('count')
            print(count)
            # 建立数据库连接
            conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union',
                                   charset='utf8')
            # 建立索引
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

            # 获取报账项的ID
            cursor.execute('SELECT reim_num_id FROM chuanshanghui_fundrecord')
            reim_nums = cursor.fetchall()
            # print(reim_nums)
            # [{'reim_num_id': 60063}, {'reim_num_id': 60066}, {'reim_num_id': 60067}, {'reim_num_id': 60068},
            #  {'reim_num_id': 60073}, {'reim_num_id': 60074}]

            # 获取资金项的ID
            cursor.execute('SELECT fund_num FROM chuanshanghui_fundrecord')
            fund_nums = cursor.fetchall()
            # print(fund_nums)
            # [{'fund_num': 90005}, {'fund_num': 90008}, {'fund_num': 90015}, {'fund_num': 90016}, {'fund_num': 90009},
            #  {'fund_num': 90010}]
            # 关闭索引
            cursor.close()
            # 关闭数据库连接
            conn.close()

            # 由于获得的数据是对象列表，需要进行转换
            # 转换fund_nums
            fund_num = []
            for i in fund_nums:
                fund_num.append(i['fund_num'])

            # 转换reim_nums
            reim_num = []
            for i in reim_nums:
                reim_num.append(i['reim_num_id'])

            # 循环删除fundrecord中的数据记录
            for num in fund_num:
                FundRecord.objects.filter(fund_num=num).delete()

            # 循环删除reimbursement中的数据记录
            for num in reim_num:
                Reimbursement.objects.filter(reim_num=num).delete()

            # 设置提示信息
            sign = '已成功删除所有数据！'

            # 将提示信息渲染到前端，提示用户操作已经成功被执行
            return render(request, 'fund_apply_list.html', {'sign': sign})
    except:
        return HttpResponse('''删除数据出错！''')


def banggongshi_checkFundApply(request):  # 办公室审核其他部门提交的报账申请
    try:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()

        # 检验登陆状态
        if not request.session.get('is_login', None):
            # 如果本来就未登录，也就没有登出一说
            return redirect("/chuanshanghui/login/")
        if request.method == "GET":
            # 获取前端传来的nid和reim_state的值
            nid = int(request.GET.get("nid"))
            reim_state = Reimbursement.objects.get(reim_num__exact=nid).reim_state
            # 将获取得到的数据渲染至前端
            return render(request, "confirm.html", {'nid': nid, 'reim_state': reim_state})
    except Exception as e:
        return HttpResponse(e)

# 审核并通过
def allow_apply(request):
    try:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()

        # 检验登陆状态
        if not request.session.get('is_login', None):
            # 如果本来就未登录，也就没有登出一说
            return redirect("/chuanshanghui/login/")

        if request.method == 'GET':
            nid = request.GET.get('nid')
            reim_state = Reimbursement.objects.get(reim_num__exact=nid).reim_state
            if reim_state == '未审核':
                Reimbursement.objects.filter(reim_num__exact=nid).update(reim_state='已审核，已通过')
                # 修改审核状态
                reim_state = Reimbursement.objects.get(reim_num__exact=nid).reim_state
                return HttpResponse("<script>alert('操作成功！')</script>")
                # return redirect("/chuanshanghui/allow_apply/")
            # 如果已审核，在页面直接提示
            elif reim_state == '已审核，已通过':
                return HttpResponse("<script>alert('该申请已审核，申请结果为“通过”！')</script>")
            else:
                return HttpResponse('<script>alert("操作有误！")</script>')
    except Exception as e:
        return HttpResponse(e)


# 审核但不通过
def disallow_apply(request):
    try:
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()

        # 检验登陆状态
        if not request.session.get('is_login', None):
            # 如果本来就未登录，也就没有登出一说
            return redirect("/chuanshanghui/login/")

        if request.method == 'GET':
            nid = request.GET.get('nid')
            reim_state = Reimbursement.objects.get(reim_num__exact=nid).reim_state
            print(reim_state)
            if reim_state == '未审核':
                Reimbursement.objects.filter(reim_num__exact=nid).update(reim_state='已审核，未通过')
                # 修改审核状态
                reim_state = Reimbursement.objects.get(reim_num__exact=nid).reim_state
                return HttpResponse("<script>alert('操作成功！')</script>")
                # return redirect("/chuanshanghui/allow_apply/")
            # 如果已审核，在页面直接提示
            elif reim_state == '已审核，未通过':
                return HttpResponse("<script>alert('该申请已审核，申请结果为“未通过”！')</script>")
            else:
                return HttpResponse('<script>alert("操作有误！！")</script>')
    except Exception as e:
        return HttpResponse(e)


# —————————————————————————————————————————资金管理结束———————————————————————————————————————————


def admin_add(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    return render(request, 'admin-add_new.html', {'person': person})


def admin_list(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/chuanshanghui/login/")
    return render(request, "admin-list.html", {'person': person})


def money_list(request):  # 展示资金记录列表
    all_moneylist = FundRecord.objects.all().order_by('fund_num')  # 获取活动信息（单表）;降序
    return render(request, 'money-list.html', context={'all_moneylist': all_moneylist})  # 暂时只能实现单表查询


def money_apply(request):
    all_goodslist = Goodslist.objects.all().order_by('Goods_num')  # 获取活动信息（单表）;降序
    return render(request, 'money-apply.html', {'all_goodslist': all_goodslist})  # 暂时只能实现单表查询


# 2020-12-12
def money_add_form(request):
    try:
        act_list = ActivityInfo.objects.all()
        return render(request, 'money-add.html', {'act_list': act_list})
    except Exception as e:
        return HttpResponse("<script>alert('操作失败')</script>")


# 2020-12-12
def money_add(request):   # 增加资金项
    try:
        if request.method == "POST":
            Goods_for_act = request.POST.get('goodsfor_act')
            Goods_name = request.POST.get('Goodsname')
            Goods_price = int(request.POST.get('Goodsprice'))
            Goods_qua = int(request.POST.get('Goodsqua'))
            Goods_total = Goods_price * Goods_qua
            bei_zhu = request.POST.get('beizhu')
            Goodslist.objects.create(Goods_for_act_id=Goods_for_act, Goods_name=Goods_name, Goods_price=Goods_price,
                                     Goods_qua=Goods_qua, Goods_total=Goods_total, beizhu=bei_zhu)
            return redirect('/chuanshanghui/money_list')
        else:
            return render(request, 'money-add.html', {'message': "添加失败，请重试！"})
    except Exception as e:
        return HttpResponse("<script>alert('出现错误，请重试！')</script>")


def money_look(request):  # 展示资金明细
    all_goodslist = Goodslist.objects.all().order_by('Goods_num')  # 获取活动信息（单表）;降序
    count = all_goodslist.count()
    page_info = pagination.PageInfo(request.GET.get("page"), count, 5, 5, 'http://127.0.0.1:8000/chuanshanghui/money_look/')
    print(count)
    count_money = 0
    for row in all_goodslist:
        count_money = count_money + row.Goods_total
    all_goodslist = all_goodslist[page_info.start():page_info.end()]
    return render(request, 'money-look.html', {'all_goodslist': all_goodslist, 'count': count, 'page_info': page_info, 'count_money': count_money}) # 暂时只能实现单表查询


def if_del_money(request):
    try:
        if request.method == "POST":
            id = int(request.POST.get("id"))
            print(id)
            return render(request, 'if_del_money.html', {'id': id})
        elif request.method == "GET":
            id = request.GET.get("id")
            print('if_del_money')
            print(id)
            return render(request, 'if_del_money.html', {"id": id})
        else:
            return HttpResponse('操作失败！请重试。')
    except Exception as e:
        return HttpResponse(e)


def del_moneylook(request):   # 删除部门成员信息
    id = int(request.POST.get('id'))
    btn = request.POST.get('btn')
    print(request.POST)
    print(btn)
    if btn == "delete":
        Goodslist.objects.get(pk=id).delete()
        return redirect('chuanshanghui:money_look')
    elif btn == "cancel":
        return HttpResponse("<script>alert('确定取消？')</script>")


def classroom_list(request):   # 展示教室信息
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", password="Misseriah58262", db='student_union',
                           charset='utf8')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM chuanshanghui_classroom")
    classroom = cursor.fetchall()
    print(classroom)
    # all_classroom = ClassroomRecord.objects.filter()
    return render(request, 'classroom_list.html', context={'classroom': classroom})   # 传递到模板中的数据是classroom_list


def classroom_apply(request):
    dps = Department.objects.all()
    rooms = Classroom.objects.filter(classroom_borrowif='可借用')
    if request.method== 'POST' :
        id = request.POST.get('rom')
        Room_for_dp = request.POST.get('room_for_dp_id')
        Room_pincharge = request.POST.get('room_pincharge_id')
        Room_for_matt = request.POST.get('room_for_matt')
        ClassroomRecord.objects.create(room_num_id=id, room_for_dp_id=Room_for_dp, room_for_matt=Room_for_matt, room_pincharge_id=Room_pincharge, room_checkif='未审核', commands='无')
#        R=ClassroomRecord()
#        R.room_for_dp_id=Department.objects.filter(dp_num=Room_for_dp).first()
#        R.room_num_id=Classroom.objects.filter(classroom_num=id).first()
#        R.room_pincharge_id=Room_pincharge
#        R.room_for_matt=Room_for_matt
#        R.save()
        Classroom.objects.filter(classroom_num=id).update(classroom_borrowif='审核中')
        return HttpResponse("<script>alert('操作成功！')</script>")
    return render(request, 'classroom_apply.html', context={'dps': dps, 'rooms': rooms})


def classroom_applyed(request):
    dps = Department.objects.all()
    id = request.POST.get("dp")
    rooms = ClassroomRecord.objects.filter(room_for_dp_id=id)
    return render(request, 'classroom_applyed.html', {'rooms':rooms, 'dps':dps})


def classroom_applydel(request):
    id = request.GET.get('id')
    rom = request.GET.get('room')
    room = ClassroomRecord.objects.get(id=id)
    if room.room_checkif=='已审核'or room.room_checkif=='未审核':
        Classroom.objects.filter(classroom_num=rom).update(classroom_borrowif='可借用')
    ClassroomRecord.objects.get(id=id).delete( )
    return redirect('chuanshanghui:classroom_applyed' )


def classroom_checklist(request):
    all_room_apply_list = ClassroomRecord.objects.all().order_by('room_num')
    return render(request, 'classroom_checklist.html', context={'all_room_apply_list': all_room_apply_list})


def classroom_viewcheck(request):
    room = request.GET.get('room')
    id = request.GET.get('id')
    all_room_apply_list = ClassroomRecord.objects.filter(room_num_id=room)
    state=ClassroomRecord.objects.filter(id=id).first().room_checkif
    if state=='未审核':
        return render(request, 'classroom_viewcheck.html', {'all_room_apply_list':all_room_apply_list})
    else:
        return HttpResponse("<script>alert('发生错误，该申请可能已经通过或驳回')</script>")

def classroom_applypass(request):
    room = request.GET.get('room')
    ClassroomRecord.objects.filter(room_num_id=room).update(room_checkif='已审核')
    Classroom.objects.filter(classroom_num=room).update(classroom_borrowif='已借用')
    return HttpResponse("<script>alert('操作成功！')</script>")


def classroom_applyfail(request):
    room = request.GET.get('room')
    classroom = ClassroomRecord.objects.filter(room_num_id=room)
    ClassroomRecord.objects.filter(room_num_id=room).update(room_checkif='未通过')
    Classroom.objects.filter(classroom_num=room).update(classroom_borrowif='可借用')
    return render(request, 'b_success.html', {'classroom':classroom})


def classroom_applyfailb(request):
    ro = request.POST.get('room')
    com = request.POST.get('commands')
    ClassroomRecord.objects.filter(room_num_id=ro).update(commands=com)
    return HttpResponse("<script>alert('操作成功！')</script>")


# 活动信息展示管理
class article_list(View):
    def get(self,request):
        if not request.session.get('is_login', None):
            return render(request, '404.html')
        else:
            usernum = request.session.get('person_num')
            people = People.objects.filter(stu_num=usernum)
            person = people.last()
            person_id = person.stu_num
            # 展示活动信息列表
            # 获取当前页码数
            if request.GET.get('page'):
                page_num = int(request.GET.get('page'))
            else:
                # 如果没有指明页码数，默认为第一页（首页）
                page_num = 1
            # 计算当前页面需要展示的数据量，以及位置（第几个-第几个）
            data_start = (page_num - 1) * 6
            data_end = page_num * 6
            # 计算总体数据量
            total_count = Department.objects.all().count()
            # 说明一页展示多少个数据
            per_page = 6
            # 展示需要的总页数以及是否有剩余
            total_page, plus = divmod(total_count, per_page)
            if plus:
                total_page += 1
            # 页面最多展示页码数（1、2、3；2、3、4）
            max_page = 4
            half_max_page = max_page // 2
            # 页面上展示的页码的开始页
            page_start = page_num - half_max_page
            # 页面上展示的页码的结束页
            page_end = page_num + half_max_page
            if page_start <= 1:
                page_start = 1
                page_end = max_page
            if page_end > total_page:
                page_end = total_page
                page_start = total_page - max_page + 1
            if page_start <= 1:
                page_start = 1
            html_list = []
            for i in range(page_start, page_end + 1):
                tmp = '<a href="/chuanshanghui/article_list/?page={0}">{0}</a><span> <span>'.format(i)
                html_list.append(tmp)
            page_html = "".join(html_list)
            all_article = Article.objects.all().filter(stu_num=person_id).order_by('article_is_delete','-article_update_time')[data_start:data_end]
            return render(request, 'article-list.html', {'all_article':all_article,'person': person,
                                                         'page_html':page_html,'page_num':page_num})

    def post(self,request):
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        person_id = person.stu_num
        search_name = request.POST.get('search_name')
        result = Article.objects.filter(article_name__icontains=search_name, stu_num=person_id)
        if result:
            return render(request, 'article-list.html', {'result': result})
        else:
            return render(request, 'article-list.html', {'message': '查询语句有误，请检查！'})


class ArticleAddView(View):
    def get(self, request):
        if not request.session.get('is_login', None):
            return render(request, '404.html')
        else:
            form = ArticleForm()
            return render(request, 'article_add.html', context={'form': form})
    def post(self, request):
        usernum = request.session.get('person_num')
        people = People.objects.filter(stu_num=usernum)
        person = people.last()
        image_file = request.FILES.get('article_image')
        file = request.FILES.get('article_appendix')
        form = ArticleForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.article_image = image_file
            instance.article_appendix = file
            instance.stu_num = person
            instance.save()
            return render(request, 'article_add.html', context={'form': form,'message':'添加新闻成功'})
        else:
            return render(request, 'article_add.html', context={'form': form, 'message':'添加新闻失败，请检查格式'})


class ArticleDeleteView(View):
    def get(self,request):
        article_num = request.GET.get('article_num')
        article = Article.objects.filter(article_num=article_num)
        aa = article.last()
        aa.article_is_delete = True
        aa.save()
        return redirect("/chuanshanghui/article_list/")

    def post(self,request):
        getlist = request.POST.getlist('list')
        articlelist=re.sub("\[|\]","",getlist[0])
        articlelist = articlelist.split(",")
        for a in articlelist:
            a = eval(a)
            article = Article.objects.filter(article_num=a)
            aa = article.last()
            aa.article_is_delete = True
            aa.save()
        return redirect("/chuanshanghui/article_list/")


class ArticleRegetView(View):
    def get(self, request):
        article_num = request.GET.get('article_num')
        article = Article.objects.filter(article_num=article_num)
        aa = article.last()
        aa.article_is_delete = False
        aa.save()
        return redirect("/chuanshanghui/article_list/")

# 在myadmin/views.py中添加如下视图
class ArticleUpdateView(View):
    """
    新闻修改视图
    """
    def get(self, request, article_num):
        # 1> 拿到对应的新闻对象
        article = Article.objects.filter(article_num=article_num).first()
        if article:
            # 2. 生成表单对象
            form = ArticleForm(instance=article)
        else:
            return json_response(errno=Code.NODATA, errmsg='没有此新闻！')

        # 3. 渲染并返回
        return render(request, 'article_detail.html', context={'form': form, 'article':article})

    def post(self, request, article_num):
        # 1. 获取新闻对象
        article = Article.objects.filter(article_num=article_num, article_is_delete=False).first()
        # 1.1 判断新闻是否存在
        if not article:
            return json_response(errno=Code.NODATA, errmsg='该新闻不存在!')
        # 2. 接收参数
        image_file = request.FILES.get('article_image')
        old_image_file = article.article_image
        file = request.FILES.get('article_appendix')
        old_file = article.article_appendix
        put_data = request.POST
        # 3. 创建表单对象
        form = ArticleForm(put_data, instance=article)
        # 4. 校验
        if form.is_valid():
            # 4.1 如果成功,保存数据,返回消息ok
            # form.save()
            # 优化保存
            instance = form.save(commit=False)
            if old_image_file:
                if old_image_file != image_file:
                    instance.article_image = image_file
            else:
                instance.article_image = image_file
            if old_file:
                if old_file != file:
                    instance.article_appendix = file
            else:
                instance.article_appendix = file
            instance.save()
            if form.has_changed():
                # 如果表单参数有改动
                # 先延迟form表单的保存
                instance = form.save(commit=False)
                # 然后按照有改动的字段来保存,避免错误
                instance.save(update_fields=form.changed_data)
            return render(request, 'article_detail.html', context={'form': form})
        else:
            print(form.cleaned_data)
            print(form.errors)
            # 4.2 如果失败,返回渲染了错误信息的html
            return render(request, 'article_detail.html', context={'form': form})

def article_hitcount(request):
    usernum = request.session.get('person_num')
    people = People.objects.filter(stu_num=usernum)
    person = people.last()
    post = DpMembers.objects.values('stu_post').filter(stu_num=usernum).last()
    dp_num = DpMembers.objects.values('dp_num').filter(stu_num=usernum)
    print(datetime.now().time())
    if post==None:
        hitcount_list = Article.objects.values('article_name', 'article_hit')
        hitcount_list = json.dumps(list(hitcount_list))
        if hitcount_list:
            return render(request, 'article_hicount.html', {'person': person, 'hitcount_list': hitcount_list})
        else:
            return HttpResponse("暂无文章发布")
    elif post["stu_post"] == "干事":
        hitcount_list = Article.objects.values('article_name', 'article_hit').filter(stu_num__in=usernum)
        hitcount_list = json.dumps(list(hitcount_list))
        if hitcount_list:
            return render(request, 'article_hicount.html', {'person':person,'hitcount_list':hitcount_list})
        else:
            return HttpResponse("暂无文章发布")
    elif post["stu_post"] == "部长":
        hitcount_list = Article.objects.values('article_name', 'article_hit').filter(stu_num__dpmembers__dp_num__in=dp_num)
        hitcount_list = json.dumps(list(hitcount_list))
        if hitcount_list:
            return render(request, 'article_hicount.html', {'person': person, 'hitcount_list': hitcount_list})
        else:
            return HttpResponse("暂无文章发布")


# ——————————————————————————————————————————— 部门管理—————————————————————————————————————————————————————
# 部门信息管理
def dpmembers_list(request):    # 展示部门成员信息
    all_dpm = DpMembers.objects.all()
    # dpm_dp = DpMembers.objects.get(dp_num=all_dpm.dp_num_id).dp_num_id    # 一对多关系
    # dpm_stu = DpMembers.objects.get().stu_num_id   # 一对一关系
    return render(request, 'dpmembers_list.html', context={'all_dpm': all_dpm})   # 传递到模板中的数据是dpmembers_list


def dpmembers_add(request):   # 增加新部门成员
    if request.method == "POST":
        stunum = request.POST.get('stunum')
        stunum = int(stunum)
        dpnum = request.POST.get('dpnum')
        stupost = request.POST.get('stupost')
        DpMembers.objects.create(stu_num=stunum, dp_num_id=dpnum, stu_post=stupost)
        return redirect('chuanshanghui:a_success')
    return render(request, 'dpmembers_add.html')


def a_success(request):   # 提交成功
    return render(request, 'a_success.html')


def dpmembers_del(request):   # 删除部门成员信息
    # 获取要删除数据的id
    pk = request.GET.get('pk')    # 括号内pk对应页面？后字段
    # pk = int(pk)
    # 根据id到数据库进行删除
    DpMembers.objects.get(stu_num=pk).delete()   # 查询到一个对象  删除该对象
    # 返回重定向到list页面
    return redirect('chuanshanghui:dpmembers_list')


def dpmembers_edit(request):     # 编辑部门成员信息
    pk = request.GET.get('pk')
    dpm_obj = DpMembers.objects.get(pk=pk)
    if request.method == 'GET':
        # get 返回一个页面 也没拿包含form表单 input有原始的数据
        return render(request,'dpmembers_edit.html',{'dpm_obj': dpm_obj})
    else:   # post
        stupost = request.POST.get('stupost')   # 获取用户提交的信息
        dpnum = request.POST.get('dpnum')
        # 修改数据库中对应的数据
        dpm_obj.stu_post = stupost    # 只是在内存中修改
        dpm_obj.dp_num_id = dpnum
        dpm_obj.save()    # 提交到数据库
        return redirect('chuanshanghui:a_success')    # 返回重定向到展示出版社的页面


def dpmembers_read(request):   # 查看部门成员详细信息
    pk = request.GET.get('pk')
    dpm_obj = DpMembers.objects.get(pk=pk)
    people = People.objects.filter(stu_num=pk)
    person = people.last()
    dpmember = (DpMembers.objects.filter(stu_num=pk)).last()
    dpnum = dpmember.dp_num_id  # 2020-12-08将dp_num改为了dp_num_id
    department = (Department.objects.filter(dp_num=dpnum)).last()
    return render(request, 'dpmembers_read.html', {'dpm_p': person, 'dpm_obj': dpm_obj, 'dpm_dp': department})


# 导出后端的Excel表
def export_excel(request):
    # 设置HTTPResponse的类型
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=order.xls'
    # 创建一个文件对象
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('order-sheet')
    # 设置文件头的样式
    style_heading = xlwt.easyxf("""
            font:name Arial,colour_index white,bold on,height 0xA0;
            align:wrap off,vert center,horiz center;
            pattern:pattern solid,fore-colour 0x19;
            borders:left THIN,right THIN,top THIN,bottom THIN;""")
    # 写入文件标题
    sheet.write(0, 0, '学号', style_heading)
    sheet.write(0, 1, '部门编号', style_heading)
    sheet.write(0, 2, '职位', style_heading)
    # 写入数据
    data_row = 1
    # DpMembers.objects.all()   # 查询条件
    for dpm in DpMembers.objects.all():
        # 格式化datetime
        # pri_time = i.pri_date.strftime('%Y-%m-%d')
        # oper_time = i.operating_time.strftime('%Y-%m-%d')
        sheet.write(data_row, 0, dpm.stu_num)
        sheet.write(data_row, 1, dpm.dp_num_id)  # 2020-12-08将dp_num改为了dp_num_id
        sheet.write(data_row, 2, dpm.stu_post)
        data_row = data_row + 1
    # 写出到IO
    output = BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response


def dp_list(request):   # 展示部门信息
    all_dp = Department.objects.all()
    # all_dp = Department.objects.filter(dp_num_id='09')   # 查询操作
    return render(request, 'dp_list.html', context={'all_dp': all_dp})   # 传递到模板中的数据是dpmembers_list


def dp_edit(request):     # 编辑部门成员信息
    pk = request.GET.get('pk')
    dp = Department.objects.get(pk=pk)
    if request.method == 'GET':
        return render(request,'dp_edit.html',{'dp':dp})
    else:
        pre = request.POST.get('pre')
        dp.dp_presentetion = pre
        dp.save()
        return  redirect('chuanshanghui:a_success')    # 返回重定向到展示出版社的页面


def dp_leaders(request):  # 展示部长信息
    return render(request, 'dp_leaders.html')


# ———————————————————————————————————————————部门对接管理—————————————————————————————————————————————————————
# 部门对接管理
def cooperation_alist(request):   # 展示信息
    all_cooa = Cooperation.objects.all()
    return render(request, 'cooperation_alist.html', context={'all_coo': all_cooa})


def cooperation_blist(request):   # 展示信息
    all_coob = Cooperation.objects.all()
    return render(request, 'cooperation_blist.html', context={'all_coo': all_coob})


def cooperation_add(request):  # 增加任务
    return render(request, 'cooperation_add.html')


def cooperation_read(request):  # 查看详情
    return render(request, 'cooperation_read.html')


# ---------------------------------------------权限管理------------------------------------------
class AuthControlView(View):
    def get(self, request):
        usernum = request.session.get('person_num')
        person = People.objects.filter(stu_num=usernum).last()
        dps = DpMembers.objects.all().order_by('dp_num','stu_post','stu_num')
        return render(request, 'auth_list.html', {'person':person,'dps':dps})
    def post(self, request):
        pass