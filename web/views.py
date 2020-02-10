import json
from django.shortcuts import render
import os
import time, datetime
import xlrd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.db.utils import DataError
from django.core.paginator import Paginator
from yqry import settings
from .models import yqdx, list_type, yqdx_hwz, yqdx_ypz, yqdx_glz
import xlsxwriter
from django.http import FileResponse
from django.utils.http import urlquote
from .froms import gldx_import_Form
from django.db.models import Q


# Create your views here.

def index(request):
    return render(request, 'index.html', )


def dx_import(request):
    return render(request, 'import.html')


# 全库检索
def search_all(request):
    back_data_list = []
    search_value = request.POST.get('search_value')
    queryset = yqdx.objects.filter(Q(phone_no=search_value) | Q(name=search_value) | Q(sfzh=search_value)).distinct()
    for qs in queryset:
        back_data_list.append({"phone_no": qs.phone_no, "name": qs.name, 'sfzh': qs.sfzh, "form_ku": '正式库','from_source': qs.from_source})
    queryset = yqdx_hwz.objects.filter(Q(phone_no=search_value) | Q(name=search_value) | Q(sfzh=search_value)).distinct()
    for qs in queryset:
        back_data_list.append({"phone_no": qs.phone_no, "name": qs.name, 'sfzh': qs.sfzh, "form_ku": '话务组库',
                               'from_source': qs.from_source})
    queryset = yqdx_ypz.objects.filter(Q(phone_no=search_value) | Q(name=search_value) | Q(sfzh=search_value)).distinct()
    for qs in queryset:
        back_data_list.append({"phone_no": qs.phone_no, "name": qs.name, 'sfzh': qs.sfzh, "form_ku": '研判组库',
                               'from_source': qs.from_source})
    queryset = yqdx_glz.objects.filter(Q(phone_no=search_value) | Q(name=search_value) | Q(sfzh=search_value)).distinct()
    for qs in queryset:
        back_data_list.append({"phone_no": qs.phone_no, "name": qs.name, 'sfzh': qs.sfzh, "form_ku": '集中隔离库','from_source': qs.from_source})
    return JsonResponse({"back_data_list": back_data_list}, content_type="application/json,charset=utf-8")


def muban_upload(request):
    excel = request.FILES.get('excel')
    # 获取文件类型
    file_type = excel.name.split('.')[-1]
    file_type = file_type.lower()
    update_list = []
    err_info_list = []
    if file_type in ['xls', 'xlsx']:
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

        # 开始导入excel模板
        book = xlrd.open_workbook(path)
        sheet1 = book.sheets()[0]
        row_num = sheet1.nrows
        col_num = sheet1.ncols

        insert_succ_count = 0
        insert_error_count = 0
        if col_num != 25:
            msg = {'code': 305, 'url': '', 'error': 'excel预定有效值是25列，请删除无效列，当前表格的列数为' + str(col_num)}
        else:
            for n in range(3, row_num):

                phone_no = sheet1.cell_value(n, 0)
                if sheet1.cell(n, 0).ctype == 2:
                    phone_no = str(int(phone_no))
                phone_no = phone_no.strip()
                name = sheet1.cell_value(n, 1)
                sfzh = sheet1.cell_value(n, 2)
                if sheet1.cell(n, 2).ctype == 2:
                    sfzh = str(int(sfzh))
                sfzh = sfzh.strip()
                hjdz = sheet1.cell_value(n, 3)
                xzdz = sheet1.cell_value(n, 4)
                ssjd = sheet1.cell_value(n, 5)
                if not ssjd.strip():
                    ssjd = '空'
                is_wuhan = sheet1.cell_value(n, 6)
                is_hubei = sheet1.cell_value(n, 7)
                is_not_zhenhai = sheet1.cell_value(n, 8)
                is_not_ningbo = sheet1.cell_value(n, 9)
                is_not_zhejiang = sheet1.cell_value(n, 10)

                back_provinces = sheet1.cell_value(n, 11)
                back_city = sheet1.cell_value(n, 12)

                back_month = sheet1.cell_value(n, 13)
                if sheet1.cell(n, 13).ctype == 2:
                    back_month = str(int(back_month))
                back_day = sheet1.cell_value(n, 14)
                if sheet1.cell(n, 14).ctype == 2:
                    back_day = str(int(back_day))
                back_year = '2019' if back_month in ['11', '12'] else '2020'

                status = sheet1.cell_value(n, 15)
                if not status.strip():
                    status = '空'
                status_remarks = sheet1.cell_value(n, 16)
                call_detail = sheet1.cell_value(n, 17)
                if not call_detail.strip():
                    call_detail = '空'
                self_tell = sheet1.cell_value(n, 18)
                from_source = sheet1.cell_value(n, 19)
                if not from_source.strip():
                    from_source = '空'
                gkr = sheet1.cell_value(n, 20)
                gkr_phone = sheet1.cell_value(n, 21)
                if sheet1.cell(n, 21).ctype == 2:
                    gkr_phone = str(int(gkr_phone))
                other1 = sheet1.cell_value(n, 22)
                other2 = sheet1.cell_value(n, 23)
                other3 = sheet1.cell_value(n, 24)
                if phone_no != '' or name != '' or sfzh != '':
                    try:

                        if not yqdx.objects.filter(phone_no=phone_no, name=name):  # 如果手机号不存在，则插入

                            yqdx.objects.create(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                                ssjd=ssjd,
                                                is_wuhan=is_wuhan, is_hubei=is_hubei, is_not_zhenhai=is_not_zhenhai,
                                                is_not_ningbo=is_not_ningbo,
                                                is_not_zhejiang=is_not_zhejiang, back_provinces=back_provinces,
                                                back_city=back_city,
                                                back_year=back_year, back_month=back_month, back_day=back_day,
                                                status=status, status_remarks=status_remarks, call_detail=call_detail,
                                                self_tell=self_tell, from_source=from_source, gkr=gkr,
                                                gkr_phone=gkr_phone,
                                                other1=other1, other2=other2,
                                                other3=other3)
                            insert_succ_count += 1
                        else:
                            update_list.append([phone_no, name, sfzh, ssjd, status, from_source])
                    except DataError as e:
                        insert_error_count += 1
                        err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

            msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                   'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                       str(insert_succ_count + len(update_list) + insert_error_count),
                       str(insert_succ_count), len(update_list), str(insert_error_count))}


    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

    return render(request, 'import_result.html', {'need_update': update_list, 'msg': msg})


