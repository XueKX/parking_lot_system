import datetime
import math
from _decimal import Decimal

import decimal
from django.shortcuts import render, redirect

from django.http import HttpResponse
from django.template.defaultfilters import register

from carport import models
from carport.models import LoginForm, AppointmentForm
from carport.train_predict.out_result import out_results, filter_results


def login(request):
    '''
    post：登录验证。其他为get，初始化网页并显示
    :param request:
    :return:
    '''
    request.session.flush()
    request.session['current_page'] = ''
    request.session['previous_page'] = ''
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        message = "检查填写内容！"
        if login_form.is_valid():
            phone = login_form.cleaned_data['phone']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(phone=phone)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['user'] = user
                    request.session['message'] = ''
                    request.session['alert_class'] = ''
                    return redirect('/carport/appointment')
                else:
                    message = "密码不正确！"
            except:
                message = "该用户不存在！"
        return render(request, 'carport/login.html', locals())

    login_form = LoginForm()
    return render(request, 'carport/login.html', locals())


def logout(request):
    request.session.flush()
    return HttpResponse('200')


def appointment(request):
    '''
    post：直接预约，生成订单。其他为get，初始化网页并显示
    :param request:
    :return:
    '''
    if not request.session.get('is_login'):
        return redirect('/carport/login')
    message = request.session['message']
    alert_class = request.session['alert_class']
    request.session['message'] = ''
    request.session['alert_class'] = ''
    if request.method == 'POST':
        carport_site = request.POST.get('carport_site')
        car_license = request.session['appointment_car_license']
        begin_time = request.session['appointment_begin_time']
        end_time = request.session['appointment_end_time']
        total = request.session['appointment_total']
        carport = models.Carport.objects.get(site=carport_site)
        owner = models.User.objects.get(phone=carport.owner_phone)
        customer = request.session['user']
        models.Order.objects.create(
            car_license=car_license,
            create_time=get_now(),
            begin_time=begin_time,
            end_time=end_time,
            amount=total,
            status='success',
            carport_site=carport_site,
            carport_owner=owner,
            carport_customer=customer,
        )
        # 更新 availcarport 状态
        boj = models.AvailCarport.objects.get(carport_site=carport_site)
        boj.site_status = 'reserved'
        boj.save()
        request.session['message'] = '预订成功!'
        request.session['alert_class'] = 'alert-success'
        return render(request, 'carport/order_to.html', locals())

    # 以下为get
    appointment_form = AppointmentForm(request.GET)
    request.session['previous_page'] = request.session['current_page']
    request.session['current_page'] = 'appointment'
    return render(request, 'carport/appointment.html', locals())


def get_carport_list(begin_time, end_time):
    '''
    获得此时间段内可选车位 排除已被租用的
    :param begin_time:
    :param end_time:
    :return:
    '''
    availCarports = models.AvailCarport.objects.filter(begin_time__lte=begin_time, end_time__gte=end_time)
    res = list(availCarports)
    for i, port in enumerate(res):
        # 有时间重复的
        obj = models.Order.objects.filter(carport_site=port.carport_site, status='success', begin_time__lte=end_time,
                                          end_time__gte=begin_time)
        for o in obj:
            if o:
                res.remove(port)
    return res


def publish(request):
    '''
    post：发出空闲车位的验证,如果已有发布，则更新发布时间。其他为get，初始化网页并显示
    :param request:
    :return:
    '''
    if not request.session.get('is_login'):
        return redirect('/carport/login')
    user_phone = request.session.get('user').phone
    # 展示已发布订单及所拥有车位
    published_list = models.AvailCarport.objects.filter(owner_phone=user_phone)
    carport_site_list = models.Carport.objects.filter(owner_phone=user_phone).values_list('site', flat=True)
    request.session['previous_page'] = request.session['current_page']
    request.session['current_page'] = 'publish'
    result_list = []
    # 提交发布表单
    if request.method == 'POST':
        carport_site = request.POST.get('carport_site')
        begin_time = request.POST.get('begin_time')
        end_time = request.POST.get('end_time')
        message = '发布成功!'
        alert_class = 'alert-success'
        if carport_site == '' or begin_time == '' or end_time == '':
            message = '请检查填写信息'
            alert_class = 'alert-danger'
        try:
            # 该车位如果在这个时间段内被租用 则不允许发布车位 否则就更新
            old = models.AvailCarport.objects.filter(carport_site=carport_site)
            filter1 = models.Order.objects.filter(carport_site=carport_site, status='success',
                                                  begin_time__lte=end_time, end_time__gte=begin_time)
            if filter1.count() != 0:
                message = '所选车位在该时间段被占用,请重新选取'
                alert_class = 'alert-danger'
                result_list = list(carport_site_list)
                result_list_size = result_list.__len__()
                return render(request, 'carport/publish.html', locals())
            else:
                old.delete()
                models.AvailCarport.objects.create(
                    carport_site=carport_site,
                    begin_time=begin_time,
                    end_time=end_time,
                    owner_phone=user_phone,
                    site_status='free'
                )
        except:
            pass

        for carport_site in carport_site_list:
            if models.Carport.objects.get(site=carport_site).current_car_license == '':
                result_list.append(carport_site)
        if result_list.__len__() == 0:
            message = '此账号下无可发布车位'
            alert_class = 'alert-warning'
        result_list_size = result_list.__len__()

        return render(request, 'carport/publish.html', locals())

    # for published in published_list:
    #     models.Order.objects.filter(carport_site=published.carport_site,begin_time=published.begin_time)
    for carport_site in carport_site_list:
        if models.Carport.objects.get(site=carport_site).current_car_license == '':
            result_list.append(carport_site)
    if result_list.__len__() == 0:
        message = '此账号下无可发布车位'
        alert_class = 'alert-warning'
    result_list_size = result_list.__len__()

    # site_status = get_site_status(user_phone)
    return render(request, 'carport/publish.html', locals())


