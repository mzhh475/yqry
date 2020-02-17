from django.db import models


# Create your models here.

class yqdx(models.Model):
    # 疫情人员表
    phone_no = models.CharField('手机号', max_length=11, null='空')  # 手机号
    name = models.CharField('姓名', max_length=20, null=True)  # 姓名
    sfzh = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    hjdz = models.CharField('户籍地址', max_length=500, null=True)  # 允许空
    xzdz = models.CharField('现住地址', max_length=500, null=True)
    ssjd = models.CharField('所属街道', max_length=20, default='空')
    is_wuhan = models.CharField('是否武汉', max_length=1, null=True)
    is_hubei = models.CharField('是否湖北', max_length=1, null=True)
    is_not_zhenhai = models.CharField('市内非镇海', max_length=1, null=True)
    is_not_ningbo = models.CharField('省内非宁波', max_length=1, null=True)
    is_not_zhejiang = models.CharField('是否省外', max_length=1, null=True)
    back_provinces = models.CharField('返回省', max_length=20, null=True)
    back_city = models.CharField('返回市', max_length=20, null=True)
    back_year = models.CharField('返回年', max_length=4, default='2020')
    back_month = models.CharField('返回月', max_length=2, null=True)
    back_day = models.CharField('返回日', max_length=2, null=True)

    status = models.CharField('当前状态', max_length=10, default='空')
    status_remarks = models.CharField('当前状态备注', max_length=500, null=True)
    call_detail = models.CharField('拨打情况', max_length=100, default='空')
    self_tell = models.CharField('自述情况', max_length=100, null=True)
    # white_list_flag = models.SmallIntegerField(default=0)
    white_list_flag = models.ForeignKey('list_type', to_field='type_value', on_delete=models.SET_DEFAULT, default=0)
    timestamp = models.DateTimeField('最后更新时间', auto_now=True)
    from_source = models.CharField('数据来源', max_length=50, default='市局下发')
    gkr = models.CharField('管控人', max_length=20, null=True)  # 允许空
    gkr_phone = models.CharField('管控人电话', max_length=11, null=True)  # 允许空
    other1 = models.CharField('备用3', max_length=500, null=True)  # 允许空
    other2 = models.CharField('备用4', max_length=500, null=True)  # 允许空
    other3 = models.CharField('备用5', max_length=500, null=True)  # 允许空2

    class Meta:
        # 元类
        db_table = 'yqdx'
        verbose_name = '疫情对象'
        verbose_name_plural = verbose_name  # 去复数形式


