import os
import time, datetime
import xlrd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.db.utils import DataError
from django.core.paginator import Paginator
from yqry import settings
from .models import list_type, yqdx_hbz
import xlsxwriter
from django.http import FileResponse
from django.utils.http import urlquote
from .froms import hbz_import_Form
from django.views.decorators.cache import cache_page


# Create your views here.
################集中隔离数据组#################


def dx_import_hbz(request):
    return render(request, 'import_hbz.html')


def need_update_db_hbz(request):
    upload_file_name = request.POST.get('upload_file_name')
    update_phone_list = request.POST.getlist('update_phone')
    begin_row_num = int(request.POST.get('begin_row_num'))
    label = request.POST.get('label')

    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0

    for n in range(begin_row_num - 1, row_num):
        phone_no = sheet1.cell_value(n, 0)
        if sheet1.cell(n, 0).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()
        name = sheet1.cell_value(n, 1).strip()
        if '{0}|{1}'.format(phone_no, name) in update_phone_list:
            sfzh = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                sfzh = str(int(sfzh))
            sfzh = sfzh.strip()

            hjdz = sheet1.cell_value(n, 3)
            if sheet1.cell(n, 3).ctype == 2:
                hjdz = str(int(hjdz))
            hjdz = hjdz.strip()

            xzdz = sheet1.cell_value(n, 4)
            if sheet1.cell(n, 4).ctype == 2:
                xzdz = str(int(xzdz))
            xzdz = xzdz.strip()

            remark = sheet1.cell_value(n, 5)
            if sheet1.cell(n, 5).ctype == 2:
                remark = str(int(remark))
            remark = remark.strip()
            from_source = sheet1.cell_value(n, 6).strip()

            try:
                kwargs2 = {}  # 动态更新字段
                query_set = yqdx_hbz.objects.filter(phone_no=phone_no, name=name)
                null_list = ['', None, '/N', '空', '\\N', '不详']
                if sfzh not in null_list:
                    kwargs2['sfzh'] = sfzh
                if hjdz not in null_list:
                    kwargs2['hjdz'] = hjdz
                if xzdz not in null_list:
                    kwargs2['xzdz'] = xzdz
                if remark not in null_list:
                    kwargs2['remark'] = remark
                if from_source not in null_list:
                    kwargs2['from_source'] = from_source
                if label != '0':
                    kwargs2['label'] = label
                query_set.update(**kwargs2)
                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，姓名：{1}，身份证号：{2},错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))
    return render(request, 'update_result_hbz.html',
                  {'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                           'error': err_info_list}})


@cache_page(60 * 5)
def yqdx_list_hbz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    label = request.POST.get('label')
    from_source = request.POST.get('from_source')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_hbz.objects.all().order_by('timestamp')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (label is not None) and (label != '全部'):
        data_list = data_list.filter(label=label)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'label': label, 'from_source': from_source}

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
        # 查询数据来源值
        from_source_list = yqdx_hbz.objects.values('from_source').distinct()
        # 查询标签
        label_list = yqdx_hbz.objects.values('label').distinct()

        return render(request, 'yqdx_list_hbz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num, 'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list, 'label_list': label_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse(
            "库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='/yqdx_list_hbz?page=1&size=100'>返回列表</a>")


def jjbd_hbz(request):
    return render(request, "jjbd_hbz.html")


def jjbd_upload_hbz(request):
    excel = request.FILES.get('excel')
    bd_type = request.POST.get('bd_type')
    labels = request.POST.getlist('labels')

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
            kwargs['label__in'] = labels
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
            kwargs['label__in'] = labels
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
            kwargs['label__in'] = labels
        elif bd_type == '4':
            pass
        if kwargs and yqdx_hbz.objects.filter(**kwargs).exists():
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


def yqdx_list_export_hbz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    label = request.POST.get('label')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_hbz.objects.all()
    if (phone_no is not None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (name is not None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (sfzh is not None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (label is not None) and (label != '全部'):
        data_list_tmp = data_list_tmp.filter(label=label)
    if (from_source is not None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('集中隔离库查询导出')
    label_list = ['未处理', '已研判排除', '已返甬未管', '已返甬在管', '不返甬', '其他']
    # 写入第一行标题
    export_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '备注',
                                  '标签', '数据来源', '入库时间'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.phone_no, for_tmp.name, for_tmp.sfzh, for_tmp.hjdz, for_tmp.xzdz, for_tmp.remark,
                          label_list[for_tmp.label], for_tmp.from_source, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M')]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def bddc_hbz(request):
    return render(request, "bddc_hbz.html")


def bddc_upload_hbz(request):
    excel = request.FILES.get('excel')
    bd_type = request.POST.get('bd_type')
    labels = request.POST.getlist('labels')
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
    label_list = ['未处理', '已研判排除', '已返甬未管', '已返甬在管', '不返甬', '其他']
    # 写入第一行标题
    same_sheet.write_row(0, 0, ['手机号', '姓名', '身份证号', '户籍地址', '现住地址', '备注', '标签', '数据来源', '入库时间'])

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
            kwargs['label__in'] = labels
        elif bd_type == '2' and cell_0_value != '':  # 身份证号
            kwargs['sfzh'] = cell_0_value
            kwargs['label__in'] = labels
        elif bd_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
            kwargs['phone_no'] = cell_0_value
            kwargs['name'] = cell_1_value
            kwargs['label__in'] = labels
        elif bd_type == '4':
            pass
        # 执行过滤
        queryset_tmp = yqdx_hbz.objects.filter(**kwargs)
        if kwargs and queryset_tmp.exists():
            queryset = queryset_tmp.first()
            query_set_list = [queryset.phone_no, queryset.name, queryset.sfzh, queryset.hjdz, queryset.xzdz,
                              queryset.remark,
                              label_list[queryset.label], queryset.from_source,
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


def yqdx_mod_db_hbz(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    hjdz = request.POST.get('hjdz')
    xzdz = request.POST.get('xzdz')
    remark = request.POST.get('remark')
    label = request.POST.get('label')
    from_source = request.POST.get('from_source')

    try:
        yqdx_hbz.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, hjdz=hjdz, xzdz=xzdz,
                                              remark=remark, label=label, from_source=from_source)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result_hbz.html", {'msg': msg})


def yqdx_mod_hbz(request):
    id = request.GET.get('id')
    data_list = yqdx_hbz.objects.filter(id=id).first()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod_hbz.html", {'msg': msg})


def yqdx_del_hbz(request):
    id = request.GET.get('id')

    if yqdx_hbz.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


# 使用form组件实现验证表单，实现疫情人员导入模板上传
def muban_upload_hbz(request):
    form_obj = hbz_import_Form()
    if request.method == "POST":
        # 实例化form对象的时候，把post提交过来的数据直接传进去
        form_obj = hbz_import_Form(request.POST, request.FILES)
        # 调用form_obj校验数据的方法
        if form_obj.is_valid():
            post_data = form_obj.clean()
            excel = post_data['excel']
            begin_row_num = int(post_data['begin_row_num'])
            label = post_data['label']

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
                if col_num != 7:
                    msg = {'code': 305, 'url': '', 'error': '模板预定有效值是7列，请删除无效列，当前表格的列数为' + str(col_num)}
                else:
                    for n in range(begin_row_num - 1, row_num):
                        phone_no = sheet1.cell_value(n, 0)
                        if sheet1.cell(n, 0).ctype == 2:
                            phone_no = str(int(phone_no))
                        phone_no = phone_no.strip()
                        name = sheet1.cell_value(n, 1).strip()
                        sfzh = sheet1.cell_value(n, 2)
                        if sheet1.cell(n, 2).ctype == 2:
                            sfzh = str(int(sfzh))
                        sfzh = sfzh.strip()

                        hjdz = sheet1.cell_value(n, 3)
                        if sheet1.cell(n, 3).ctype == 2:
                            hjdz = str(int(hjdz))
                        hjdz = hjdz.strip()

                        xzdz = sheet1.cell_value(n, 4)
                        if sheet1.cell(n, 4).ctype == 2:
                            xzdz = str(int(xzdz))
                        xzdz = xzdz.strip()

                        remark = sheet1.cell_value(n, 5)
                        if sheet1.cell(n, 5).ctype == 2:
                            remark = str(int(remark))
                        remark = remark.strip()

                        from_source = sheet1.cell_value(n, 6).strip()

                        if phone_no != '' or name != '' or sfzh != '':
                            try:
                                if not yqdx_hbz.objects.filter(phone_no=phone_no, name=name).exists():  # 如果手机号不存在，则插入
                                    yqdx_hbz.objects.create(name=name, sfzh=sfzh, phone_no=phone_no, hjdz=hjdz,
                                                            xzdz=xzdz, remark=remark, from_source=from_source,
                                                            label=label)
                                    insert_succ_count += 1
                                else:
                                    update_list.append(
                                        [phone_no, name, sfzh, xzdz, remark, from_source])
                            except DataError as e:
                                insert_error_count += 1
                                err_info_list.append(
                                    '手机号:{0}，姓名：{1}，身份证号：{2}，错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))

                    msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                           'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                               str(insert_succ_count + len(update_list) + insert_error_count),
                               str(insert_succ_count), len(update_list), str(insert_error_count)),
                           'begin_row_num': begin_row_num, 'label': label}
            else:
                msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

            return render(request, 'import_result_hbz.html', {'need_update': update_list, 'msg': msg})
        # form.is_valid() 为False
        else:
            return render(request, "import_hbz.html", {"obj": form_obj})

    return render(request, "import_hbz.html", {"obj": form_obj})

def plbz_hbz(request):
    return render(request, "plbz_hbz.html")


def plbz_hbz_db(request):
    bz_type= request.POST.get('bz_type')
    label_type = int(request.POST.get('label_type'))
    excel = request.FILES.get('excel')

    label_list = ['未处理', '已研判排除', '已返甬未管', '已返甬在管', '不返甬', '其他']
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

            if bz_type == '1' and cell_0_value != '':  # 手机号
                kwargs['phone_no'] = cell_0_value
            elif bz_type == '2' and cell_0_value != '':  # 身份证号
                kwargs['sfzh'] = cell_0_value
            elif bz_type == '3' and cell_1_value != '':  # 手机第一列，姓名第二列
                kwargs['phone_no'] = cell_0_value
                kwargs['name'] = cell_1_value
            elif bz_type == '4':
                pass
            queryset = yqdx_hbz.objects.filter(**kwargs)

            if kwargs and queryset.exists():  # 如果手机号姓名同时存在，则批量设置

                queryset.update(label=label_type)
                set_succ_count += 1

            else:
                set_error_count += 1
                err_info_list.append([cell_0_value, cell_1_value])

        msg = {'code': 200,
               'content': '成功批量设置#{0}#{1}条,出错{2}条。'.format(label_list[label_type], set_succ_count,
                                                           set_error_count),
               'error': err_info_list}
    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}
    return render(request, 'hbz_label_set_result.html', {'msg': msg})