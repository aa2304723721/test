from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from user.models import User,Address


from order.models import OrderGoods,OrderInfo
from django.views.generic import View
from django.http import HttpResponse
from celery_tasks.tasks import send_register_active_email
from django.conf import settings
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.contrib.auth import authenticate,login,logout
from utils.mixin import LoginRequiredMixin
from goods.models import GoodsSKU
from django.core.paginator import Paginator


# Create your views here.


# def register(request):
#     '''显示注册页面'''
#     if request.method=="GET":
#         # 显示注册页面
#         return render(request, "register.html")
#     else:
#         # 进行注册处理
#         # 接受数据
#         username = request.POST.get("user_name")
#         password = request.POST.get("pwd")
#         cpassword = request.POST.get("cpwd")
#         email = request.POST.get("email")
#         allow = request.POST.get("allow")
#
#         # 进行数据效验
#         if not all([username, password, email]):
#             return render(request, "register.html", {'error': '数据不完整'})
#         elif not 5 < len(username) < 20:
#             return render(request, "register.html", {'error': '用户名不合法'})
#         # 验证两次密码一致
#         if cpassword != password:
#             return render(request, "register.html", {"error": "两次密码不一致"})
#         # 邮箱验证
#         if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, "register.html", {'error': "邮箱格式不正确"})
#
#         # 接受协议
#         if allow != "on":
#             return render(request, "register.html", {"error": "请接收协议"})
#
#         # 验证用户名是否重复
#         try:
#             User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#
#         if user:
#             # 用户名已存在
#             return render(request, "register.html", {"error": "用户名已存在"})
#
#         # 进行业务处理：进行用户注册
#         user = User.objects.create_user(username, email, password)
#         user.is_active = 0
#         user.save()
#
#
#         # 返回应答，跳转首页
#         return redirect(reverse('goods:index'))


# def register_handler(request):
#     '''进行注册处理'''
#     # 接受数据
#     username = request.POST.get("user_name")
#     password = request.POST.get("pwd")
#     cpassword = request.POST.get("cpwd")
#     email = request.POST.get("email")
#     allow = request.POST.get("allow")
#
#     # 进行数据效验
#     if not all([username, password, email]):
#         return render(request, "register.html", {'error': '数据不完整'})
#     elif not 5 < len(username) < 20:
#         return render(request, "register.html", {'error': '用户名不合法'})
#     # 验证两次密码一致
#     if cpassword != password:
#         return render(request, "register.html", {"error": "两次密码不一致"})
#     # 邮箱验证
#     if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#         return render(request, "register.html", {'error': "邮箱格式不正确"})
#
#     # 接受协议
#     if allow != "on":
#         return render(request, "register.html", {"error": "请接收协议"})
#
#     # 验证用户名是否重复
#     try:
#         User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#
#     if user:
#         # 用户名已存在
#         return render(request, "register.html", {"error": "用户名已存在"})
#
#     # 进行业务处理：进行用户注册
#     user = User.objects.create_user(username, email, password)
#     user.is_active = 0
#     user.save()
#
#     # 返回应答，跳转首页
#     return redirect(reverse('goods:index'))


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''

        return render(request, "register.html")

    def post(self, request):
        '''进行注册处理'''
        # 接受数据

        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        cpassword = request.POST.get("cpwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 进行数据效验
        if not all([username, password, email]):
            return render(request, "register.html", {'error': '数据不完整'})
        elif not 5 < len(username) < 20:
            return render(request, "register.html", {'error': '用户名不合法'})
        # 验证两次密码一致

        if cpassword != password:
            return render(request, "register.html", {"error": "两次密码不一致"})
        # 邮箱验证

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {'error': "邮箱格式不正确"})

        # 接受协议

        if allow != "on":
            return render(request, "register.html", {"error": "请接收协议"})

        # 验证用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, "register.html", {"error": "用户名已存在"})

        # 进行业务处理：进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件,包含连接

        # 加密用户的身份信息
        serializer = Serializer(settings.SECRET_KEY, 600)
        info = {"confirm": user.id}
        token = serializer.dumps(info)
        token = token.decode()

        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答，跳转首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    '''用户激活'''

    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密，获取要激活的用户信息

        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info["confirm"]

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转登录页面
            return redirect(reverse("user:login"))
        except SignatureExpired as ex:
            # 激活链接已经过期
            return HttpResponse("激活链接已经过期")


