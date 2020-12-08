#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.http import JsonResponse
import json
import datetime
class Code:
    """
    错误代码,在引发错误的时候作为错误的标志
    """
    OK = "0"
    DBERR = "4001"
    NODATA = "4002"
    DATAEXIST = "4003"
    DATAERR = "4004"
    METHERR = "4005"
    SMSERROR = "4006"
    SMSFAIL = "4007"

    SESSIONERR = "4101"
    LOGINERR = "4102"
    PARAMERR = "4103"
    USERERR = "4104"
    ROLEERR = "4105"
    PWDERR = "4106"

    SERVERERR = "4500"
    UNKOWNERR = "4501"


error_map = {
    # 错误信息,与错误代码对应
    Code.OK: "成功",
    Code.DBERR: "数据库查询错误",
    Code.NODATA: "无数据",
    Code.DATAEXIST: "数据已存在",
    Code.DATAERR: "数据错误",
    Code.METHERR: "方法错误",
    Code.SMSERROR: "发送短信验证码异常",
    Code.SMSFAIL: "发送短信验证码失败",

    Code.SESSIONERR: "用户未登录",
    Code.LOGINERR: "用户登录失败",
    Code.PARAMERR: "参数错误",
    Code.USERERR: "用户不存在或未激活",
    Code.ROLEERR: "用户身份错误",
    Code.PWDERR: "密码错误",

    Code.SERVERERR: "内部错误",
    Code.UNKOWNERR: "未知错误",
}

class MyJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            # 转换为本地时间
            return o.astimezone().strftime('%Y-%m-%d %H:%M:%S')


def json_response(errno=Code.OK, errmsg='', data=None, kwargs=None):
    """
    该方法实现的目的是为了使json数据在传输过程中,能够携带错误代码之类的信息
    :param errno: 错误代码
    :param errmsg: 错误信息
    :param data: 携带的用户信息数据,例如用户名,手机号等
    :return: 返回的相当于是我们处理好的json响应
    """
    json_dict = {
        'errno': errno,
        'errmsg': errmsg,
        'data': data,
    }

    if kwargs and isinstance(kwargs, dict):
        # 判断kwargs中是否有传输数据信息, 有则更新我们已有的信息
        json_dict.update(kwargs)
        print(json_dict)
    return JsonResponse(json_dict, encoder=MyJSONEncoder)
