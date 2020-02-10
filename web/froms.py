from django import forms


# 按照Django form表单验证组件的要求自己写一个类
class gldx_import_Form(forms.Form):

    begin_row_num = forms.IntegerField(
        label="导入起始行",
        min_value=1,
        initial=3,
        required=True,
        error_messages={
            'required': '起始位置行不能为空',
            'min_value': '数值最小为1',
        })
    from_source = forms.CharField(label="数据来源",
                                  required=True,
                                  error_messages={'required': '输入不能为空'}
                                  )
    excel = forms.FileField(label='上传路径', required=True, error_messages={'required': '文件不能为空'})