class LoginView(View):
    '''登录'''

    def get(self, request):
        '''显示登录页面'''
        # 判断是否记住了用户名
        if "username" in request.COOKIES:
            username = request.COOKIES.get("username")
            checked="checked"
        else:
            username=''
            checked =''

        # 使用模板
        return render(request, "login.html", {"username":username, "checked":checked})

    def post(self, request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")

        # 验证数据
        if not all([username, password]):
            return render(request, "login.html", {"error": "数据不完整"})

        # 业务处理：登录验证
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户通过验证
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转的地址
                # 跳转到首页
                next_url = request.GET.get("next",reverse("goods:index"))

                # 跳转到next_url
                response=redirect(next_url)

                # 判断是否记住用户名
                remember=request.POST.get("remember")
                if remember == "on":
                    # 记住用户名
                    response.set_cookie("username",username,max_age=7*24*3600)
                else:
                    response.delete_cookie("username")
                return response
            else:
                # 用户未激活
                return render(request, "login.html", {"error": "账户未激活"})
        else:
            # 用户名或密码错误
            return render(request, "login.html", {"error": "用户名或密码错误"})


class LogoutView(View):
    '''退出登录'''
    def get(self,request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse("goods:index"))


class UserInfoView(LoginRequiredMixin,View):
    '''用户中心-信息页'''
    def get(self,request):
        '''显示'''

        # 获取用户个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        from redis import StrictRedis
        sr = StrictRedis(host="192.168.12.232",port="6379",db=2)

        history_key="history_%d"%user.id

        # 获取用户的最新浏览的5个商品的id
        sku_ids = sr.lrange(history_key,0,4)

        # # 从数据库中查询用户浏览的商品的具体信息
        # goods_li=GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户的浏览的历史商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        context={"page":"user","address":address,"goods_li":goods_li}


        return render(request, "user_center_info.html", context)

class UserOrderView(LoginRequiredMixin,View):
    '''用户中心-订单页'''
    def get(self,request,page):
        '''显示'''
        # 获取用户的订单信息
        user=request.user
        orders=OrderInfo.objects.filter(user=user).order_by("-create_time")

        # 遍历获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus=OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount=order_sku.count*order_sku.price
                # 动态给order_sku增加属性amount，保存订单商品的小计
                order_sku.amount=amount

            # 动态给order增加属性，保存订单状态标题
            order.status_name=OrderInfo.ORDER_STATUS[order.order_status]

            # 动态给order增加属性，保存订单商品的信息
            order.order_skus=order_skus


        #分页
        paginator=Paginator(orders,1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后5页，显示后5页
        # 4.其他情况，显示当前页，和当前页的前后两页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context={
            "order_page":order_page,
            "pages":pages,
            "page":"order",
        }

        # 使用模板
        return render(request, "user_center_order.html",context)

class AddressView(LoginRequiredMixin,View):
    '''用户中心-地址页'''
    def get(self,request):
        '''显示'''
        user = request.user

        # 获取用户的默认收货地址
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address=Address.objects.get_default_address(user)

        # 使用模板
        return render(request, "user_center_site.html", {"page": "address", "address":address})

    def post(self,request):
        '''地址添加'''
        # 接收数据
        receiver=request.POST.get("receiver")
        addr=request.POST.get("addr")
        zip_code=request.POST.get("zip_code")
        phone=request.POST.get("phone")

        # 校验数据
        if not all([receiver,addr,phone]):
            return render(request, "user_center_site.html", {"error": "数据不完整"})

        # 校验手机号
        if not re.match(r"^1[3|4|5|7|8][0-9]{9}$",phone):
            return render(request, "user_center_site.html", {"error": "手机号码格式不正确"})

        # 业务处理：地址添加
        # 获取登录用户对应User对象
        user=request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        address = Address.objects.get_default_address(user)

        if address:
            is_default=False
        else:
            is_default=True

        # 添加地址
        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,phone=phone,is_default=is_default)

        # 返回应答，刷新地址页面
        return redirect(reverse("user:address"))



