import os
import time, datetime
import xlrd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator
from yqry import settings
from .models import yqdx_fyz, yqdx_zzq_provinces, yqdx_zzq_city
import xlsxwriter
from django.http import FileResponse
from .query_helupingtai import *
from django.db.models import Count


# Create your views here.

###################返甬人员组######################################
def dx_import_fyz(request):
    return render(request, "import_fyz.html")


def tongbu(request):
    session_id = request.POST.get('session_id')
    succ_count = 0
    error_list = []
    i = 1
    back_dic = import_data_test(session_id, i)
    if back_dic['code'] == 305:
        return JsonResponse({"code": 305, "msg": "cookie值无效，请重新输入！", "error": "cookie值无效，请重新输入！"})
    elif back_dic['code'] == 200 and back_dic['count'] > 0:

        while True:
            insert_dic_list=list()
            try:
                for dic in back_dic['dic_list']:

                    uuid = dic['uuid']
                    userName = dic['userName']
                    phone = dic['phone']
                    idCard = dic['idCard']
                    liveAddress = dic['liveAddress']
                    workAddress = dic['workAddress']
                    carNo = dic['carNo']
                    carType = dic['carType']
                    startAddress_provinces, startAddress_city, startAddress_county = dic['startAddress'].split(' ')
                    endAddress_city, endAddress_county, endAddress_town = dic['endAddress'].split(' ')
                    endArea = dic['endArea']
                    kakou = dic['kakou']
                    whyGo = dic['whyGo']
                    createTime = dic['createTime']

                    if not yqdx_fyz.objects.filter(uuid=uuid).exists():
                        insert_dic_list.append(yqdx_fyz(uuid=uuid, userName=userName, phone=phone, idCard=idCard,
                                                liveAddress=liveAddress, workAddress=workAddress, carNo=carNo,
                                                carType=carType, startAddress_provinces=startAddress_provinces,
                                                startAddress_city=startAddress_city,
                                                startAddress_county=startAddress_county,
                                                endAddress_city=endAddress_city,
                                                endAddress_county=endAddress_county, endAddress_town=endAddress_town,
                                                endArea=endArea, kakou=kakou, whyGo=whyGo, createTime=createTime,
                                                createDate=createTime.split(' ')[0]))

                        succ_count += 1
                yqdx_fyz.objects.bulk_create(insert_dic_list)
            except Exception as e:
                error_list.append('手机：{0}，姓名：{1}，身份证号：{2}，错误：{3}'.format(phone, userName, idCard, repr(e)))

            i += 1
            back_dic = import_data_test(session_id, i)
            if back_dic['count'] == 0:
                break
        return JsonResponse({"code": 200, "msg": "同步成功,新增{0}条！".format(succ_count), "error": error_list})