def get_site_status(user_phone):
    '''
    获取车位订单状态
    :param carport_site_list:
    :return:
    '''
    availCarports = models.AvailCarport.objects.filter(owner_phone=user_phone)
    for port in availCarports:
        filter = models.Order.objects.filter(carport_site=port.carport_site, begin_time__lte=port.end_time,
                                             end_time__gte=port.begin_time)
        if filter.count() != 0 and filter.first().status == 'success':
            site_status = '被预约'
        else:
            site_status = '未被预约'
        return site_status


def inquiry(request):
    '''
     按时间查询此时间段内 可用车位/协商车位
    :param request:
    :return:
    '''
    appointment_message = "检查填写内容！"
    alert_class = 'alert-danger'
    appointment_form = AppointmentForm(request.GET)
    carport_list = []
    negotiate_list = []
    if appointment_form.is_valid():
        car_license = appointment_form.cleaned_data['car_license']
        begin_time = appointment_form.cleaned_data['begin_time']
        end_time = appointment_form.cleaned_data['end_time']
        diff = date_diff(begin_time, end_time)
        temp = math.floor(diff)
        if diff > temp:
            appointment_form.total = get_price(temp + 1)
        elif diff == temp:
            appointment_form.total = get_price(temp)

        message = '查询、计价成功！'
        alert_class = 'alert-success'
        data_all = out_results(path_yuce_dir="./codedir/ensemble/")
        start = int(str(begin_time).split(' ')[1].split(':')[0])
        end = int(str(end_time).split(' ')[1].split(':')[0])

        negotiate_list = filter_results(data_all, start, end)
        # 不显示当前用户
        for list in negotiate_list:
            if list[2] == request.session['user'].phone:
                negotiate_list.remove(list)

        result = get_carport_list(begin_time, end_time)
        carport_list = []
        # 不显示当前用户
        for list in result:
            if list.owner_phone != request.session['user'].phone:
                carport_list.append(list)

        request.session['negotiate_list'] = negotiate_list
        request.session['appointment_car_license'] = car_license
        request.session['appointment_begin_time'] = begin_time
        request.session['appointment_end_time'] = end_time
        request.session['appointment_total'] = appointment_form.total

    return render(request, 'carport/appointment_new.html', locals())


def get_negotiate_list(begin_time, end_time):
    '''
    返回指定时间内的可协商车位的列表(弃用)
    :param begin_time:
    :param end_time:
    :return:
    '''
    record_map = {}
    carport_list = models.Carport.objects.all()
    for i in carport_list:
        record_map.update({i.site: 0})
    # weekday= datetime.datetime.strptime(begin_time ,'%Y-%m-%d %H:%M:%S').weekday
    weekday = begin_time.weekday()
    begin_hours = datetime.datetime.strptime(str(begin_time).split(' ')[1], '%H:%M:%S')
    end_hours = datetime.datetime.strptime(str(end_time).split(' ')[1], '%H:%M:%S')

    record_list1 = list(
        models.Record.objects.filter(weekday=weekday, begin_hours__gte=begin_hours, begin_hours__lte=end_hours))
    record_list2 = list(
        models.Record.objects.filter(weekday=weekday, begin_hours__lte=begin_hours, end_hours__gte=begin_hours))
    record_list = record_list1.__add__(record_list2)
    result = []
    print(record_list1)
    print(record_list2)
    for i in record_list:
        record_map.update({i.carport_site: record_map.get(i.carport_site, 0) + 1})
    sort_list = sorted(record_map.items(), key=lambda x: x[1], reverse=False)
    success_map = {}
    for i in range(0, 15):
        try:
            success_list = list(models.Order.objects.filter(carport_site=sort_list[i][0], status='warning'))
            success_map.update({sort_list[i][0]: success_list.__len__()})
        except:
            continue
    sort_list = sorted(success_map.items(), key=lambda x: x[1], reverse=True)
    for i in range(0, len(sort_list)):
        try:
            result.append(
                (sort_list[i][0], models.Carport.objects.get(site=sort_list[i][0]).owner_phone, result.__len__() + 1))
        except:
            print(i)
    return result


