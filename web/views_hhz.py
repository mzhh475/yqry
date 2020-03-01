import os
import time, datetime
import xlrd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.db.utils import DataError
from django.core.paginator import Paginator
from yqry import settings
from .models import list_type, yqdx_hhz
import xlsxwriter
from django.http import FileResponse
from django.utils.http import urlquote
from .froms import gldx_import_Form
from django.views.decorators.cache import cache_page


# Create your views here.
################红黄绿码组#################


def dx_import_hhz(request):
    return render(request, 'import_hhz.html')


def need_update_db_hhz(request):
    upload_file_name = request.POST.get('upload_file_name')
    from_source = request.POST.get('from_source')
    update_phone_list = request.POST.getlist('update_phone')
    null_list = ['', None, '/N', '空', '\\N', '不详']
    # 开始查找静态上传文件，根据手机号更新
    # 获取程序需要写入的文件路径
    path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, upload_file_name)
    book = xlrd.open_workbook(path)
    sheet1 = book.sheets()[0]
    row_num = sheet1.nrows
    err_info_list = []
    update_succ_count = 0
    update_error_count = 0

    for n in range(1, row_num):
        name = sheet1.cell_value(n, 1)
        if sheet1.cell(n, 1).ctype == 2:
            name = str(int(name))
        name = name.strip()
        sfzh = sheet1.cell_value(n, 3)
        if sheet1.cell(n, 3).ctype == 2:
            sfzh = str(int(sfzh))
        sfzh = sfzh.strip()
        phone_no = sheet1.cell_value(n, 6)
        if sheet1.cell(n, 6).ctype == 2:
            phone_no = str(int(phone_no))
        phone_no = phone_no.strip()

        if '{0}|{1}|{2}'.format(phone_no, name, sfzh) in update_phone_list:  # 判断是否在库里
            card_type = sheet1.cell_value(n, 2)
            if sheet1.cell(n, 2).ctype == 2:
                card_type = str(int(card_type))
            card_type = card_type.strip()
            xzdz = sheet1.cell_value(n, 4)
            lzqy = sheet1.cell_value(n, 5)
            jkzt = sheet1.cell_value(n, 7)
            if sheet1.cell(n, 7).ctype == 2:
                jkzt = str(int(jkzt))
            is_14 = sheet1.cell_value(n, 8)
            if sheet1.cell(n, 8).ctype == 2:
                is_14 = str(int(is_14))
            is_local = sheet1.cell_value(n, 9)
            if sheet1.cell(n, 9).ctype == 2:
                is_local = str(int(is_local))
            glzt = sheet1.cell_value(n, 10)
            if sheet1.cell(n, 10).ctype == 2:
                glzt = str(int(glzt))

            ypyj = sheet1.cell_value(n, 11).strip()
            sjly = sheet1.cell_value(n, 12).strip()
            ma_status = sheet1.cell_value(n, 13).strip()

            cjsj = sheet1.cell_value(n, 14)
            if sheet1.cell(n, 14).ctype == 3:
                cjsj = xlrd.xldate_as_datetime(sheet1.cell_value(n, 14), 0).strftime('%Y-%m-%d %H:%M:%S')
            gxdw = sheet1.cell_value(n, 15).strip()
            qz = sheet1.cell_value(n, 16).strip()
            ys = sheet1.cell_value(n, 17).strip()
            jzgl = sheet1.cell_value(n, 18).strip()
            jjgl = sheet1.cell_value(n, 19).strip()
            wfx = sheet1.cell_value(n, 20).strip()
            bzy = sheet1.cell_value(n, 21).strip()
            ssz = sheet1.cell_value(n, 22).strip()
            zlm = sheet1.cell_value(n, 23).strip()
            zhm = sheet1.cell_value(n, 24).strip()
            gzz = sheet1.cell_value(n, 25).strip()
            remark = sheet1.cell_value(n, 26).strip()

            kwargs = {}  # 动态查询的字段
            kwargs2 = {}  # 动态更新的可变字段
            if sfzh:  # 身份证号存在
                kwargs['sfzh'] = sfzh
            elif phone_no or name:  # 手机号 姓名 有一个非空
                kwargs['phone_no'] = phone_no
                kwargs['name'] = name
            try:
                query_set = yqdx_hhz.objects.filter(**kwargs)
                if name not in null_list:
                    kwargs2['name'] = name
                if sfzh not in null_list:
                    kwargs2['sfzh'] = sfzh
                if phone_no not in null_list:
                    kwargs2['phone_no'] = phone_no
                if card_type not in null_list:
                    kwargs2['card_type'] = card_type
                if xzdz not in null_list:
                    kwargs2['xzdz'] = xzdz
                if lzqy not in null_list:
                    kwargs2['lzqy'] = lzqy
                if jkzt not in null_list:
                    kwargs2['jkzt'] = jkzt
                if is_14 not in null_list:
                    kwargs2['is_14'] = is_14
                if is_local not in null_list:
                    kwargs2['is_local'] = is_local
                if glzt not in null_list:
                    kwargs2['glzt'] = glzt
                if ypyj not in null_list:
                    kwargs2['ypyj'] = ypyj
                if sjly not in null_list:
                    kwargs2['sjly'] = sjly
                if ma_status not in null_list:
                    kwargs2['ma_status'] = ma_status
                if cjsj not in null_list:
                    kwargs2['cjsj'] = cjsj
                if gxdw not in null_list:
                    kwargs2['gxdw'] = gxdw
                if qz not in null_list:
                    kwargs2['qz'] = qz
                if ys not in null_list:
                    kwargs2['ys'] = ys
                if jzgl not in null_list:
                    kwargs2['jzgl'] = jzgl
                if jjgl not in null_list:
                    kwargs2['jjgl'] = jjgl
                if wfx not in null_list:
                    kwargs2['wfx'] = wfx
                if bzy not in null_list:
                    kwargs2['bzy'] = bzy
                if ssz not in null_list:
                    kwargs2['ssz'] = ssz
                if zlm not in null_list:
                    kwargs2['zlm'] = zlm
                if zhm not in null_list:
                    kwargs2['zhm'] = zhm
                if gzz not in null_list:
                    kwargs2['gzz'] = gzz
                if from_source not in null_list:
                    kwargs2['from_source'] = from_source
                if remark not in null_list:
                    kwargs2['remark'] = remark
                query_set.update(**kwargs2)
                update_succ_count += 1
            except DataError as e:
                update_error_count += 1
                err_info_list.append('手机号:{0}，姓名：{1}，身份证号：{2},错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))
    return render(request, 'update_result_hhz.html', {
        'msg': {'code': 200, 'content': '成功覆盖更新{0}条,出错{1}条。'.format(update_succ_count, update_error_count),
                'error': err_info_list}})


@cache_page(60 * 1)
def yqdx_list_hhz(request):
    # 搜索条件获取
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ma_status = request.POST.get('ma_status')
    zlm = request.POST.get('zlm')
    zhm = request.POST.get('zhm')
    from_source = request.POST.get('from_source')

    now_page = request.GET['page']
    size = request.GET['size']
    data_list = yqdx_hhz.objects.all().order_by('timestamp')
    if (phone_no is not None) and (phone_no != ''):
        data_list = data_list.filter(phone_no=phone_no)
        now_page = '1'
    if (name is not None) and (name != ''):
        data_list = data_list.filter(name__contains=name)
        now_page = '1'
    if (sfzh is not None) and (sfzh != ''):
        data_list = data_list.filter(sfzh__contains=sfzh)
        now_page = '1'
    if (ma_status is not None) and (ma_status != '全部'):
        data_list = data_list.filter(ma_status=ma_status)
        now_page = '1'
    if (zlm is not None) and (zlm != '全部'):
        data_list = data_list.filter(zlm=zlm)
        now_page = '1'
    if (zhm is not None) and (zhm != '全部'):
        data_list = data_list.filter(zhm=zhm)
        now_page = '1'
    if (from_source is not None) and (from_source != '全部'):
        data_list = data_list.filter(from_source=from_source)
        now_page = '1'
    search_cache = {'phone_no': phone_no, 'name': name, 'sfzh': sfzh, 'ma_status': ma_status,
                    'zlm': zlm, 'zhm': zhm, 'from_source': from_source}

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

        # 查询码状态
        ma_status_list = yqdx_hhz.objects.values('ma_status').distinct()

        # 查询转绿码
        zlm_list = yqdx_hhz.objects.values('zlm').distinct()
        # 查询转黄码
        zhm_list = yqdx_hhz.objects.values('zhm').distinct()
        from_source_list = yqdx_hhz.objects.values('from_source').distinct()

        return render(request, 'yqdx_list_hhz.html',
                      {'back_page': back_page, 'now_page': now_page, 'size': size, 'total_page': total_page,
                       'next_num': next_num,
                       'pre_num': pre_num, 'has_pre': has_pre, 'has_next': has_next,
                       'from_source_list': from_source_list, 'ma_status_list': ma_status_list,
                       'zlm_list': zlm_list, 'zhm_list': zhm_list, 'search_cache': search_cache,
                       'total_count': total_count})
    else:
        return HttpResponse("库里无数据，请先批量导入或修改查询条件<br><a href='/'>首页</a><br><a href='#' onclick='history.go(-1)'>返回</a>")


def jjbd_hhz(request):
    return render(request, "jjbd_hhz.html")


def jjbd_upload_hhz(request):
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
        if kwargs and yqdx_hhz.objects.filter(**kwargs).exists():
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


def yqdx_list_export_hhz(request):
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    ma_status = request.POST.get('ma_status')

    zlm = request.POST.get('zlm')
    zhm = request.POST.get('zhm')
    from_source = request.POST.get('from_source')

    # 获取当前时间的时间戳
    timestr = str(time.time()).replace('.', '')

    data_list_tmp = yqdx_hhz.objects.all()
    if (phone_no is not None) and (phone_no != ''):
        data_list_tmp = data_list_tmp.filter(phone_no=phone_no)
    if (name is not None) and (name != ''):
        data_list_tmp = data_list_tmp.filter(name__contains=name)
    if (sfzh is not None) and (sfzh != ''):
        data_list_tmp = data_list_tmp.filter(sfzh__contains=sfzh)
    if (ma_status is not None) and (ma_status != '全部'):
        data_list_tmp = data_list_tmp.filter(ma_status=ma_status)
    if (zlm is not None) and (zlm != '全部'):
        data_list_tmp = data_list_tmp.filter(zlm=zlm)
    if (zhm is not None) and (zhm != '全部'):
        data_list_tmp = data_list_tmp.filter(zhm=zhm)
    if (from_source is not None) and (from_source != '全部'):
        data_list_tmp = data_list_tmp.filter(from_source=from_source)
    # 创建结果导出文档
    result_path = os.path.join(settings.BASE_DIR + settings.MEDIA_URL, 'export/', '{0}.xls'.format(timestr))

    export_xls = xlsxwriter.Workbook(result_path)  # 新建excel表
    export_sheet = export_xls.add_worksheet('集中隔离库查询导出')

    # 写入第一行标题
    export_sheet.write_row(0, 0,
                           ['姓名', '证件类型', '证件号码', '居住地', '来自区域', '联系电话', '健康状况', '14天是否离开本地', '是否本地', '隔离状态', '研判依据',
                            '数据来源', '码状态', '采集时间', '管辖单位', '确诊', '疑似', '集中隔离', '居家隔离', '未发现', '不在甬', '申诉中', '转绿码',
                            '转黄/红码', '工作中', '备注', '入库时间', '导入数据来源标签'])
    row_num = 1
    for for_tmp in data_list_tmp:
        query_set_list = [for_tmp.name, for_tmp.card_type, for_tmp.sfzh, for_tmp.xzdz, for_tmp.lzqy, for_tmp.phone_no,
                          for_tmp.jkzt, for_tmp.is_14, for_tmp.is_local, for_tmp.glzt, for_tmp.ypyj, for_tmp.sjly,
                          for_tmp.ma_status, for_tmp.cjsj.strftime('%Y-%m-%d %H:%M'), for_tmp.gxdw, for_tmp.qz,
                          for_tmp.ys, for_tmp.jzgl, for_tmp.jjgl, for_tmp.wfx, for_tmp.bzy, for_tmp.ssz, for_tmp.zlm,
                          for_tmp.zhm, for_tmp.gzz, for_tmp.remark, for_tmp.timestamp.strftime('%Y-%m-%d %H:%M'),
                          for_tmp.from_source]

        export_sheet.write_row(row_num, 0, query_set_list)
        row_num += 1
    # 循环完毕，开始写入
    export_xls.close()
    result = {"field": "export", "filename": timestr + '.xls'}

    return JsonResponse(result)


def bddc_hhz(request):
    return render(request, "bddc_hhz.html")


def bddc_upload_hhz(request):
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
    same_sheet.write_row(0, 0,
                         ['姓名', '证件类型', '证件号码', '居住地', '来自区域', '联系电话', '健康状况', '14天是否离开本地', '是否本地', '隔离状态', '研判依据',
                          '数据来源', '码状态', '采集时间', '管辖单位', '确诊', '疑似', '集中隔离', '居家隔离', '未发现', '不在甬', '申诉中', '转绿码', '转黄/红码',
                          '工作中', '备注', '入库时间', '导入数据来源标签'])

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
        queryset_tmp = yqdx_hhz.objects.filter(**kwargs)
        if kwargs and queryset_tmp.exists():
            queryset = queryset_tmp.first()

            query_set_list = [queryset.name, queryset.card_type, queryset.sfzh, queryset.xzdz, queryset.lzqy,
                              queryset.phone_no, queryset.jkzt, queryset.is_14, queryset.is_local, queryset.glzt,
                              queryset.ypyj, queryset.sjly, queryset.ma_status,
                              queryset.cjsj.strftime('%Y-%m-%d %H:%M'),
                              queryset.gxdw, queryset.qz, queryset.ys, queryset.jzgl, queryset.jjgl, queryset.wfx,
                              queryset.bzy, queryset.ssz, queryset.zlm, queryset.zhm, queryset.gzz, queryset.remark,
                              queryset.timestamp.strftime('%Y-%m-%d %H:%M'), queryset.from_source]

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


def yqdx_mod_db_hhz(request):
    id = request.POST.get('id')
    phone_no = request.POST.get('phone_no')
    name = request.POST.get('name')
    sfzh = request.POST.get('sfzh')
    card_type = request.POST.get('card_type')
    xzdz = request.POST.get('xzdz')
    lzqy = request.POST.get('lzqy')
    jkzt = request.POST.get('jkzt')
    is_14 = request.POST.get('is_14')
    is_local = request.POST.get('is_local')
    glzt = request.POST.get('glzt')
    ypyj = request.POST.get('ypyj')
    sjly = request.POST.get('sjly')
    ma_status = request.POST.get('ma_status')
    cjsj = request.POST.get('cjsj')
    gxdw = request.POST.get('gxdw')
    qz = request.POST.get('qz')
    ys = request.POST.get('ys')
    jzgl = request.POST.get('jzgl')
    jjgl = request.POST.get('jjgl')
    wfx = request.POST.get('wfx')
    bzy = request.POST.get('bzy')
    ssz = request.POST.get('ssz')
    zlm = request.POST.get('zlm')
    zhm = request.POST.get('zhm')
    gzz = request.POST.get('gzz')
    from_source = request.POST.get('from_source')
    remark = request.POST.get('remark')
    try:
        yqdx_hhz.objects.filter(id=id).update(phone_no=phone_no, name=name, sfzh=sfzh, card_type=card_type, xzdz=xzdz,
                                              lzqy=lzqy,
                                              jkzt=jkzt, is_14=is_14, is_local=is_local, glzt=glzt, ypyj=ypyj,
                                              sjly=sjly, ma_status=ma_status,
                                              cjsj=cjsj, gxdw=gxdw, qz=qz, ys=ys, jzgl=jzgl, jjgl=jjgl, wfx=wfx,
                                              bzy=bzy, ssz=ssz,
                                              zlm=zlm, zhm=zhm, gzz=gzz, from_source=from_source, remark=remark)
        msg = {'code': 200, 'info': '修改成功!', 'error': ''}
    except Exception as e:
        msg = {'code': 305, 'info': '修改失败!', 'error': phone_no + ':' + repr(e)}

    return render(request, "mod_result_hhz.html", {'msg': msg})


def yqdx_mod_hhz(request):
    id = request.GET.get('id')
    data_list = yqdx_hhz.objects.filter(id=id).first()

    if data_list:
        msg = {'code': 200, 'error': '', 'data_list': data_list}
    else:

        msg = {'code': 305, 'error': '该对象数据库信息不存在'}

    return render(request, "yqdx_mod_hhz.html", {'msg': msg})


def yqdx_del_hhz(request):
    id = request.GET.get('id')

    if yqdx_hhz.objects.filter(id=id).delete()[0]:
        msg = {'code': 200, 'flag': True}
    else:
        msg = {'code': 305, 'flag': False}
    return JsonResponse(msg)


# 使用form组件实现验证表单，实现疫情人员导入模板上传
def muban_upload_hhz(request):
    from_source = request.POST.get('from_source')
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
        if col_num != 27:
            msg = {'code': 305, 'url': '', 'error': '模板预定有效值是27列，请删除无效列，当前表格的列数为' + str(col_num)}
        else:
            for n in range(1, row_num):

                name = sheet1.cell_value(n, 1)
                if sheet1.cell(n, 1).ctype == 2:
                    name = str(int(name))
                name = name.strip()

                card_type = sheet1.cell_value(n, 2)
                if sheet1.cell(n, 2).ctype == 2:
                    card_type = str(int(card_type))
                card_type = card_type.strip()

                sfzh = sheet1.cell_value(n, 3)
                if sheet1.cell(n, 3).ctype == 2:
                    sfzh = str(int(sfzh))
                sfzh = sfzh.strip()

                xzdz = sheet1.cell_value(n, 4)
                lzqy = sheet1.cell_value(n, 5)
                phone_no = sheet1.cell_value(n, 6)
                if sheet1.cell(n, 6).ctype == 2:
                    phone_no = str(int(phone_no))
                phone_no = phone_no.strip()

                jkzt = sheet1.cell_value(n, 7)
                if sheet1.cell(n, 7).ctype == 2:
                    jkzt = str(int(jkzt))
                is_14 = sheet1.cell_value(n, 8)
                if sheet1.cell(n, 8).ctype == 2:
                    is_14 = str(int(is_14))
                is_local = sheet1.cell_value(n, 9)
                if sheet1.cell(n, 9).ctype == 2:
                    is_local = str(int(is_local))
                glzt = sheet1.cell_value(n, 10)
                if sheet1.cell(n, 10).ctype == 2:
                    glzt = str(int(glzt))

                ypyj = sheet1.cell_value(n, 11).strip()
                sjly = sheet1.cell_value(n, 12).strip()
                ma_status = sheet1.cell_value(n, 13).strip()

                cjsj = sheet1.cell_value(n, 14)
                if sheet1.cell(n, 14).ctype == 3:
                    cjsj = xlrd.xldate_as_datetime(sheet1.cell_value(n, 14), 0).strftime('%Y-%m-%d %H:%M:%S')

                gxdw = sheet1.cell_value(n, 15).strip()
                qz = sheet1.cell_value(n, 16).strip()
                ys = sheet1.cell_value(n, 17).strip()
                jzgl = sheet1.cell_value(n, 18).strip()
                jjgl = sheet1.cell_value(n, 19).strip()
                wfx = sheet1.cell_value(n, 20).strip()
                bzy = sheet1.cell_value(n, 21).strip()
                ssz = sheet1.cell_value(n, 22).strip()
                zlm = sheet1.cell_value(n, 23).strip()
                zhm = sheet1.cell_value(n, 24).strip()
                gzz = sheet1.cell_value(n, 25).strip()
                remark = sheet1.cell_value(n, 26).strip()

                kwargs = {}  # 动态查询的字段
                if sfzh:  # 身份证号存在
                    kwargs['sfzh'] = sfzh
                elif phone_no or name:  # 手机号 姓名 有一个非空
                    kwargs['phone_no'] = phone_no
                    kwargs['name'] = name
                try:
                    if kwargs and not yqdx_hhz.objects.filter(**kwargs).exists():  # 如果手机号不存在，则插入
                        yqdx_hhz.objects.create(phone_no=phone_no, name=name, sfzh=sfzh, card_type=card_type, xzdz=xzdz,
                                                lzqy=lzqy, jkzt=jkzt,
                                                is_14=is_14, is_local=is_local, glzt=glzt, ypyj=ypyj, sjly=sjly,
                                                ma_status=ma_status, cjsj=cjsj, gxdw=gxdw, qz=qz, ys=ys, jzgl=jzgl,
                                                jjgl=jjgl,
                                                wfx=wfx, bzy=bzy, ssz=ssz, zlm=zlm, zhm=zhm, gzz=gzz,
                                                from_source=from_source, remark=remark)
                        insert_succ_count += 1
                    else:
                        update_list.append([phone_no, name, sfzh, lzqy, ma_status, from_source])
                except DataError as e:
                    insert_error_count += 1
                    err_info_list.append(
                        '手机号:{0}，姓名：{1}，身份证号：{2}，错误信息：{3}'.format(phone_no, name, sfzh, repr(e)))

            msg = {'code': 200, 'url': '{0}.{1}'.format(timestr, file_type), 'error': err_info_list,
                   'content': '总执行条数{0},成功新增{1}条，待覆盖{2}条,出错{3}条'.format(
                       str(insert_succ_count + len(update_list) + insert_error_count),
                       str(insert_succ_count), len(update_list), str(insert_error_count)), 'from_source': from_source}
    else:
        msg = {'code': 305, 'url': '', 'error': '不支持该类型文件'}

    return render(request, 'import_result_hhz.html', {'need_update': update_list, 'msg': msg})
