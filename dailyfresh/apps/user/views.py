from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from user.models import User
from django.core.mail import send_mail


from django.views.generic import View
from django.http import HttpResponse
from celery_tasks.tasks import send_register_active_email
from django.conf import settings
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.contrib.auth import authenticate,login


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
                next_url = request.GET.get("next",reverse("goods:index"))

                # 跳转到首页
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


class UserInfoView(View):
    '''用户中心-信息页'''
    def get(self,request):
        '''显示'''
        return render(request,"user_center_info.html",{"page":"user"})

class UserOrderView(View):
    '''用户中心-订单页'''
    def get(self,request):
        '''显示'''
        return render(request,"user_center_order.html",{"page":"order"})

class AddressView(View):
    '''用户中心-地址页'''
    def get(self,request):
        '''显示'''
        return render(request,"user_center_site.html",{"page":"address"})