class list_type(models.Model):
    type_value = models.SmallIntegerField(default=0, unique=True)
    type_name = models.CharField('名单名称', max_length=10)

    class Meta:
        # 元类
        db_table = 'list_type'
        verbose_name = '白红名单类型'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_hwz(models.Model):
    # 疫情人员表
    phone_no = models.CharField('手机号', max_length=11, null='空')  # 手机号
    name = models.CharField('姓名', max_length=20, null=True)  # 姓名
    sfzh = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    hjdz = models.CharField('户籍地址', max_length=500, null=True)  # 允许空
    xzdz = models.CharField('现住地址', max_length=500, null=True)
    ssjd = models.CharField('所属街道', max_length=20, default='空')
    is_wuhan = models.CharField('是否武汉', max_length=1, null=True)
    is_hubei = models.CharField('是否湖北', max_length=1, null=True)
    is_not_zhenhai = models.CharField('市内非镇海', max_length=1, null=True)
    is_not_ningbo = models.CharField('省内非宁波', max_length=1, null=True)
    is_not_zhejiang = models.CharField('是否省外', max_length=1, null=True)
    back_provinces = models.CharField('返回省', max_length=20, null=True)
    back_city = models.CharField('返回市', max_length=20, null=True)
    back_year = models.CharField('返回年', max_length=4, default='2020')
    back_month = models.CharField('返回月', max_length=2, null=True)
    back_day = models.CharField('返回日', max_length=2, null=True)

    status = models.CharField('当前状态', max_length=10, default='空')
    status_remarks = models.CharField('当前状态备注', max_length=500, null=True)
    call_detail = models.CharField('拨打情况', max_length=100, default='空')
    self_tell = models.CharField('自述情况', max_length=100, null=True)
    # white_list_flag = models.SmallIntegerField(default=0)
    white_list_flag = models.ForeignKey('list_type', to_field='type_value', on_delete=models.SET_DEFAULT, default=0)
    timestamp = models.DateTimeField('最后更新时间', auto_now=True)
    from_source = models.CharField('数据来源', max_length=50, default='市局下发')
    gkr = models.CharField('管控人', max_length=20, null=True)  # 允许空
    gkr_phone = models.CharField('管控人电话', max_length=11, null=True)  # 允许空
    other1 = models.CharField('备用3', max_length=500, null=True)  # 允许空
    other2 = models.CharField('备用4', max_length=500, null=True)  # 允许空
    other3 = models.CharField('备用5', max_length=500, null=True)  # 允许空2

    class Meta:
        # 元类
        db_table = 'yqdx_hwz'
        verbose_name = '疫情对象话务组'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_ypz(models.Model):
    # 疫情人员表
    phone_no = models.CharField('手机号', max_length=11, null='空')  # 手机号
    name = models.CharField('姓名', max_length=20, null=True)  # 姓名
    sfzh = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    hjdz = models.CharField('户籍地址', max_length=500, null=True)  # 允许空
    xzdz = models.CharField('现住地址', max_length=500, null=True)
    ssjd = models.CharField('所属街道', max_length=20, default='空')
    is_wuhan = models.CharField('是否武汉', max_length=1, null=True)
    is_hubei = models.CharField('是否湖北', max_length=1, null=True)
    is_not_zhenhai = models.CharField('市内非镇海', max_length=1, null=True)
    is_not_ningbo = models.CharField('省内非宁波', max_length=1, null=True)
    is_not_zhejiang = models.CharField('是否省外', max_length=1, null=True)
    back_provinces = models.CharField('返回省', max_length=20, null=True)
    back_city = models.CharField('返回市', max_length=20, null=True)
    back_year = models.CharField('返回年', max_length=4, default='2020')
    back_month = models.CharField('返回月', max_length=2, null=True)
    back_day = models.CharField('返回日', max_length=2, null=True)

    status = models.CharField('当前状态', max_length=10, default='空')
    status_remarks = models.CharField('当前状态备注', max_length=500, null=True)
    call_detail = models.CharField('拨打情况', max_length=100, default='空')
    self_tell = models.CharField('自述情况', max_length=100, null=True)
    # white_list_flag = models.SmallIntegerField(default=0)
    white_list_flag = models.ForeignKey('list_type', to_field='type_value', on_delete=models.SET_DEFAULT, default=0)
    timestamp = models.DateTimeField('最后更新时间', auto_now=True)
    from_source = models.CharField('数据来源', max_length=50, default='市局下发')
    gkr = models.CharField('管控人', max_length=20, null=True)  # 允许空
    gkr_phone = models.CharField('管控人电话', max_length=11, null=True)  # 允许空
    other1 = models.CharField('备用3', max_length=500, null=True)  # 允许空
    other2 = models.CharField('备用4', max_length=500, null=True)  # 允许空
    other3 = models.CharField('备用5', max_length=500, null=True)  # 允许空2

    class Meta:
        # 元类
        db_table = 'yqdx_ypz'
        verbose_name = '疫情对象研判组'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_glz(models.Model):
    # 疫情人员表
    name = models.CharField('姓名', max_length=20, null=True)  # 姓名
    sex = models.CharField('性别', max_length=1, null=True)
    sfzh = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    phone_no = models.CharField('手机号', max_length=11, null='空')  # 手机号
    rzrq = models.CharField('入住日期', max_length=50, null=True)  # 身份证
    ryrq = models.CharField('入甬日期', max_length=50, null=True)  # 身份证
    yjjc = models.CharField('预计解除', max_length=50, null=True)  # 身份证
    sjjc = models.CharField('实际解除', max_length=50, null=True)  # 身份证
    glwz = models.CharField('隔离位置', max_length=50, null=True)  # 身份证
    white_list_flag = models.ForeignKey('list_type', to_field='type_value', on_delete=models.SET_DEFAULT, default=0)
    timestamp = models.DateTimeField('最后更新时间', auto_now=True)
    from_source = models.CharField('数据来源', max_length=50, default='区隔离数据')

    class Meta:
        # 元类
        db_table = 'yqdx_glz'
        verbose_name = '疫情对象集中隔离组'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_mzz(models.Model):
    # 疫情人员表
    phone_no = models.CharField('手机号', max_length=11, null='空')  # 手机号
    name = models.CharField('姓名', max_length=20, null=True)  # 姓名
    sfzh = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    hjdz = models.CharField('户籍地址', max_length=500, null=True)  # 允许空
    xzdz = models.CharField('现住地址', max_length=500, null=True)
    ssjd = models.CharField('所属街道', max_length=20, default='空')
    is_wuhan = models.CharField('是否武汉', max_length=1, null=True)
    is_hubei = models.CharField('是否湖北', max_length=1, null=True)
    is_not_zhenhai = models.CharField('市内非镇海', max_length=1, null=True)
    is_not_ningbo = models.CharField('省内非宁波', max_length=1, null=True)
    is_not_zhejiang = models.CharField('是否省外', max_length=1, null=True)
    back_provinces = models.CharField('返回省', max_length=20, null=True)
    back_city = models.CharField('返回市', max_length=20, null=True)
    back_year = models.CharField('返回年', max_length=4, default='2020')
    back_month = models.CharField('返回月', max_length=2, null=True)
    back_day = models.CharField('返回日', max_length=2, null=True)

    status = models.CharField('当前状态', max_length=10, default='空')
    status_remarks = models.CharField('当前状态备注', max_length=500, null=True)
    call_detail = models.CharField('拨打情况', max_length=100, default='空')
    self_tell = models.CharField('自述情况', max_length=100, null=True)
    # white_list_flag = models.SmallIntegerField(default=0)
    white_list_flag = models.ForeignKey('list_type', to_field='type_value', on_delete=models.SET_DEFAULT, default=0)
    timestamp = models.DateTimeField('最后更新时间', auto_now=True)
    from_source = models.CharField('数据来源', max_length=50, default='市局下发')
    gkr = models.CharField('管控人', max_length=20, null=True)  # 允许空
    gkr_phone = models.CharField('管控人电话', max_length=11, null=True)  # 允许空
    other1 = models.CharField('备用3', max_length=500, null=True)  # 允许空
    other2 = models.CharField('备用4', max_length=500, null=True)  # 允许空
    other3 = models.CharField('备用5', max_length=500, null=True)  # 允许空2

    class Meta:
        # 元类
        db_table = 'yqdx_mzz'
        verbose_name = '疫情对象门诊组'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_fyz(models.Model):
    # 疫情人员返甬对象表
    uuid = models.CharField('id', max_length=32, unique=True, default='00000000000000000000000000000000')
    userName = models.CharField('姓名', max_length=20, null=True)  # 姓名
    phone = models.CharField('手机号', max_length=11, null='空')  # 手机号
    idCard = models.CharField('身份证号', max_length=18, null=True)  # 身份证
    liveAddress = models.CharField('现住地址', max_length=500, null=True)  # 允许空
    workAddress = models.CharField('工作地址', max_length=500, null=True)  # 允许空
    carNo = models.CharField('车牌号', max_length=500, null=True)  # 允许空
    carType = models.CharField('交通工具', max_length=50, null=True)  # 允许空
    startAddress_provinces = models.CharField('来自省', max_length=50, null=True)  # 允许空
    startAddress_city = models.CharField('来自市', max_length=50, null=True)  # 允许空
    startAddress_county = models.CharField('来自县', max_length=50, null=True)  # 允许空
    endAddress_city = models.CharField('返回市', max_length=50, null=True)  # 允许空
    endAddress_county = models.CharField('返回县', max_length=50, null=True)  # 允许空
    endAddress_town = models.CharField('返回镇', max_length=50, null=True)  # 允许空
    endArea = models.CharField('返回地址', max_length=100, null=True)  # 允许空
    kakou = models.CharField('卡口', max_length=50, null=True)  # 允许空
    whyGo = models.CharField('返回事由', max_length=50, null=True)  # 允许空
    createTime = models.DateTimeField('登记日期时间', null=True)
    createDate = models.DateField('登记日期', null=True)
    from_source = models.CharField('数据来源', max_length=50, default='核录平台自动爬取')

    class Meta:
        # 元类
        db_table = 'yqdx_fyz'
        verbose_name = '疫情对象返甬人员'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_zzq_provinces(models.Model):
    # 疫情人员重灾地区
    startAddress_provinces = models.CharField('重灾省', max_length=50, unique=True, default='无')

    class Meta:
        # 元类
        db_table = 'yqdx_zzq_provinces'
        verbose_name = '疫情对象重灾区省'
        verbose_name_plural = verbose_name  # 去复数形式


class yqdx_zzq_city(models.Model):
    # 疫情人员重灾地区
    startAddress_city = models.CharField('重灾地市', max_length=50, unique=True, default='无')

    class Meta:
        # 元类
        db_table = 'yqdx_zzq_city'
        verbose_name = '疫情对象重灾区市'
        verbose_name_plural = verbose_name  # 去复数形式
