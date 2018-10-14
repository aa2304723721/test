from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from user.models import User,Address


from django.views.generic import View
from django.http import HttpResponse
from celery_tasks.tasks import send_register_active_email
from django.conf import settings
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.contrib.auth import authenticate,login,logout
from utils.mixin import LoginRequiredMixin


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

        serializer = Serializer(settings.SECRET_KEY, 600)
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
        return render(request, "login.html",{"username":username,"checked":checked})

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

        return render(request,"user_center_info.html",{"page":"user","address":address})

class UserOrderView(LoginRequiredMixin,View):
    '''用户中心-订单页'''
    def get(self,request):
        '''显示'''
        # 获取用户的订单信息

        return render(request,"user_center_order.html",{"page":"order"})

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
        return render(request,"user_center_site.html",{"page":"address","address":address})

    def post(self,request):
        '''地址添加'''
        # 接收数据
        receiver=request.POST.get("receiver")
        addr=request.POST.get("addr")
        zip_code=request.POST.get("zip_code")
        phone=request.POST.get("phone")

        # 校验数据
        if not all([receiver,addr,phone]):
            return render(request,"user_center_site.html",{"error":"数据不完整"})

        # 校验手机号
        if not re.match(r"^1[3|4|5|7|8][0-9]{9}$",phone):
            return render(request,"user_center_site.html",{"error":"手机号码格式不正确"})

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



