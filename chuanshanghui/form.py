from django import forms
from django.forms import ModelForm
from .models import Reimbursement, Article
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class changeInfoForm(forms.Form):
    renew_stucollege = forms.CharField(max_length=30,required=False)
    renew_stumajor = forms.CharField(max_length=15,required=False)
    renew_stuclass = forms.IntegerField(required=False)
    renew_stuphone = forms.CharField(max_length=11,required=False)
    renew_stuqq = forms.CharField(max_length=20,required=False)
    renew_stuemail = forms.EmailField(required=False)

class changePwdForm(forms.Form):
    password = forms.CharField(max_length=12)
    new_password = forms.CharField(max_length=12)
    renew_password = forms.CharField(max_length=12)

class ArticleForm(forms.ModelForm):
    article_name = forms.CharField(label='文章标题', max_length=100)
    article_image = forms.ImageField(label='封面选择', required=False)
    article_content = forms.CharField(widget=CKEditorUploadingWidget(), label='内容', required=False)
    article_appendix = forms.FileField(label='附件上传', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Article
        fields = ['article_name', 'article_image', 'article_content', 'article_appendix']