def yqdx_list_fyz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    carType = request.POST.get('carType')
    startAddress_provinces = request.POST.get('startAddress_provinces')
    startAddress_city = request.POST.get('startAddress_city')
    endAddress_town = request.POST.get('endAddress_town')
    createDate = request.POST.get('createDate')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_fyz.objects.order_by('-createTime')

    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(userName__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(idCard__contains=sfzh)
        now_page = '1'
    if (carType is not None) and (carType != '全部'):
        data_list = data_list.filter(carType=carType)
        now_page = '1'
    if (startAddress_provinces is not None) and (startAddress_provinces != '全部'):
        data_list = data_list.filter(startAddress_provinces=startAddress_provinces)
        now_page = '1'
    if (startAddress_city is not None) and (startAddress_city != '全部'):
        data_list = data_list.filter(startAddress_city=startAddress_city)
        now_page = '1'
    if (endAddress_town is not None) and (endAddress_town != '全部'):
        data_list = data_list.filter(endAddress_town=endAddress_town)
        now_page = '1'
    if (createDate is not None) and (createDate != '全部'):
        data_list = data_list.filter(createDate=createDate)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'carType': carType,
                    'startAddress_provinces': startAddress_provinces, 'startAddress_city': startAddress_city,
                    'endAddress_town': endAddress_town, 'startAddress_city': startAddress_city,
                    'createDate': createDate}

    if data_list.exists():
        # 分页
        paginator = Paginator(data_list, size)
        total_page = paginator.num_pages
        total_count = paginator.count
        back_page = paginator.page(now_page)
        has_pre = back_page.has_previous()
        has_next = back_page.has_next()
        next_num = total_page
        pre_num = 1
        if has_next:
            next_num = back_page.next_page_number()
        if has_pre:
            pre_num = back_page.previous_page_number()

        # 查询交通工具
        carType_list = yqdx_fyz.objects.values('carType').distinct()
        # 查询来自省
        startAddress_provinces_list = yqdx_fyz.objects.values('startAddress_provinces').distinct()
        # 查询来自市
        startAddress_city_list = yqdx_fyz.objects.values('startAddress_city').distinct()
        # 查询返回镇街道
        endAddress_town_list = yqdx_fyz.objects.values('endAddress_town').distinct()
        # 查询申报日期集
        createDate_list = yqdx_fyz.objects.values('createDate').distinct().order_by('createDate')

        return render(request, 'yqdx_list_fyz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'carType_list': carType_list, 'startAddress_provinces_list': startAddress_provinces_list,
                       'startAddress_city_list': startAddress_city_list, 'endAddress_town_list': endAddress_town_list,
                       'search_cache': search_cache, 'createDate_list': createDate_list,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list_fyz?page=1&size=100'>返回列表</a>")


def yqdx_list_export_fyz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    carType = request.POST.get('carType')
    startAddress_provinces = request.POST.get('startAddress_provinces')
    startAddress_city = request.POST.get('startAddress_city')
    endAddress_town = request.POST.get('endAddress_town')
    createTime = request.POST.get('createTime')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_fyz.objects.all()
    if (phone_no is not None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone=phone_no)
    if (name is not None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(userName__contains=name)
    if (sfzh is not None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(idCard__contains=sfzh)
    if (carType is not None) and (carType != '全部'):
        data_list_tmp = data_list_tmp.filter(carType=carType)
    if (startAddress_provinces is not None) and (startAddress_provinces != '全部'):
        data_list_tmp = data_list_tmp.filter(startAddress_provinces=startAddress_provinces)
    if (startAddress_city is not None) and (startAddress_city != '全部'):
        data_list_tmp = data_list_tmp.filter(startAddress_city=startAddress_city)
    if (endAddress_town is not None) and (endAddress_town != '全部'):
        data_list_tmp = data_list_tmp.filter(endAddress_town=endAddress_town)
    if (createTime is not None) and (createTime != '全部'):
        data_list_tmp = data_list_tmp.filter(createTime=createTime)

    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('返甬预登记库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '现住地址', '工作地址', '车牌/次号', '交通工具',
                                  '来自省', '来自市', '来自县', '返回市', '返回区', '返回镇', '返回详址', '卡口', '返回理由', '登记日期', '数据来源'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone, for_tmp.userName, for_tmp.idCard, for_tmp.liveAddress, for_tmp.workAddress,
                          for_tmp.carNo,
                          for_tmp.carType, for_tmp.startAddress_provinces, for_tmp.startAddress_city,
                          for_tmp.startAddress_county, for_tmp.endAddress_city,
                          for_tmp.endAddress_county, for_tmp.endAddress_town, for_tmp.endArea, for_tmp.kakou,
                          for_tmp.whyGo,
                          for_tmp.createTime.strftime('%Y-%m-%d %H:%M'), for_tmp.from_source, ]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def jjbd_fyz(request):
    return render(request, "jjbd_fyz.html")


def jjbd_upload_fyz(request):
    excel = request.FILES.get('excel')
    bd_type = request.POST.get('bd_type')

    # 获取文件类型
    file_type = excel.name.rsplit('.')[-1]
    file_type = file_type.lower()

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, '{0}.{1}'.format(timestr, file_type))
    # 根据路径打开指定的文件(以二进制读写方式打开)
    f = open(path, 'wb+')
    # chunks将对应的文件数据转换成若干片段, 分段写入, 可以有效提高文件的写入速度, 适用于2.5M以上的文件
    for chunk in excel.chunks():
        f.write(chunk)
    f.close()

    # 创建比对结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'jjbd/', '{0}.xls'.format(timestr))
    jjbd_result_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    same_sheet = jjbd_result_xls.add_worksheet('相同结果集')
    different_sheet = jjbd_result_xls.add_worksheet('不同结果集')
    same_sheet_row_num = 0
    different_sheet_row_num = 0

    # 开始导入excel模板
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows

    for n in range(0, row_num):
        cell_0_value = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            cell_0_value = str(int(cell_0_value))
        cell_0_value = cell_0_value.strip()

        cell_1_value = sheet1.cell_value(n, 1)
        if sheet1.cell(n, 1).ctype == 2:
            cell_1_value = str(int(cell_1_value))
        cell_1_value = cell_1_value.strip()
        kwargs = {
            # 动态查询的字段
        }

        if bd_type == '1' and cell_0_value != '':  # 手机号
            kwargs['phone'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['idCard'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone'] = cell_0_value
            kwargs['userName'] = cell_1_value
        elif bd_type == '4':
            pass
        if kwargs and yqdx_fyz.objects.filter(**kwargs).exists():
            same_sheet.write_row(same_sheet_row_num, 0, sheet1.row_values(n))
            same_sheet_row_num += 1
        else:
            different_sheet.write_row(different_sheet_row_num, 0, sheet1.row_values(n))
            different_sheet_row_num += 1
    jjbd_result_xls.close()

    file_tmp = open(result_path, 'rb')

    response = FileResponse(file_tmp)

    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment;filename=' + urlquote(
        '比对结果' + timestr + '.xls')  # 返回下载文件的名称(activity.xls)

    return response


def bddc_fyz(request):
    return render(request, "bddc_fyz.html")


def bddc_upload_fyz(request):
    excel = request.FILES.get('excel')
    bd_type = request.POST.get('bd_type')
    # 获取文件类型
    file_type = excel.name.rsplit('.')[-1]
    file_type = file_type.lower()

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')
    file_name = '{0}.{1}'.format(timestr, file_type)
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, file_name)
    # 根据路径打开指定的文件(以二进制读写方式打开)
    f = open(path, 'wb+')
    # chunks将对应的文件数据转换成若干片段, 分段写入, 可以有效提高文件的写入速度, 适用于2.5M以上的文件
    for chunk in excel.chunks():
        f.write(chunk)
    f.close()

    # 创建比对结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'bddc/', '{0}.xls'.format(timestr))

    bddc_result_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    same_sheet = bddc_result_xls.add_worksheet('镇海库中有对象导出')
    different_sheet = bddc_result_xls.add_worksheet('库中无')

    # 写入第一行标题
    same_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '现住地址', '工作地址', '车牌/次号', '交通工具',
                                '来自省', '来自市', '来自县', '返回市', '返回区', '返回镇', '返回详址', '卡口', '返回理由', '登记日期', '数据来源'])

    same_sheet_row_num = 1
    different_sheet_row_num = 0

    # 开始导入excel模板
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows

    for n in range(0, row_num):

        cell_0_value = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            cell_0_value = str(int(cell_0_value))
        cell_0_value = cell_0_value.strip()

        cell_1_value = sheet1.cell_value(n, 1)
        if sheet1.cell(n, 1).ctype == 2:
            cell_1_value = str(int(cell_1_value))
        cell_1_value = cell_1_value.strip()
        kwargs = {}  # 动态查询的字段

        if bd_type == '1' and cell_0_value != '':  # 手机号
            kwargs['phone'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['idCard'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone'] = cell_0_value
            kwargs['userName'] = cell_1_value
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx_fyz.objects.filter(**kwargs)
        if kwargs and queryset_tmp.exists():
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone, queryset.userName, queryset.idCard, queryset.liveAddress,
                              queryset.workAddress, queryset.carNo,
                              queryset.carType, queryset.startAddress_provinces, queryset.startAddress_city,
                              queryset.startAddress_county, queryset.endAddress_city,
                              queryset.endAddress_county, queryset.endAddress_town, queryset.endArea, queryset.kakou,
                              queryset.whyGo,
                              queryset.createTime.strftime('%Y-%m-%d %H:%M'), queryset.from_source, ]

            same_sheet.write_row(same_sheet_row_num, 0, query_set_list)
            same_sheet_row_num += 1


        else:
            different_sheet.write_row(different_sheet_row_num, 0, sheet1.row_values(n))
            different_sheet_row_num += 1
    bddc_result_xls.close()

    file_tmp = open(result_path, 'rb')

    response = FileResponse(file_tmp)

    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = 'attachment;filename=' + urlquote(
        '库中比对导出结果' + timestr + '.xls')  # 返回下载文件的名称(activity.xls)

    return response


def zzq_fyz_manager(request):
    zzq_provinces_list = yqdx_zzq_provinces.objects.all()
    zzq_city_list = yqdx_zzq_city.objects.all()
    startAddress_provinces_list = yqdx_fyz.objects.all().values('startAddress_provinces').distinct()
    startAddress_city_list = yqdx_fyz.objects.all().values('startAddress_city').distinct()
    context = {"zzq_provinces_list": zzq_provinces_list, "zzq_city_list": zzq_city_list,
               "startAddress_provinces_list": startAddress_provinces_list,
               "startAddress_city_list": startAddress_city_list}
    return render(request, "zzq_fyz.html", context)


def zzq_fyz_db(request):
    zzq_provinces_list = []
    zzq_city_list = []
    provinces_post_list = request.POST.getlist('zzq_provinces_list')
    city_post_list = request.POST.getlist('zzq_city_list')

    for provinces in provinces_post_list:
        zzq_provinces_list.append(yqdx_zzq_provinces(startAddress_provinces=provinces))

    for city in city_post_list:
        zzq_city_list.append(yqdx_zzq_city(startAddress_city=city))
    # 修改前清空表
    yqdx_zzq_provinces.objects.all().delete()
    yqdx_zzq_city.objects.all().delete()
    yqdx_zzq_city.objects.bulk_create(zzq_city_list)
    yqdx_zzq_provinces.objects.bulk_create(zzq_provinces_list)
    return HttpResponse('修改成功<br><a href=\'/\'>返回首页</a><br><a href=\'/zzq_fyz\'>重灾区管理</a>')


def tongji_fyz(request):
    provinces_tongji_list = list()
    provinces_zengzhanglv_list = list()
    city_tongji_list = list()
    city_zengzhanglv_list= list()
    back_date = str()  # 返回给前端图表
    date_list = list()

    zzq_provinces_list = [tmp[0] for tmp in yqdx_zzq_provinces.objects.all().values_list('startAddress_provinces')]
    zzq_city_list = [tmp[0] for tmp in yqdx_zzq_city.objects.all().values_list('startAddress_city')]
    back_provinces = '\'' + '\',\''.join(zzq_provinces_list) + '\''  # 形成类似'四川省','安徽省','浙江省',的格式
    back_city = '\'' + '\',\''.join(zzq_city_list) + '\''

    zzq_provinces_queryset = yqdx_fyz.objects.extra(
        select={"createDate": "DATE_FORMAT(createTime, '%%Y-%%m-%%d')"}).filter(
        startAddress_provinces__in=zzq_provinces_list).values('createDate', 'startAddress_provinces').annotate(
        num=Count('createDate')).order_by('createDate')
    zzq_city_queryset = yqdx_fyz.objects.extra(select={"createDate": "DATE_FORMAT(createTime, '%%Y-%%m-%%d')"}).filter(
        startAddress_city__in=zzq_city_list).values('createDate', 'startAddress_city').annotate(
        num=Count('createDate')).order_by('createDate')
    quanguo_queryset = yqdx_fyz.objects.extra(select={"createDate": "DATE_FORMAT(createTime, '%%Y-%%m-%%d')"}).values(
        'createDate').annotate(
        num=Count('createDate')).order_by('createDate')

    # 先获得时间数组格式的日期
    now = datetime.datetime.now()
    for i in range(0, 7)[::-1]:
        dif_day = (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        back_date += ("'{0}',".format(dif_day[5:]))
        date_list.append(dif_day)
    # 开始查询重灾区省
    for zzq_provinces in zzq_provinces_list:
        provinces_tmp_tongji = str()
        provinces_tmp_zengzhanglv = str()
        num_yestoday = 0
        for date in date_list:
            num_today = 0
            if zzq_provinces_queryset.filter(startAddress_provinces=zzq_provinces, createDate=date).exists():

                num_today = zzq_provinces_queryset.get(startAddress_provinces=zzq_provinces, createDate=date)['num']
            provinces_tmp_tongji += '{0},'.format(num_today)
            if num_yestoday == 0:  # 被除数不能为0
                provinces_tmp_zengzhanglv += '0,'
            else:
                provinces_tmp_zengzhanglv += '{:.2f},'.format((num_today - num_yestoday) / num_yestoday *100)  # 计算增长率
            num_yestoday = num_today
        provinces_tongji_list.append({'provinces': zzq_provinces, 'tongji': provinces_tmp_tongji})
        provinces_zengzhanglv_list.append({'provinces': zzq_provinces, 'zengzhanglv': provinces_tmp_zengzhanglv})

    # 开始查询重灾区市
    for zzq_city in zzq_city_list:
        city_tmp_tongji = str()
        city_tmp_zengzhanglv = str()
        num_yestoday = 0
        for date in date_list:
            num_today = 0
            if zzq_city_queryset.filter(startAddress_city=zzq_city, createDate=date).exists():
                num_today = zzq_city_queryset.get(startAddress_city=zzq_city, createDate=date)['num']
            city_tmp_tongji += '{0},'.format(num_today)
            if num_yestoday == 0:  # 被除数不能为0
                city_tmp_zengzhanglv += '0,'
            else:
                city_tmp_zengzhanglv += '{:.2f},'.format(
                    (num_today - num_yestoday) / num_yestoday * 100)  # 计算增长率
            num_yestoday = num_today
        city_tongji_list.append({'city': zzq_city, 'tongji': city_tmp_tongji})
        city_zengzhanglv_list.append({'city': zzq_city, 'zengzhanglv': city_tmp_zengzhanglv})

    # 开始统计全国返甬

    quanguo_tmp_tongji = str()
    for date in date_list:
        if quanguo_queryset.filter(createDate=date).exists():
            quanguo_tmp_tongji += '{0},'.format(
                quanguo_queryset.get(createDate=date)['num'])
        else:
            quanguo_tmp_tongji += '0,'
    quanguo_tongji_dic = {'quanguo': '全国', 'tongji': quanguo_tmp_tongji}

    return render(request, "tongji_fyz.html",
                  {'back_date': back_date, 'back_provinces': back_provinces, 'back_city': back_city,
                   'provinces_tongji_list': provinces_tongji_list,'provinces_zengzhanglv_list':provinces_zengzhanglv_list ,'city_tongji_list': city_tongji_list,
                   'city_zengzhanglv_list':city_zengzhanglv_list ,'quanguo_tongji_dic': quanguo_tongji_dic})