def negotiate(request):
    '''
    执行协商
    :param request:
    :return:
    '''
    negotiate_list = request.session['negotiate_list']
    negotiate_list = negotiate_list[0:5] if len(negotiate_list) >= 5 else negotiate_list
    user = request.session['user']
    car_license = request.POST['car_license']
    begin_time = request.POST['begin_time']
    end_time = request.POST['end_time']
    total = get_price(date_diff(datetime.datetime.strptime(begin_time, '%Y-%m-%d %H:%M'),
                                datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')))
    try:
        order_list = models.Order.objects.filter(carport_customer_id=user.phone, status='negotiate')
        for i in order_list:
            i.status = 'invalid'
            i.save()
    except:
        pass
    try:
        n = models.Negotiation.objects.get(customer_phone=user.phone, status='underway')
        try:
            info = models.Inform.objects.filter(negotiate_id=n.id, status='success')
            for i in info:
                i.status = 'active'
                i.save()
        except:
            pass
        n.delete()
    except:
        pass

    n = models.Negotiation.objects.create(
        customer_phone=user.phone,
        last_site=negotiate_list[-1][0],
        begin_site=negotiate_list[0][0],
        negotiate_list=negotiate_list,
        record_time=get_now(),
        status='underway',
    )
    for i in range(0, len(negotiate_list)):
        o = models.Order.objects.create(
            car_license=car_license,
            create_time=get_now(),
            begin_time=begin_time,
            carport_site=negotiate_list[i][0],
            end_time=end_time,
            amount=total,
            status='negotiate',
            carport_customer_id=user.phone,
            carport_owner_id=negotiate_list[i][2],
        )
        models.Inform.objects.create(
            belong_phone=negotiate_list[i][2],
            message=user.phone + ' 请求协商车位：' + negotiate_list[i][0] + "\t预约时间为：" + begin_time + " 至 " + end_time,
            create_time=get_now(),
            status='success',
            order=o,
            negotiate_id=n.id,
        )
    return render(request, 'carport/appointment.html', locals())


def auto_negotiate():
    '''
    自动协商
    :return:
    '''
    negotiation_list = models.Negotiation.objects.filter(status='underway')
    for item in negotiation_list:
        now = get_now()
        create_time = item.record_time
        # 如果当前时间-记录时间 > 1min ，选择下一个车位进行协商
        if (now - create_time).seconds / 60 > 10:
            negotiate_next(item)


def negotiate_next(negotiation):
    '''
    协商下一车位
    :param negotiation:
    :return:
    '''
    last_site = negotiation.last_site
    negotiate_list = eval(negotiation.negotiate_list)
    index = -1
    for i in range(0, negotiate_list.__len__()):
        if last_site == negotiate_list[i][0]:
            index = i
            break
    info_list = models.Inform.objects.filter(negotiate_id=negotiation.id, status='success')
    print(info_list)
    order = list(info_list)[0].order
    for i in info_list:
        i.status = 'active'
        i.save()
        i.order.status = 'invalid'
        i.order.save()
    if index == negotiate_list.__len__() - 1:
        negotiation.status = 'end'
        negotiation.save()
        models.Inform.objects.create(
            belong_phone=negotiation.customer_phone,
            message='协商未成功',
            create_time=get_now(),
            status='danger',
            order=None
        )
        return 200
    index = index + 1
    if negotiate_list.__len__() - index >= 5:
        negotiation.begin_site = negotiate_list[index][0]
        negotiation.last_site = negotiate_list[index + 5][0]
        negotiation.save()
        for i in range(index, index + 5):
            o = models.Order.objects.create(
                car_license=order.car_license,
                create_time=get_now(),
                begin_time=order.begin_time,
                end_time=order.end_time,
                carport_site=negotiate_list[i][0],
                amount=order.amount,
                status='negotiate',
                carport_customer_id=order.carport_customer_id,
                carport_owner_id=negotiate_list[i][1],
            )
            models.Inform.objects.create(
                belong_phone=negotiate_list[i][1],
                message=order.carport_customer_id + ' 请求协商车位：' + negotiate_list[i][0] + "\t预约时间为：" + str(
                    order.begin_time) + " 至 " + str(order.end_time),
                create_time=get_now(),
                status='success',
                order=o,
                negotiate_id=negotiation.id,
            )
    else:
        negotiation.begin_site = negotiate_list[index][0]
        negotiation.last_site = negotiate_list[negotiate_list.__len__() - 1][0]
        negotiation.save()
        for i in range(index, negotiate_list.__len__()):
            o = models.Order.objects.create(
                car_license=order.car_license,
                create_time=get_now(),
                begin_time=order.begin_time,
                end_time=order.end_time,
                carport_site=negotiate_list[i][0],
                amount=order.amount,
                status='negotiate',
                carport_customer_id=order.carport_customer_id,
                carport_owner_id=negotiate_list[i][1],
            )
            models.Inform.objects.create(
                belong_phone=negotiate_list[i][1],
                message=order.carport_customer_id + ' 请求协商车位：' + negotiate_list[i][0] + "\t预约时间为：" + str(
                    order.begin_time) + " 至 " + str(order.end_time),
                create_time=get_now(),
                status='success',
                order=o,
                negotiate_id=negotiation.id,
            )


def order_to(request):
    '''
    '我预约的订单'页面
    :param request:
    :return:
    '''
    message = request.session['message']
    alert_class = request.session['alert_class']
    request.session['message'] = ''
    request.session['alert_class'] = ''
    user_phone = request.session.get('user').phone
    # order_list = models.Order.objects.filter(carport_customer_id=user_phone).exclude(status='negotiate').exclude(status='invalid')
    order_list = models.Order.objects.filter(carport_customer_id=user_phone)
    k = 0
    step_begin = -1
    step_end = -1
    try:
        negotiation = models.Negotiation.objects.get(customer_phone=user_phone, status='underway')
        negotiate_list = list(eval(negotiation.negotiate_list))
        list_len = negotiate_list.__len__()
        negotiate_begin = negotiation.begin_site
        negotiate_end = negotiation.last_site
        for i in range(0, negotiate_list.__len__()):
            if negotiate_list[i][0] == negotiate_begin:
                step_begin = i
            if negotiate_list[i][0] == negotiate_end:
                step_end = i
    except:
        pass

    request.session['previous_page'] = request.session['current_page']
    request.session['current_page'] = 'order_to'
    return render(request, 'carport/order_to.html', locals())


def order_from(request):
    '''
    '我接受的订单'页面
    :param request:
    :return:
    '''
    message = request.session['message']
    alert_class = request.session['alert_class']
    request.session['message'] = ''
    request.session['alert_class'] = ''
    user_phone = request.session.get('user').phone
    order_list = models.Order.objects.filter(carport_owner_id=user_phone).exclude(status='negotiate').exclude(
        status='invalid')

    request.session['previous_page'] = request.session['current_page']
    request.session['current_page'] = 'order_from'
    return render(request, 'carport/order_from.html', locals())


def inform(request):
    '''
    显示消息通知页面
    :param request:
    :return:
    '''
    message = request.session['message']
    alert_class = request.session['alert_class']
    request.session['message'] = ''
    request.session['alert_class'] = ''
    user_phone = request.session['user'].phone
    inform_list = []
    try:
        inform_list = models.Inform.objects.filter(belong_phone=user_phone)
    except:
        pass
    list_len = inform_list.__len__()
    request.session['previous_page'] = request.session['current_page']
    request.session['current_page'] = 'inform'
    return render(request, 'carport/inform.html', locals())


def accept(request):
    """
    接受协商
    """
    inform_id = request.POST['inform_id']
    info = models.Inform.objects.get(id=inform_id)
    o = info.order
    try:
        n = models.Negotiation.objects.get(customer_phone=o.carport_customer_id, status='underway')
        n.status = 'end'
        n.save()
        o.status = 'success'
        o.save()
        info.status = 'warning'
        info.save()
        request.session['message'] = '协商成交，订单生成成功！'
        request.session['alert_class'] = 'alert-success'
    except:
        # 已被其他车位主协商，删除其余协商车位主的通知信息
        negotiation_id = models.Negotiation.objects.get(customer_phone=o.carport_customer_id, status='end').pk
        informs = models.Inform.objects.filter(negotiate_id=negotiation_id, status='success')
        informs.delete()
        request.session['message'] = '已被协商，订单生成失败！'
        request.session['alert_class'] = 'alert-danger'
    return render(request, 'carport/order_from.html', locals())


def reject(request):
    """
    拒绝协商
    """
    inform_id = request.POST['inform_id']
    info = models.Inform.objects.get(id=inform_id)
    request.session['message'] = '拒绝协商成功'
    request.session['alert_class'] = 'alert-warning'
    info.status = 'active'
    info.order.status = 'invalid'
    info.order.save()
    info.save()
    return render(request, 'carport/order_from.html', locals())


def finish(request):
    """
    在我的订单页面提前终止订单的方法
    """
    order_id = request.GET.get('order_id')
    this_order = models.Order.objects.get(id=order_id)
    this_order.status = 'warning'
    this_order.save()
    user_phone = request.session.get('user').phone
    order_list = models.Order.objects.filter(carport_customer_id=user_phone).exclude(status='negotiate').exclude(
        status='invalid')

    # 更新 availcarport 状态
    boj = models.AvailCarport.objects.get(carport_site=this_order.carport_site)
    boj.site_status = 'free'
    boj.save()

    request.session['message'] = '终止成功'
    request.session['alert_class'] = 'alert-success'
    return render(request, 'carport/order_to.html', locals())


def cancel_published(request):
    '''
    取消已发布车位
    :param request:
    :return:
    '''
    carport_site = request.POST['carport_site']
    boj = models.AvailCarport.objects.get(carport_site=carport_site)
    boj.delete()
    return render(request, 'carport/publish.html', locals())


def cancel(request):
    """
    在我的订单页面，撤销订单的方法
    """
    order_id = request.GET.get('order_id')
    order = models.Order.objects.get(id=order_id)
    begin_time = order.begin_time
    now = get_now()
    diff = date_diff(now, begin_time)
    user_phone = request.session.get('user').phone
    carport_customer = order.carport_customer
    carport_owner = order.carport_owner
    if diff > 1:
        order.status = 'active'
        order.save()
    elif diff <= 1:
        if order.carport_owner.pk == user_phone:
            carport_owner.credit -= decimal.Decimal(0.50)
            carport_owner.remain -= decimal.Decimal(order.amount * 2)
            carport_customer.remain += decimal.Decimal(order.amount * 2)
            order.status = 'active'
            order.save()
            carport_owner.save()
            carport_customer.save()
        elif order.carport_customer.pk == user_phone:
            order.status = 'active'
            order.save()
            carport_customer.credit -= decimal.Decimal(0.50)
            carport_customer.save()
    # 更新 availcarport 状态
    boj = models.AvailCarport.objects.get(carport_site=order.carport_site)
    boj.site_status = 'free'
    boj.save()
    request.session['message'] = '取消成功'
    request.session['alert_class'] = 'alert-success'
    return render(request, 'carport/order_to.html', locals())


def date_diff(begin_time, end_time):
    '''
    辅助函数，返回end_time - begin_time的差值，结果为一个可能包含小数的数值，单位为小时
    :param begin_time:
    :param end_time:
    :return:
    '''
    diff = end_time - begin_time
    diff_str = str(diff)
    if diff_str.find(' days, ') > 0:
        d = int(diff_str.split(' days, ')[0])
        h = diff.seconds / 60 / 60
        return d * 24 + h
    elif diff_str.find(' day, ') > 0:
        h = diff.seconds / 60 / 60
        return 24 + h
    else:
        h = diff.seconds / 60 / 60
        return h


def get_price(time):
    '''
    由传入的小时数，返回相应时间的停车费
    :param time:
    :return:
    '''
    table = {1: 2, 5: 5, 24: 10}
    over_day = (int(time / 24)) * 10
    inner_day = 0
    for i in table:
        if (int(time % 24)) < i:
            inner_day = table[i]
            break
    return over_day + inner_day


def check():
    '''
    定时任务，检查订单是否超时
    :return:
    '''
    order_list = models.Order.objects.filter(status='success')
    for order in order_list:
        end_time = order.end_time
        present_time = get_now()
        carport_customer = order.carport_customer
        if present_time > end_time:
            carport_customer.credit -= decimal.Decimal(1)
            order.status = 'danger'
            carport_customer.save()
            order.save()


def get_now():
    '''
    返回特定格式的当前时间
    :return:
    '''
    return datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')


@register.filter(name='displayName')
def displayName(value, arg):
    '''
    自定义过滤器,详情见 https://blog.csdn.net/lzw2016/article/details/81546311
    :param value:
    :param arg:
    :return:
    '''
    return eval('value.get_' + arg + '_display()')
