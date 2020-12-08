from django.contrib import admin
# Register your models here.
from chuanshanghui.models import People, Department

#注册
admin.site.register(People)
admin.site.register(Department)


#自定义管理页面,属性说明,列表页属性:list_display、显示字段:list_filter、过滤字段:search_fields、
# 搜索字段:list_per_page、分页、添加、修改页属性：fields、属性的先后顺序：fieldsets、给属性分组  注意：fields与fieldsets不能同时使用