def need_update_db(request):
    upload_file_name = request.POST.get('upload_file_name')
    update_phone_list = request.POST.getlist('update_phone')

    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0
    for n in range(3, row_num):

        phone_no = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()
        if phone_no in update_phone_list:

            name = sheet1.cell_value(n, 1)
            sfzh = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                sfzh = str(int(sfzh))
            sfzh = sfzh.strip()
            hjdz = sheet1.cell_value(n, 3)
            xzdz = sheet1.cell_value(n, 4)
            ssjd = sheet1.cell_value(n, 5)
            if not ssjd.strip():
                ssjd = '空'
            is_wuhan = sheet1.cell_value(n, 6)
            is_hubei = sheet1.cell_value(n, 7)
            is_not_zhenhai = sheet1.cell_value(n, 8)
            is_not_ningbo = sheet1.cell_value(n, 9)
            is_not_zhejiang = sheet1.cell_value(n, 10)

            back_provinces = sheet1.cell_value(n, 11)
            back_city = sheet1.cell_value(n, 12)

            back_month = sheet1.cell_value(n, 13)
            if sheet1.cell(n, 13).ctype == 2:
                back_month = str(int(back_month))
            back_day = sheet1.cell_value(n, 14)
            if sheet1.cell(n, 14).ctype == 2:
                back_day = str(int(back_day))
            back_year = '2019' if back_month in ['11', '12'] else '2020'
            status = sheet1.cell_value(n, 15)
            if not status.strip():
                status = '空'
            status_remarks = sheet1.cell_value(n, 16)
            call_detail = sheet1.cell_value(n, 17)
            if not call_detail.strip():
                call_detail = '空'
            self_tell = sheet1.cell_value(n, 18)
            from_source = sheet1.cell_value(n, 19)
            if not from_source.strip():
                from_source = '空'
            gkr = sheet1.cell_value(n, 20)
            gkr_phone = sheet1.cell_value(n, 21)
            if sheet1.cell(n, 21).ctype == 2:
                gkr_phone = str(int(gkr_phone))
            other1 = sheet1.cell_value(n, 22)
            other2 = sheet1.cell_value(n, 23)
            other3 = sheet1.cell_value(n, 24)
            try:
                query_set = yqdx.objects.filter(phone_no=phone_no, name=name)
                null_list = ['', None, '/N', '空', '\\N', '不详']
                # if name not in null_list:
                #     query_set.update(name=name)
                if sfzh not in null_list:
                    query_set.update(sfzh=sfzh)
                if hjdz not in null_list:
                    query_set.update(hjdz=hjdz)
                if xzdz not in null_list:
                    query_set.update(xzdz=xzdz)
                if ssjd not in null_list:
                    query_set.update(ssjd=ssjd)
                if is_wuhan not in null_list:
                    query_set.update(is_wuhan=is_wuhan)
                if is_hubei not in null_list:
                    query_set.update(is_hubei=is_hubei)
                if is_not_zhenhai not in null_list:
                    query_set.update(is_not_zhenhai=is_not_zhenhai)
                if is_not_ningbo not in null_list:
                    query_set.update(is_not_ningbo=is_not_ningbo)
                if is_not_zhejiang not in null_list:
                    query_set.update(is_not_zhejiang=is_not_zhejiang)
                if back_provinces not in null_list:
                    query_set.update(back_provinces=back_provinces)
                if back_city not in null_list:
                    query_set.update(back_city=back_city)
                if back_year not in null_list:
                    query_set.update(back_year=back_year)
                if back_month not in null_list:
                    query_set.update(back_month=back_month)
                if back_day not in null_list:
                    query_set.update(back_day=back_day)
                if status not in null_list:
                    query_set.update(status=status)
                if status_remarks not in null_list:
                    query_set.update(status_remarks=status_remarks)
                if call_detail not in null_list:
                    query_set.update(call_detail=call_detail)
                if self_tell not in null_list:
                    query_set.update(self_tell=self_tell)
                if from_source not in null_list:
                    query_set.update(from_source=from_source)
                if gkr not in null_list:
                    query_set.update(gkr=gkr)
                if gkr_phone not in null_list:
                    query_set.update(gkr_phone=gkr_phone)
                if other1 not in null_list:
                    query_set.update(other1=other1)
                if other2 not in null_list:
                    query_set.update(other2=other2)
                if other3 not in null_list:
                    query_set.update(other3=other3)

                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

    return render(request, 'update_result.html', {
        'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                'error': err_info_list}})


def white_red_list_set(request):
    return render(request, 'white_red_list_set.html')


def white_red_list_set_db(request):
    excel = request.FILES.get('excel')
    list_type_value = request.POST.get('list_type')
    bd_type = request.POST.get('bd_type')

    # 获取文件类型
    file_type = excel.name.split('.')[-1]
    file_type = file_type.lower()

    err_info_list = []
    if file_type in ['xls', 'xlsx']:
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

        # 开始导入excel模板
        book = xlrd.open_workbook(path)
        sheet1 = book.sheets()[0]
        row_num = sheet1.nrows

        set_succ_count = 0
        set_error_count = 0

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
                kwargs['phone_no'] = cell_0_value
            elif bd_type == '2' and cell_0_value != '':  # 身份证号
                kwargs['sfzh'] = cell_0_value
            elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
                kwargs['phone_no'] = cell_0_value
                kwargs['name'] = cell_1_value
            elif bd_type == '4':
                pass
            queryset = yqdx.objects.filter(**kwargs)
            list_type_object = list_type.objects.get(type_value=list_type_value)
            if kwargs and queryset:  # 如果手机号姓名同时存在，则批量设置

                queryset.update(white_list_flag=list_type_object)
                set_succ_count += 1

            else:
                set_error_count += 1
                err_info_list.append([cell_0_value, cell_1_value])
        list_type_name = list_type.objects.values('type_name').get(type_value=list_type_value)

        msg = {'code': 200,
               'content': '成功批量设置#{0}#{1}条,出错{2}条。'.format(list_type_name['type_name'], set_succ_count,
                                                           set_error_count),
               'error': err_info_list}
    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}
    return render(request, 'list_set_result.html', {'msg': msg})


def yqdx_list(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx.objects.all().order_by('id')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (ssjd is not None) and (ssjd != '全部'):
        data_list = data_list.filter(ssjd=ssjd)
        now_page = '1'
    if (status is not None) and (status != '全部'):
        data_list = data_list.filter(status=status)
        now_page = '1'
    if (call_detail is not None) and (call_detail != '全部'):
        data_list = data_list.filter(call_detail=call_detail)
        now_page = '1'
    if (white_list_flag is not None) and (white_list_flag != '全部'):
        data_list = data_list.filter(white_list_flag=white_list_flag)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'ssjd': ssjd, 'status': status,
                    'call_detail': call_detail, 'white_list_flag': white_list_flag, 'from_source': from_source}

    # data_list = yqdx.objects.filter(list_type__type_value=1)
    if data_list:
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

        # 查询数据来源值
        from_source_list = yqdx.objects.values('from_source').distinct()
        # 查询拨打情况
        call_detail_list = yqdx.objects.values('call_detail').distinct()
        # 查询状态
        status_list = yqdx.objects.values('status').distinct()
        # 查询所属街道
        ssjd_list = yqdx.objects.values('ssjd').distinct()
        # 查询白名单
        white_list_flag_list = list_type.objects.all()

        return render(request, 'yqdx_list.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list,
                       'call_detail_list': call_detail_list, 'status_list': status_list, 'ssjd_list': ssjd_list,
                       'white_list_flag_list': white_list_flag_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list?page=1&size=100'>返回列表</a>")


def jjbd(request):
    return render(request, "jjbd.html")


def jjbd_upload(request):
    excel = request.FILES.get('excel')
    bd_type = request.POST.get('bd_type')

    # 获取文件类型
    file_type = excel.name.split('.')[-1]
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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass

        if kwargs and yqdx.objects.filter(**kwargs):
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


def yqdx_list_export(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx.objects.all()
    if (not phone_no is None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (not name is None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (not sfzh is None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (not ssjd is None) and (ssjd != '全部'):
        data_list_tmp = data_list_tmp.filter(ssjd=ssjd)
    if (not status is None) and (status != '全部'):
        data_list_tmp = data_list_tmp.filter(status=status)
    if (not call_detail is None) and (call_detail != '全部'):
        data_list_tmp = data_list_tmp.filter(call_detail=call_detail)
    if (not white_list_flag is None) and (white_list_flag != '全部'):
        data_list_tmp = data_list_tmp.filter(white_list_flag=white_list_flag)
    if (not from_source is None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('镇海库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                  '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                  '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                  '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone_no, for_tmp.name, for_tmp.sfzh, for_tmp.hjdz, for_tmp.xzdz, for_tmp.ssjd,
                          for_tmp.is_wuhan, for_tmp.is_hubei, for_tmp.is_not_zhenhai, for_tmp.is_not_ningbo,
                          for_tmp.is_not_zhejiang, for_tmp.back_provinces, for_tmp.back_city, for_tmp.back_year,
                          for_tmp.back_month, for_tmp.back_day, for_tmp.status, for_tmp.status_remarks,
                          for_tmp.call_detail, for_tmp.self_tell, for_tmp.white_list_flag.type_name,
                          for_tmp.from_source, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M'), for_tmp.gkr,
                          for_tmp.gkr_phone, for_tmp.other1, for_tmp.other2, for_tmp.other3]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def back_date_whitelist(request):
    safe_date = (datetime.datetime.now() + datetime.timedelta(days=-14))
    year = safe_date.year
    month = safe_date.month
    day = safe_date.day

    # yqdx.objects.filter(back_year)


def bddc(request):
    return render(request, "bddc.html")


def bddc_upload(request):
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
    same_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])

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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx.objects.filter(**kwargs)
        if kwargs and queryset_tmp:
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone_no, queryset.name, queryset.sfzh, queryset.hjdz, queryset.xzdz,
                              queryset.ssjd, queryset.is_wuhan, queryset.is_hubei, queryset.is_not_zhenhai,
                              queryset.is_not_ningbo, queryset.is_not_zhejiang, queryset.back_provinces,
                              queryset.back_city, queryset.back_year, queryset.back_month, queryset.back_day,
                              queryset.status, queryset.status_remarks, queryset.call_detail, queryset.self_tell,
                              queryset.white_list_flag.type_name, queryset.from_source,
                              queryset.timestamp.strftime('%Y-%m-%d %H:%M'), queryset.gkr, queryset.gkr_phone,
                              queryset.other1, queryset.other2, queryset.other3]

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


# 下载视图
def download(request):
    field = request.GET.get('field')
    filename = request.GET.get('filename')
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, field, filename)
    file = open(path, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/msword'
    response['Content-Disposition'] = 'attachment;filename=' + filename
    return response


def yqdx_mod(request):
    id = request.GET.get('id')
    data_list = yqdx.objects.filter(id=id).first()

    # 查询白名单名称
    white_list_flag_list = list_type.objects.all()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list, 'white_list_flag_list': white_list_flag_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod.html", {'msg': msg})


def yqdx_del(request):
    id = request.GET.get('id')

    if yqdx.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


def yqdx_mod_db(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    hjdz = request.POST.get('hjdz')
    xzdz = request.POST.get('xzdz')
    ssjd = request.POST.get('ssjd')
    is_hubei = request.POST.get('is_hubei')
    is_wuhan = request.POST.get('is_wuhan')
    is_not_zhenhai = request.POST.get('is_not_zhenhai')
    is_not_ningbo = request.POST.get('is_not_ningbo')
    is_not_zhejiang = request.POST.get('is_not_zhejiang')
    back_provinces = request.POST.get('back_provinces')
    back_city = request.POST.get('back_city')
    back_year = request.POST.get('back_year')
    back_month = request.POST.get('back_month')
    back_day = request.POST.get('back_day')
    status = request.POST.get('status')
    status_remarks = request.POST.get('status_remarks')
    call_detail = request.POST.get('call_detail')
    self_tell = request.POST.get('self_tell')
    from_source = request.POST.get('from_source')
    gkr = request.POST.get('gkr')
    gkr_phone = request.POST.get('gkr_phone')
    other1 = request.POST.get('other1')
    other2 = request.POST.get('other2')
    other3 = request.POST.get('other3')
    white_list_flag = request.POST.get('white_list_flag')

    white_list_object = list_type.objects.get(type_value=white_list_flag)

    try:
        yqdx.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                          ssjd=ssjd,
                                          is_wuhan=is_wuhan, is_hubei=is_hubei,
                                          is_not_zhejiang=is_not_zhejiang,
                                          is_not_zhenhai=is_not_zhenhai, is_not_ningbo=is_not_ningbo,
                                          back_provinces=back_provinces,
                                          back_city=back_city, back_year=back_year, back_month=back_month,
                                          back_day=back_day,
                                          status=status,
                                          status_remarks=status_remarks, call_detail=call_detail,
                                          self_tell=self_tell,
                                          from_source=from_source, gkr=gkr,
                                          gkr_phone=gkr_phone, other1=other1, other2=other2, other3=other3,
                                          white_list_flag=white_list_object)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result.html", {'msg': msg})


################话务组#################

def dx_import_hwz(request):
    return render(request, 'import_hwz.html')


def muban_upload_hwz(request):
    excel = request.FILES.get('excel')
    # 获取文件类型
    file_type = excel.name.rsplit('.')[-1]
    file_type = file_type.lower()
    update_list = []
    err_info_list = []
    if file_type in ['xls', 'xlsx']:
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

        # 开始导入excel模板
        book = xlrd.open_workbook(path)
        sheet1 = book.sheets()[0]
        row_num = sheet1.nrows
        col_num = sheet1.ncols

        insert_succ_count = 0
        insert_error_count = 0
        if col_num != 25:
            msg = {'code': 305, 'url': '', 'error': 'excel预定有效值是25列，请删除无效列，当前表格的列数为' + str(col_num)}
        else:
            for n in range(3, row_num):

                phone_no = sheet1.cell_value(n, 0)
                if sheet1.cell(n, 0).ctype == 2:
                    phone_no = str(int(phone_no))
                phone_no = phone_no.strip()
                name = sheet1.cell_value(n, 1)
                sfzh = sheet1.cell_value(n, 2)
                if sheet1.cell(n, 2).ctype == 2:
                    sfzh = str(int(sfzh))
                sfzh = sfzh.strip()
                hjdz = sheet1.cell_value(n, 3)
                xzdz = sheet1.cell_value(n, 4)
                ssjd = sheet1.cell_value(n, 5)
                if not ssjd.strip():
                    ssjd = '空'
                is_wuhan = sheet1.cell_value(n, 6)
                is_hubei = sheet1.cell_value(n, 7)
                is_not_zhenhai = sheet1.cell_value(n, 8)
                is_not_ningbo = sheet1.cell_value(n, 9)
                is_not_zhejiang = sheet1.cell_value(n, 10)

                back_provinces = sheet1.cell_value(n, 11)
                back_city = sheet1.cell_value(n, 12)

                back_month = sheet1.cell_value(n, 13)
                if sheet1.cell(n, 13).ctype == 2:
                    back_month = str(int(back_month))
                back_day = sheet1.cell_value(n, 14)
                if sheet1.cell(n, 14).ctype == 2:
                    back_day = str(int(back_day))
                back_year = '2019' if back_month in ['11', '12'] else '2020'

                status = sheet1.cell_value(n, 15)
                if not status.strip():
                    status = '空'
                status_remarks = sheet1.cell_value(n, 16)
                call_detail = sheet1.cell_value(n, 17)
                if not call_detail.strip():
                    call_detail = '空'
                self_tell = sheet1.cell_value(n, 18)
                from_source = sheet1.cell_value(n, 19)
                if not from_source.strip():
                    from_source = '空'
                gkr = sheet1.cell_value(n, 20)
                gkr_phone = sheet1.cell_value(n, 21)
                if sheet1.cell(n, 21).ctype == 2:
                    gkr_phone = str(int(gkr_phone))
                other1 = sheet1.cell_value(n, 22)
                other2 = sheet1.cell_value(n, 23)
                other3 = sheet1.cell_value(n, 24)
                if phone_no != '' or name != '' or sfzh != '':
                    try:

                        if not yqdx_hwz.objects.filter(phone_no=phone_no, name=name):  # 如果手机号不存在，则插入

                            yqdx_hwz.objects.create(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                                    ssjd=ssjd,
                                                    is_wuhan=is_wuhan, is_hubei=is_hubei, is_not_zhenhai=is_not_zhenhai,
                                                    is_not_ningbo=is_not_ningbo,
                                                    is_not_zhejiang=is_not_zhejiang, back_provinces=back_provinces,
                                                    back_city=back_city,
                                                    back_year=back_year, back_month=back_month, back_day=back_day,
                                                    status=status, status_remarks=status_remarks,
                                                    call_detail=call_detail,
                                                    self_tell=self_tell, from_source=from_source, gkr=gkr,
                                                    gkr_phone=gkr_phone,
                                                    other1=other1, other2=other2,
                                                    other3=other3)
                            insert_succ_count += 1
                        else:
                            update_list.append([phone_no, name, sfzh, ssjd, status, from_source])
                    except DataError as e:
                        insert_error_count += 1
                        err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

            msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                   'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                       str(insert_succ_count + len(update_list) + insert_error_count),
                       str(insert_succ_count), len(update_list), str(insert_error_count))}


    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

    return render(request, 'import_result_hwz.html', {'need_update': update_list, 'msg': msg})


def need_update_db_hwz(request):
    upload_file_name = request.POST.get('upload_file_name')
    update_phone_list = request.POST.getlist('update_phone')

    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0
    for n in range(3, row_num):

        phone_no = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()
        if phone_no in update_phone_list:

            name = sheet1.cell_value(n, 1)
            sfzh = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                sfzh = str(int(sfzh))
            sfzh = sfzh.strip()
            hjdz = sheet1.cell_value(n, 3)
            xzdz = sheet1.cell_value(n, 4)
            ssjd = sheet1.cell_value(n, 5)
            if not ssjd.strip():
                ssjd = '空'
            is_wuhan = sheet1.cell_value(n, 6)
            is_hubei = sheet1.cell_value(n, 7)
            is_not_zhenhai = sheet1.cell_value(n, 8)
            is_not_ningbo = sheet1.cell_value(n, 9)
            is_not_zhejiang = sheet1.cell_value(n, 10)

            back_provinces = sheet1.cell_value(n, 11)
            back_city = sheet1.cell_value(n, 12)

            back_month = sheet1.cell_value(n, 13)
            if sheet1.cell(n, 13).ctype == 2:
                back_month = str(int(back_month))
            back_day = sheet1.cell_value(n, 14)
            if sheet1.cell(n, 14).ctype == 2:
                back_day = str(int(back_day))
            back_year = '2019' if back_month in ['11', '12'] else '2020'
            status = sheet1.cell_value(n, 15)
            if not status.strip():
                status = '空'
            status_remarks = sheet1.cell_value(n, 16)
            call_detail = sheet1.cell_value(n, 17)
            if not call_detail.strip():
                call_detail = '空'
            self_tell = sheet1.cell_value(n, 18)
            from_source = sheet1.cell_value(n, 19)
            if not from_source.strip():
                from_source = '空'
            gkr = sheet1.cell_value(n, 20)
            gkr_phone = sheet1.cell_value(n, 21)
            if sheet1.cell(n, 21).ctype == 2:
                gkr_phone = str(int(gkr_phone))
            other1 = sheet1.cell_value(n, 22)
            other2 = sheet1.cell_value(n, 23)
            other3 = sheet1.cell_value(n, 24)
            try:
                query_set = yqdx_hwz.objects.filter(phone_no=phone_no, name=name)
                null_list = ['', None, '/N', '空', '\\N', '不详']
                # if name not in null_list:
                #     query_set.update(name=name)
                if sfzh not in null_list:
                    query_set.update(sfzh=sfzh)
                if hjdz not in null_list:
                    query_set.update(hjdz=hjdz)
                if xzdz not in null_list:
                    query_set.update(xzdz=xzdz)
                if ssjd not in null_list:
                    query_set.update(ssjd=ssjd)
                if is_wuhan not in null_list:
                    query_set.update(is_wuhan=is_wuhan)
                if is_hubei not in null_list:
                    query_set.update(is_hubei=is_hubei)
                if is_not_zhenhai not in null_list:
                    query_set.update(is_not_zhenhai=is_not_zhenhai)
                if is_not_ningbo not in null_list:
                    query_set.update(is_not_ningbo=is_not_ningbo)
                if is_not_zhejiang not in null_list:
                    query_set.update(is_not_zhejiang=is_not_zhejiang)
                if back_provinces not in null_list:
                    query_set.update(back_provinces=back_provinces)
                if back_city not in null_list:
                    query_set.update(back_city=back_city)
                if back_year not in null_list:
                    query_set.update(back_year=back_year)
                if back_month not in null_list:
                    query_set.update(back_month=back_month)
                if back_day not in null_list:
                    query_set.update(back_day=back_day)
                if status not in null_list:
                    query_set.update(status=status)
                if status_remarks not in null_list:
                    query_set.update(status_remarks=status_remarks)
                if call_detail not in null_list:
                    query_set.update(call_detail=call_detail)
                if self_tell not in null_list:
                    query_set.update(self_tell=self_tell)
                if from_source not in null_list:
                    query_set.update(from_source=from_source)
                if gkr not in null_list:
                    query_set.update(gkr=gkr)
                if gkr_phone not in null_list:
                    query_set.update(gkr_phone=gkr_phone)
                if other1 not in null_list:
                    query_set.update(other1=other1)
                if other2 not in null_list:
                    query_set.update(other2=other2)
                if other3 not in null_list:
                    query_set.update(other3=other3)

                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

    return render(request, 'update_result_hwz.html', {
        'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                'error': err_info_list}})


def yqdx_list_hwz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_hwz.objects.all().order_by('id')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (ssjd is not None) and (ssjd != '全部'):
        data_list = data_list.filter(ssjd=ssjd)
        now_page = '1'
    if (status is not None) and (status != '全部'):
        data_list = data_list.filter(status=status)
        now_page = '1'
    if (call_detail is not None) and (call_detail != '全部'):
        data_list = data_list.filter(call_detail=call_detail)
        now_page = '1'
    if (white_list_flag is not None) and (white_list_flag != '全部'):
        data_list = data_list.filter(white_list_flag=white_list_flag)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'ssjd': ssjd, 'status': status,
                    'call_detail': call_detail, 'white_list_flag': white_list_flag, 'from_source': from_source}

    # data_list = yqdx_hwz.objects.filter(list_type__type_value=1)
    if data_list:
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

        # 查询数据来源值
        from_source_list = yqdx_hwz.objects.values('from_source').distinct()
        # 查询拨打情况
        call_detail_list = yqdx_hwz.objects.values('call_detail').distinct()
        # 查询状态
        status_list = yqdx_hwz.objects.values('status').distinct()
        # 查询所属街道
        ssjd_list = yqdx_hwz.objects.values('ssjd').distinct()
        # 查询白名单
        white_list_flag_list = list_type.objects.all()

        return render(request, 'yqdx_list_hwz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list,
                       'call_detail_list': call_detail_list, 'status_list': status_list, 'ssjd_list': ssjd_list,
                       'white_list_flag_list': white_list_flag_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list_hwz?page=1&size=100'>返回列表</a>")


def jjbd_hwz(request):
    return render(request, "jjbd_hwz.html")


def jjbd_upload_hwz(request):
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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        if kwargs and yqdx_hwz.objects.filter(**kwargs):
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


def yqdx_list_export_hwz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_hwz.objects.all()
    if (not phone_no is None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (not name is None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (not sfzh is None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (not ssjd is None) and (ssjd != '全部'):
        data_list_tmp = data_list_tmp.filter(ssjd=ssjd)
    if (not status is None) and (status != '全部'):
        data_list_tmp = data_list_tmp.filter(status=status)
    if (not call_detail is None) and (call_detail != '全部'):
        data_list_tmp = data_list_tmp.filter(call_detail=call_detail)
    if (not white_list_flag is None) and (white_list_flag != '全部'):
        data_list_tmp = data_list_tmp.filter(white_list_flag=white_list_flag)
    if (not from_source is None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('镇海库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                  '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                  '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                  '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone_no, for_tmp.name, for_tmp.sfzh, for_tmp.hjdz, for_tmp.xzdz, for_tmp.ssjd,
                          for_tmp.is_wuhan, for_tmp.is_hubei, for_tmp.is_not_zhenhai, for_tmp.is_not_ningbo,
                          for_tmp.is_not_zhejiang, for_tmp.back_provinces, for_tmp.back_city, for_tmp.back_year,
                          for_tmp.back_month, for_tmp.back_day, for_tmp.status, for_tmp.status_remarks,
                          for_tmp.call_detail, for_tmp.self_tell, for_tmp.white_list_flag.type_name,
                          for_tmp.from_source, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M'), for_tmp.gkr,
                          for_tmp.gkr_phone, for_tmp.other1, for_tmp.other2, for_tmp.other3]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def bddc_hwz(request):
    return render(request, "bddc_hwz.html")


def bddc_upload_hwz(request):
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
    same_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])

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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx_hwz.objects.filter(**kwargs)
        if kwargs and queryset_tmp:
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone_no, queryset.name, queryset.sfzh, queryset.hjdz, queryset.xzdz,
                              queryset.ssjd, queryset.is_wuhan, queryset.is_hubei, queryset.is_not_zhenhai,
                              queryset.is_not_ningbo, queryset.is_not_zhejiang, queryset.back_provinces,
                              queryset.back_city, queryset.back_year, queryset.back_month, queryset.back_day,
                              queryset.status, queryset.status_remarks, queryset.call_detail, queryset.self_tell,
                              queryset.white_list_flag.type_name, queryset.from_source,
                              queryset.timestamp.strftime('%Y-%m-%d %H:%M'), queryset.gkr, queryset.gkr_phone,
                              queryset.other1, queryset.other2, queryset.other3]

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


def yqdx_mod_db_hwz(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    hjdz = request.POST.get('hjdz')
    xzdz = request.POST.get('xzdz')
    ssjd = request.POST.get('ssjd')
    is_hubei = request.POST.get('is_hubei')
    is_wuhan = request.POST.get('is_wuhan')
    is_not_zhenhai = request.POST.get('is_not_zhenhai')
    is_not_ningbo = request.POST.get('is_not_ningbo')
    is_not_zhejiang = request.POST.get('is_not_zhejiang')
    back_provinces = request.POST.get('back_provinces')
    back_city = request.POST.get('back_city')
    back_year = request.POST.get('back_year')
    back_month = request.POST.get('back_month')
    back_day = request.POST.get('back_day')
    status = request.POST.get('status')
    status_remarks = request.POST.get('status_remarks')
    call_detail = request.POST.get('call_detail')
    self_tell = request.POST.get('self_tell')
    from_source = request.POST.get('from_source')
    gkr = request.POST.get('gkr')
    gkr_phone = request.POST.get('gkr_phone')
    other1 = request.POST.get('other1')
    other2 = request.POST.get('other2')
    other3 = request.POST.get('other3')
    white_list_flag = request.POST.get('white_list_flag')

    white_list_object = list_type.objects.get(type_value=white_list_flag)

    try:
        yqdx_hwz.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                              ssjd=ssjd,
                                              is_wuhan=is_wuhan, is_hubei=is_hubei,
                                              is_not_zhejiang=is_not_zhejiang,
                                              is_not_zhenhai=is_not_zhenhai, is_not_ningbo=is_not_ningbo,
                                              back_provinces=back_provinces,
                                              back_city=back_city, back_year=back_year, back_month=back_month,
                                              back_day=back_day,
                                              status=status,
                                              status_remarks=status_remarks, call_detail=call_detail,
                                              self_tell=self_tell,
                                              from_source=from_source, gkr=gkr,
                                              gkr_phone=gkr_phone, other1=other1, other2=other2, other3=other3,
                                              white_list_flag=white_list_object)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result_hwz.html", {'msg': msg})


def yqdx_mod_hwz(request):
    id = request.GET.get('id')
    data_list = yqdx_hwz.objects.filter(id=id).first()

    # 查询白名单名称
    white_list_flag_list = list_type.objects.all()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list, 'white_list_flag_list': white_list_flag_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod_hwz.html", {'msg': msg})


def yqdx_del_hwz(request):
    id = request.GET.get('id')

    if yqdx_hwz.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


################研判组#################


def dx_import_ypz(request):
    return render(request, 'import_ypz.html')


def muban_upload_ypz(request):
    excel = request.FILES.get('excel')
    # 获取文件类型
    file_type = excel.name.rsplit('.')[-1]
    file_type = file_type.lower()
    update_list = []
    err_info_list = []
    if file_type in ['xls', 'xlsx']:
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

        # 开始导入excel模板
        book = xlrd.open_workbook(path)
        sheet1 = book.sheets()[0]
        row_num = sheet1.nrows
        col_num = sheet1.ncols

        insert_succ_count = 0
        insert_error_count = 0
        if col_num != 25:
            msg = {'code': 305, 'url': '', 'error': 'excel预定有效值是25列，请删除无效列，当前表格的列数为' + str(col_num)}
        else:
            for n in range(3, row_num):

                phone_no = sheet1.cell_value(n, 0)
                if sheet1.cell(n, 0).ctype == 2:
                    phone_no = str(int(phone_no))
                phone_no = phone_no.strip()
                name = sheet1.cell_value(n, 1)
                sfzh = sheet1.cell_value(n, 2)
                if sheet1.cell(n, 2).ctype == 2:
                    sfzh = str(int(sfzh))
                sfzh = sfzh.strip()
                hjdz = sheet1.cell_value(n, 3)
                xzdz = sheet1.cell_value(n, 4)
                ssjd = sheet1.cell_value(n, 5)
                if not ssjd.strip():
                    ssjd = '空'
                is_wuhan = sheet1.cell_value(n, 6)
                is_hubei = sheet1.cell_value(n, 7)
                is_not_zhenhai = sheet1.cell_value(n, 8)
                is_not_ningbo = sheet1.cell_value(n, 9)
                is_not_zhejiang = sheet1.cell_value(n, 10)

                back_provinces = sheet1.cell_value(n, 11)
                back_city = sheet1.cell_value(n, 12)

                back_month = sheet1.cell_value(n, 13)
                if sheet1.cell(n, 13).ctype == 2:
                    back_month = str(int(back_month))
                back_day = sheet1.cell_value(n, 14)
                if sheet1.cell(n, 14).ctype == 2:
                    back_day = str(int(back_day))
                back_year = '2019' if back_month in ['11', '12'] else '2020'

                status = sheet1.cell_value(n, 15)
                if not status.strip():
                    status = '空'
                status_remarks = sheet1.cell_value(n, 16)
                call_detail = sheet1.cell_value(n, 17)
                if not call_detail.strip():
                    call_detail = '空'
                self_tell = sheet1.cell_value(n, 18)
                from_source = sheet1.cell_value(n, 19)
                if not from_source.strip():
                    from_source = '空'
                gkr = sheet1.cell_value(n, 20)
                gkr_phone = sheet1.cell_value(n, 21)
                if sheet1.cell(n, 21).ctype == 2:
                    gkr_phone = str(int(gkr_phone))
                other1 = sheet1.cell_value(n, 22)
                other2 = sheet1.cell_value(n, 23)
                other3 = sheet1.cell_value(n, 24)
                if phone_no != '' or name != '' or sfzh != '':
                    try:

                        if not yqdx_ypz.objects.filter(phone_no=phone_no, name=name):  # 如果手机号不存在，则插入

                            yqdx_ypz.objects.create(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                                    ssjd=ssjd,
                                                    is_wuhan=is_wuhan, is_hubei=is_hubei, is_not_zhenhai=is_not_zhenhai,
                                                    is_not_ningbo=is_not_ningbo,
                                                    is_not_zhejiang=is_not_zhejiang, back_provinces=back_provinces,
                                                    back_city=back_city,
                                                    back_year=back_year, back_month=back_month, back_day=back_day,
                                                    status=status, status_remarks=status_remarks,
                                                    call_detail=call_detail,
                                                    self_tell=self_tell, from_source=from_source, gkr=gkr,
                                                    gkr_phone=gkr_phone,
                                                    other1=other1, other2=other2,
                                                    other3=other3)
                            insert_succ_count += 1
                        else:
                            update_list.append([phone_no, name, sfzh, ssjd, status, from_source])
                    except DataError as e:
                        insert_error_count += 1
                        err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

            msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                   'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                       str(insert_succ_count + len(update_list) + insert_error_count),
                       str(insert_succ_count), len(update_list), str(insert_error_count))}


    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

    return render(request, 'import_result_ypz.html', {'need_update': update_list, 'msg': msg})


def need_update_db_ypz(request):
    upload_file_name = request.POST.get('upload_file_name')
    update_phone_list = request.POST.getlist('update_phone')

    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0
    for n in range(3, row_num):

        phone_no = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()
        if phone_no in update_phone_list:

            name = sheet1.cell_value(n, 1)
            sfzh = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                sfzh = str(int(sfzh))
            sfzh = sfzh.strip()
            hjdz = sheet1.cell_value(n, 3)
            xzdz = sheet1.cell_value(n, 4)
            ssjd = sheet1.cell_value(n, 5)
            if not ssjd.strip():
                ssjd = '空'
            is_wuhan = sheet1.cell_value(n, 6)
            is_hubei = sheet1.cell_value(n, 7)
            is_not_zhenhai = sheet1.cell_value(n, 8)
            is_not_ningbo = sheet1.cell_value(n, 9)
            is_not_zhejiang = sheet1.cell_value(n, 10)

            back_provinces = sheet1.cell_value(n, 11)
            back_city = sheet1.cell_value(n, 12)

            back_month = sheet1.cell_value(n, 13)
            if sheet1.cell(n, 13).ctype == 2:
                back_month = str(int(back_month))
            back_day = sheet1.cell_value(n, 14)
            if sheet1.cell(n, 14).ctype == 2:
                back_day = str(int(back_day))
            back_year = '2019' if back_month in ['11', '12'] else '2020'
            status = sheet1.cell_value(n, 15)
            if not status.strip():
                status = '空'
            status_remarks = sheet1.cell_value(n, 16)
            call_detail = sheet1.cell_value(n, 17)
            if not call_detail.strip():
                call_detail = '空'
            self_tell = sheet1.cell_value(n, 18)
            from_source = sheet1.cell_value(n, 19)
            if not from_source.strip():
                from_source = '空'
            gkr = sheet1.cell_value(n, 20)
            gkr_phone = sheet1.cell_value(n, 21)
            if sheet1.cell(n, 21).ctype == 2:
                gkr_phone = str(int(gkr_phone))
            other1 = sheet1.cell_value(n, 22)
            other2 = sheet1.cell_value(n, 23)
            other3 = sheet1.cell_value(n, 24)
            try:
                query_set = yqdx_ypz.objects.filter(phone_no=phone_no, name=name)
                null_list = ['', None, '/N', '空', '\\N', '不详']
                # if name not in null_list:
                #     query_set.update(name=name)
                if sfzh not in null_list:
                    query_set.update(sfzh=sfzh)
                if hjdz not in null_list:
                    query_set.update(hjdz=hjdz)
                if xzdz not in null_list:
                    query_set.update(xzdz=xzdz)
                if ssjd not in null_list:
                    query_set.update(ssjd=ssjd)
                if is_wuhan not in null_list:
                    query_set.update(is_wuhan=is_wuhan)
                if is_hubei not in null_list:
                    query_set.update(is_hubei=is_hubei)
                if is_not_zhenhai not in null_list:
                    query_set.update(is_not_zhenhai=is_not_zhenhai)
                if is_not_ningbo not in null_list:
                    query_set.update(is_not_ningbo=is_not_ningbo)
                if is_not_zhejiang not in null_list:
                    query_set.update(is_not_zhejiang=is_not_zhejiang)
                if back_provinces not in null_list:
                    query_set.update(back_provinces=back_provinces)
                if back_city not in null_list:
                    query_set.update(back_city=back_city)
                if back_year not in null_list:
                    query_set.update(back_year=back_year)
                if back_month not in null_list:
                    query_set.update(back_month=back_month)
                if back_day not in null_list:
                    query_set.update(back_day=back_day)
                if status not in null_list:
                    query_set.update(status=status)
                if status_remarks not in null_list:
                    query_set.update(status_remarks=status_remarks)
                if call_detail not in null_list:
                    query_set.update(call_detail=call_detail)
                if self_tell not in null_list:
                    query_set.update(self_tell=self_tell)
                if from_source not in null_list:
                    query_set.update(from_source=from_source)
                if gkr not in null_list:
                    query_set.update(gkr=gkr)
                if gkr_phone not in null_list:
                    query_set.update(gkr_phone=gkr_phone)
                if other1 not in null_list:
                    query_set.update(other1=other1)
                if other2 not in null_list:
                    query_set.update(other2=other2)
                if other3 not in null_list:
                    query_set.update(other3=other3)

                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，错误信息：{1}'.format(phone_no, repr(e)))

    return render(request, 'update_result_ypz.html', {
        'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                'error': err_info_list}})


def yqdx_list_ypz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_ypz.objects.all().order_by('id')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (ssjd is not None) and (ssjd != '全部'):
        data_list = data_list.filter(ssjd=ssjd)
        now_page = '1'
    if (status is not None) and (status != '全部'):
        data_list = data_list.filter(status=status)
        now_page = '1'
    if (call_detail is not None) and (call_detail != '全部'):
        data_list = data_list.filter(call_detail=call_detail)
        now_page = '1'
    if (white_list_flag is not None) and (white_list_flag != '全部'):
        data_list = data_list.filter(white_list_flag=white_list_flag)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'ssjd': ssjd, 'status': status,
                    'call_detail': call_detail, 'white_list_flag': white_list_flag, 'from_source': from_source}

    # data_list = yqdx_ypz.objects.filter(list_type__type_value=1)
    if data_list:
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

        # 查询数据来源值
        from_source_list = yqdx_ypz.objects.values('from_source').distinct()
        # 查询拨打情况
        call_detail_list = yqdx_ypz.objects.values('call_detail').distinct()
        # 查询状态
        status_list = yqdx_ypz.objects.values('status').distinct()
        # 查询所属街道
        ssjd_list = yqdx_ypz.objects.values('ssjd').distinct()
        # 查询白名单
        white_list_flag_list = list_type.objects.all()

        return render(request, 'yqdx_list_ypz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list,
                       'call_detail_list': call_detail_list, 'status_list': status_list, 'ssjd_list': ssjd_list,
                       'white_list_flag_list': white_list_flag_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list_ypz?page=1&size=100'>返回列表</a>")


def jjbd_ypz(request):
    return render(request, "jjbd_ypz.html")


def jjbd_upload_ypz(request):
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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        if kwargs and yqdx_ypz.objects.filter(**kwargs):
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


def yqdx_list_export_ypz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ssjd = request.POST.get('ssjd')
    status = request.POST.get('status')
    call_detail = request.POST.get('call_detail')
    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_ypz.objects.all()
    if (not phone_no is None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (not name is None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (not sfzh is None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (not ssjd is None) and (ssjd != '全部'):
        data_list_tmp = data_list_tmp.filter(ssjd=ssjd)
    if (not status is None) and (status != '全部'):
        data_list_tmp = data_list_tmp.filter(status=status)
    if (not call_detail is None) and (call_detail != '全部'):
        data_list_tmp = data_list_tmp.filter(call_detail=call_detail)
    if (not white_list_flag is None) and (white_list_flag != '全部'):
        data_list_tmp = data_list_tmp.filter(white_list_flag=white_list_flag)
    if (not from_source is None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('镇海库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                  '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                  '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                  '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone_no, for_tmp.name, for_tmp.sfzh, for_tmp.hjdz, for_tmp.xzdz, for_tmp.ssjd,
                          for_tmp.is_wuhan, for_tmp.is_hubei, for_tmp.is_not_zhenhai, for_tmp.is_not_ningbo,
                          for_tmp.is_not_zhejiang, for_tmp.back_provinces, for_tmp.back_city, for_tmp.back_year,
                          for_tmp.back_month, for_tmp.back_day, for_tmp.status, for_tmp.status_remarks,
                          for_tmp.call_detail, for_tmp.self_tell, for_tmp.white_list_flag.type_name,
                          for_tmp.from_source, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M'), for_tmp.gkr,
                          for_tmp.gkr_phone, for_tmp.other1, for_tmp.other2, for_tmp.other3]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def bddc_ypz(request):
    return render(request, "bddc_ypz.html")


def bddc_upload_ypz(request):
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
    same_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '所属街道', '是否武汉',
                                '是否湖北', '市内非镇海', '省内非宁波', '省外', '何省返回', '何市返回', '返回年',
                                '返回月', '返回日', '当前状态', '当前状态备注', '拨打情况', '自述情况', '白名单',
                                '数据来源', '入库时间', '管控人', '管控人电话', '备用1', '备用2', '备用3'])

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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx_ypz.objects.filter(**kwargs)
        if kwargs and queryset_tmp:
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone_no, queryset.name, queryset.sfzh, queryset.hjdz, queryset.xzdz,
                              queryset.ssjd, queryset.is_wuhan, queryset.is_hubei, queryset.is_not_zhenhai,
                              queryset.is_not_ningbo, queryset.is_not_zhejiang, queryset.back_provinces,
                              queryset.back_city, queryset.back_year, queryset.back_month, queryset.back_day,
                              queryset.status, queryset.status_remarks, queryset.call_detail, queryset.self_tell,
                              queryset.white_list_flag.type_name, queryset.from_source,
                              queryset.timestamp.strftime('%Y-%m-%d %H:%M'), queryset.gkr, queryset.gkr_phone,
                              queryset.other1, queryset.other2, queryset.other3]

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


def yqdx_mod_db_ypz(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    hjdz = request.POST.get('hjdz')
    xzdz = request.POST.get('xzdz')
    ssjd = request.POST.get('ssjd')
    is_hubei = request.POST.get('is_hubei')
    is_wuhan = request.POST.get('is_wuhan')
    is_not_zhenhai = request.POST.get('is_not_zhenhai')
    is_not_ningbo = request.POST.get('is_not_ningbo')
    is_not_zhejiang = request.POST.get('is_not_zhejiang')
    back_provinces = request.POST.get('back_provinces')
    back_city = request.POST.get('back_city')
    back_year = request.POST.get('back_year')
    back_month = request.POST.get('back_month')
    back_day = request.POST.get('back_day')
    status = request.POST.get('status')
    status_remarks = request.POST.get('status_remarks')
    call_detail = request.POST.get('call_detail')
    self_tell = request.POST.get('self_tell')
    from_source = request.POST.get('from_source')
    gkr = request.POST.get('gkr')
    gkr_phone = request.POST.get('gkr_phone')
    other1 = request.POST.get('other1')
    other2 = request.POST.get('other2')
    other3 = request.POST.get('other3')
    white_list_flag = request.POST.get('white_list_flag')

    white_list_object = list_type.objects.get(type_value=white_list_flag)

    try:
        yqdx_ypz.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                              ssjd=ssjd,
                                              is_wuhan=is_wuhan, is_hubei=is_hubei,
                                              is_not_zhejiang=is_not_zhejiang,
                                              is_not_zhenhai=is_not_zhenhai, is_not_ningbo=is_not_ningbo,
                                              back_provinces=back_provinces,
                                              back_city=back_city, back_year=back_year, back_month=back_month,
                                              back_day=back_day,
                                              status=status,
                                              status_remarks=status_remarks, call_detail=call_detail,
                                              self_tell=self_tell,
                                              from_source=from_source, gkr=gkr,
                                              gkr_phone=gkr_phone, other1=other1, other2=other2, other3=other3,
                                              white_list_flag=white_list_object)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result_ypz.html", {'msg': msg})


def yqdx_mod_ypz(request):
    id = request.GET.get('id')
    data_list = yqdx_ypz.objects.filter(id=id).first()

    # 查询白名单名称
    white_list_flag_list = list_type.objects.all()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list, 'white_list_flag_list': white_list_flag_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod_ypz.html", {'msg': msg})


def yqdx_del_ypz(request):
    id = request.GET.get('id')

    if yqdx_ypz.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


################集中隔离数据组#################


def dx_import_glz(request):
    return render(request, 'import_glz.html')


def need_update_db_glz(request):
    upload_file_name = request.POST.get('upload_file_name')
    update_phone_list = request.POST.getlist('update_phone')
    begin_row_num = int(request.POST.get('begin_row_num'))
    from_source = request.POST.get('from_source')

    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0

    for n in range(begin_row_num-1, row_num):
        phone_no = sheet1.cell_value(n, 3)
        if sheet1.cell(n, 3).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()
        if phone_no in update_phone_list:
            name = sheet1.cell_value(n, 0).strip()
            sex = sheet1.cell_value(n, 1).strip()
            sfzh = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                sfzh = str(int(sfzh))
            sfzh = sfzh.strip()

            rzrq = sheet1.cell_value(n, 4)
            if sheet1.cell(n, 4).ctype == 3:
                rzrq = xlrd.xldate_as_datetime(sheet1.cell_value(n, 4), 0).strftime('%Y-%m-%d')
            ryrq = sheet1.cell_value(n, 5)
            if sheet1.cell(n, 5).ctype == 3:
                ryrq = xlrd.xldate_as_datetime(sheet1.cell_value(n, 5), 0).strftime('%Y-%m-%d')
            yjjc = sheet1.cell_value(n, 6)
            if sheet1.cell(n, 6).ctype == 3:
                yjjc = xlrd.xldate_as_datetime(sheet1.cell_value(n, 6), 0).strftime('%Y-%m-%d')
            sjjc = sheet1.cell_value(n, 7)
            if sheet1.cell(n, 7).ctype == 3:
                sjjc = xlrd.xldate_as_datetime(sheet1.cell_value(n, 7), 0).strftime('%Y-%m-%d')
            glwz = sheet1.cell_value(n, 8).strip()

            try:
                query_set = yqdx_glz.objects.filter(phone_no=phone_no, name=name)
                null_list = ['', None, '/N', '空', '\\N', '不详']
                print('gengxin')

                if sfzh not in null_list:
                    query_set.update(sfzh=sfzh)
                if sex not in null_list:
                    query_set.update(sex=sex)
                if rzrq not in null_list:
                    query_set.update(rzrq=rzrq)
                if ryrq not in null_list:
                    query_set.update(ryrq=ryrq)
                if yjjc not in null_list:
                    query_set.update(yjjc=yjjc)
                if sjjc not in null_list:
                    query_set.update(sjjc=sjjc)

                if from_source not in null_list:
                    query_set.update(from_source=from_source)
                if glwz not in null_list:
                    query_set.update(glwz=glwz)
                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，姓名：{1}，身份证号：{2},错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))
    return render(request, 'update_result_glz.html',
                  {'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                           'error': err_info_list}})


def yqdx_list_glz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    glwz = request.POST.get('glwz')
    from_source = request.POST.get('from_source')
    white_list_flag = request.POST.get('white_list_flag')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_glz.objects.all().order_by('timestamp')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (glwz is not None) and (glwz != '全部'):
        data_list = data_list.filter(glwz=glwz)
        now_page = '1'
    if (white_list_flag is not None) and (white_list_flag != '全部'):
        data_list = data_list.filter(white_list_flag=white_list_flag)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'glwz': glwz,
                    'white_list_flag': white_list_flag, 'from_source': from_source}

    if data_list:
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

        # 查询隔离位置
        glwz_list = yqdx_glz.objects.values('glwz').distinct()

        # 查询数据来源值
        from_source_list = yqdx_glz.objects.values('from_source').distinct()
        # 查询白名单
        white_list_flag_list = list_type.objects.all()

        return render(request, 'yqdx_list_glz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list, 'glwz_list': glwz_list,
                       'white_list_flag_list': white_list_flag_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list_glz?page=1&size=100'>返回列表</a>")


def jjbd_glz(request):
    return render(request, "jjbd_glz.html")


def jjbd_upload_glz(request):
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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        if kwargs and yqdx_glz.objects.filter(**kwargs):
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


def yqdx_list_export_glz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    glwz = request.POST.get('glwz')

    white_list_flag = request.POST.get('white_list_flag')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_glz.objects.all()
    if (phone_no is not None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (name is not None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (sfzh is not None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (glwz is not None) and (glwz != '全部'):
        data_list_tmp = data_list_tmp.filter(glwz=glwz)
    if (white_list_flag is not None) and (white_list_flag != '全部'):
        data_list_tmp = data_list_tmp.filter(white_list_flag=white_list_flag)
    if (from_source is not None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('集中隔离库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '性别', '入住日期', '入甬日期', '预计解除',
                                  '实际解除', '隔离位置', '白名单', '数据来源', '入库时间'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone_no, for_tmp.name, for_tmp.sfzh, for_tmp.sex, for_tmp.rzrq, for_tmp.ryrq,
                          for_tmp.yjjc, for_tmp.sjjc, for_tmp.glwz, for_tmp.white_list_flag.type_name,
                          for_tmp.from_source, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M')]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def bddc_glz(request):
    return render(request, "bddc_glz.html")


def bddc_upload_glz(request):
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
    same_sheet.write_row(0, 0, ['手机号', '姓名', '性别', '身份证号', '入住时间', '入甬时间', '预计解除', '实际解除', '隔离位置', '白名单',
                                '数据来源', '入库时间'])

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
            kwargs['phone_no'] = cell_0_value
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx_glz.objects.filter(**kwargs)
        if kwargs and queryset_tmp:
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone_no, queryset.name, queryset.sex, queryset.sfzh, queryset.rzrq,
                              queryset.ryrq,
                              queryset.yjjc, queryset.sjjc, queryset.glwz,
                              queryset.white_list_flag.type_name, queryset.from_source,
                              queryset.timestamp.strftime('%Y-%m-%d %H:%M')]

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


def yqdx_mod_db_glz(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    sex = request.POST.get('sex')
    rzrq = request.POST.get('rzrq')
    ryrq = request.POST.get('ryrq')
    yjjc = request.POST.get('yjjc')
    sjjc = request.POST.get('sjjc')
    glwz = request.POST.get('glwz')
    from_source = request.POST.get('from_source')

    white_list_flag = request.POST.get('white_list_flag')

    white_list_object = list_type.objects.get(type_value=white_list_flag)

    try:
        yqdx_glz.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, sex=sex, rzrq=rzrq,
                                              ryrq=ryrq,
                                              yjjc=yjjc, sjjc=sjjc,
                                              glwz=glwz, from_source=from_source, white_list_flag=white_list_object)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result_glz.html", {'msg': msg})


def yqdx_mod_glz(request):
    id = request.GET.get('id')
    data_list = yqdx_glz.objects.filter(id=id).first()

    # 查询白名单名称
    white_list_flag_list = list_type.objects.all()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list, 'white_list_flag_list': white_list_flag_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod_glz.html", {'msg': msg})


def yqdx_del_glz(request):
    id = request.GET.get('id')

    if yqdx_glz.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


# 使用form组件实现验证表单，实现疫情人员导入模板上传
def muban_upload_glz(request):
    form_obj = gldx_import_Form()
    if request.method == "POST":
        # 实例化form对象的时候，把post提交过来的数据直接传进去
        form_obj = gldx_import_Form(request.POST, request.FILES)
        # 调用form_obj校验数据的方法
        if form_obj.is_valid():
            post_data = form_obj.clean()
            excel = post_data['excel']
            begin_row_num = int(post_data['begin_row_num'])
            from_source = post_data['from_source']

            # 获取文件类型
            file_type = excel.name.rsplit('.')[-1]
            file_type = file_type.lower()
            update_list = []
            err_info_list = []
            if file_type in ['xls', 'xlsx']:
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

                # 开始导入excel模板
                book = xlrd.open_workbook(path)
                sheet1 = book.sheets()[0]
                row_num = sheet1.nrows
                col_num = sheet1.ncols

                insert_succ_count = 0
                insert_error_count = 0
                if col_num != 9:
                    msg = {'code': 305, 'url': '', 'error': '模板预定有效值是9列，请删除无效列，当前表格的列数为' + str(col_num)}
                else:
                    for n in range(begin_row_num-1, row_num):
                        name = sheet1.cell_value(n, 0).strip()
                        sex = sheet1.cell_value(n, 1).strip()
                        sfzh = sheet1.cell_value(n, 2)
                        if sheet1.cell(n, 2).ctype == 2:
                            sfzh = str(int(sfzh))
                        sfzh = sfzh.strip()
                        phone_no = sheet1.cell_value(n, 3)
                        if sheet1.cell(n, 3).ctype == 2:
                            phone_no = str(int(phone_no))
                        phone_no = phone_no.strip()

                        rzrq = sheet1.cell_value(n, 4)
                        if sheet1.cell(n, 4).ctype == 2:
                            rzrq = int(sheet1.cell_value(n, 4))
                        if sheet1.cell(n, 4).ctype == 3:
                            rzrq = xlrd.xldate_as_datetime(sheet1.cell_value(n, 4), 0).strftime('%Y-%m-%d')
                        ryrq = sheet1.cell_value(n, 5)
                        if sheet1.cell(n, 5).ctype == 3:
                            ryrq = xlrd.xldate_as_datetime(sheet1.cell_value(n, 5), 0).strftime('%Y-%m-%d')
                        yjjc = sheet1.cell_value(n, 6)
                        if sheet1.cell(n, 6).ctype == 3:
                            yjjc = xlrd.xldate_as_datetime(sheet1.cell_value(n, 6), 0).strftime('%Y-%m-%d')
                        sjjc = sheet1.cell_value(n, 7)
                        if sheet1.cell(n, 7).ctype == 3:
                            sjjc = xlrd.xldate_as_datetime(sheet1.cell_value(n, 7), 0).strftime('%Y-%m-%d')
                        glwz = sheet1.cell_value(n, 8).strip()

                        if phone_no != '' or name != '' or sfzh != '':
                            try:
                                if not yqdx_glz.objects.filter(phone_no=phone_no, name=name):  # 如果手机号不存在，则插入
                                    yqdx_glz.objects.create(name=name, sex=sex, sfzh=sfzh, phone_no=phone_no, rzrq=rzrq,
                                                            ryrq=ryrq, yjjc=yjjc, sjjc=sjjc, from_source=from_source,
                                                            glwz=glwz)
                                    insert_succ_count += 1
                                else:
                                    update_list.append(
                                        [name, sex, sfzh, phone_no, rzrq, ryrq, yjjc, glwz, from_source])
                            except DataError as e:
                                insert_error_count += 1
                                err_info_list.append(
                                    '手机号:{0}，姓名：{1}，身份证号：{2}，错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))

                    msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                           'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                               str(insert_succ_count + len(update_list) + insert_error_count),
                               str(insert_succ_count), len(update_list), str(insert_error_count)),
                           'begin_row_num': begin_row_num, 'from_source': from_source}
            else:
                msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

            return render(request, 'import_result_glz.html', {'need_update': update_list, 'msg': msg})
        #form.is_valid() 为False
        else:
            return render(request, "import_glz.html", {"obj": form_obj})

    return render(request, "import_glz.html", {"obj": form_obj})
