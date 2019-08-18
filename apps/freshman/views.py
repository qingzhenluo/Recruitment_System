from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail

import random

from .forms import Applyfrom, ModifyForm
from .models import Freshman
from Recruitment_System.settings import EMAIL_FROM


# Create your views here.

# 获取学生信息那里要改，应为request.Post.get('', '')
# 实现可根据专业确定学院
'''
登陆
注册
个人信息修改
提交申请书
面试时间（修改/确定）
面试（时间/地点/结果）查询
'''

# 注册、信息填写界面
class RegisterView(View):

    def get(self, request):
        apply_form = Applyfrom()
        return render(request, 'register.html', locals())

    def post(self, request):
        apply_form = Applyfrom(request.POST)
        if apply_form.is_valid():
            error = self.comfirm_password(request.POST.get('password', ''), request.POST.get('pwd', '1'))
            if not error:
                applicant = Freshman()
                applicant.newstudent_id = request.POST.get('newstudent_id', '')  # 学号
                applicant.password = request.POST.get('password', '')  # 密码
                applicant.newname = request.POST.get('newname', '')  # 姓名
                applicant.gender = request.POST.get('gender', '')  # 性别
                applicant.college = request.POST.get('college', '')  # 学院（要实现可根据专业确定）  1.用一个dict存储专业和
                # 所属学院，填入专业后匹配学院（学院在填写信息界面不显示）
                applicant.major = request.POST.get('major', '')  # 专业
                applicant.newclass = request.POST.get('newclass', '')  # 班级（需要优化成专业班级,如：数科1803）
                applicant.phone = request.POST.get('phone', '')  # 手机号
                applicant.qq = request.POST.get('qq', '')  # QQ
                applicant.email = request.POST.get('email', '')  # 邮箱
                applicant.direction = request.POST.get('direction', '')  # 选择方向
                applicant.save()
                return render(request, 'login.html')  # 提交信息成功后跳转面试时间预约界面/申请书提交界面
            else:
                return render(request, 'register.html', {'error': error})
        else:
            return render(request, 'register.html')  # 提示错误信息

    def comfirm_password(self, password, comfirm_password):
        if password != comfirm_password:
            msg = '两次密码不统一！'
            return msg


# 随机生成数字验证码
def generate_code():
    num_list = []
    for i in range(4):
        num_list.append(str(random.randint(0, 9)))
    num_code = ''.join(num_list)
    return num_code


# 可能需要重写
def send_code_by_email(email):
    title = '注册验证码'
    code = generate_code()
    content = '验证码为：' + code
    status = send_mail(title, content, EMAIL_FROM, [email])
    return status


# 查询的登录界面(可查询、更改预约时间，申请书；查询面试通知，查询面试结果）（需要学号，密码）
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):

        newstudent_id = request.POST.get('newstudent_id', '')
        password = request.POST.get('password', '')
        # user = authenticate(username=student_id, password=password)
        try:
            user = Freshman.objects.get(newstudent_id=newstudent_id)
            if user is not None:
                if user.password == password:
                    # url = '/index/' + newstudent_id + '/'
                    url = '/index/'
                    response = redirect(url)
                    response.set_cookie('newstudent_id', newstudent_id)
                    response.set_cookie('idnum', user.id)
                    return response  # 跳转到选择界面，选择查看预约、申请书、方向选择、面试通知或面试结果
                else:
                    return render(request, 'login.html', {'error': '用户名或密码不正确！'})
        except Freshman.DoesNotExist:
            return render(request, 'register.html', {'error': '你还没有注册报名哦'})


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


# 个人信息查看、修改(学号不可改)
class PersonalView(View):
    def get(self, request):
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))  # 根据cookie中的
        # newstudent_id在数据库中取出该学生传给前端
        return render(request, 'personal.html', {'student': student})  # 显示该学生选择的方向，可修改

    def post(self, request):
        newstudent_id = request.COOKIES.get('newstudent_id', '')
        student = Freshman.objects.get(newstudent_id=newstudent_id)
        modify_form = ModifyForm(request.POST)  # 验证学号，手机号，名字的格式是否正确
        if modify_form.is_valid():
            same_phones = Freshman.objects.filter(phone=request.POST.get('phone', ))
            same_student_ids = Freshman.objects.filter(newstudent_id=request.POST.get('newstudent_id', ''))
            dumplicated_phone = None
            dumplicated_student_id = None
            # 根据id检验手机号是否与别人重复
            for same_phone in same_phones:
                if same_phone.id != student.id:
                    dumplicated_phone = '手机号重复！'
            # 根据id检验学号是否与别人重复
            for same_student_id in same_student_ids:
                if same_student_id.id != student.id:
                    dumplicated_student_id = '学号重复！'
            # 如果都不重复则保存，有重复则返回该页面并提示
            if not dumplicated_phone and not dumplicated_student_id:
                student.newstudent_id = request.POST.get('newstudent_id', '')
                student.newname = request.POST.get('newname', '')
                student.gender = request.POST.get('gender', '')
                student.college = request.POST.get('college', '')
                student.major = request.POST.get('major', '')
                student.newclass = request.POST.get('newclass', '')
                student.phone = request.POST.get('phone', '')  # 手机号
                student.qq = request.POST.get('qq', '')  # QQ
                student.email = request.POST.get('email', '')  # 邮箱
                student.direction = request.POST.get('direction', '')  # 选择方向
                student.save()
                msg = '修改成功'
                if newstudent_id == student.newstudent_id:  # 没改学号正常跳回index页面
                    return render(request, 'index.html', {'msg': msg})
                else:  # 改了学号则需要退出并重新登录
                    response = log_out(request)
                    return response
            else:
                return render(request, 'personal.html', locals())
        else:
            return render(request, 'personal.html', )  # 提示错误信息


# 查看、修改预约时间界面
class AppointmentView(View):
    def get(self, request):
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))
        return render(request, 'time.html', locals())  # # 显示该学生的预约时间，

    def post(self, request):
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))
        student.appointment_one = request.POST.get('appointment_one', '')
        student.appointment_two = request.POST.get('appointment_two', '')
        student.appointment_three = request.POST.get('appointment_three', '')
        student.save()
        msg = '选择成功！记得关注面试通知哦！'
        return render(request, 'index.html', {'msg': msg})  # 可以修改


# 查询申请书界面
class ApplicationView(View):
    def get(self, request):  # 显示该学生的申请书提交情况
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))
        tip = ''
        if not student.application:
            tip = '记得及时提交申请书哦，不然就没有面试资格啦！'
        return render(request, 'application.html', locals())

    def post(self, request):  # 可以修改
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))
        student.application = request.POST.get('application', '')
        student.save()
        msg = '申请书提交成功!'
        return render(request, 'index.html', {'msg': msg})


# 面试通知界面
class InterviewInformView(View):
    # 如果从查询界面得到
    def get(self, request):
        interviewed_student = Freshman.objects.get(student_id=request.user.student,
                                                   name=request.user.name)
        interview_place = interviewed_student.interview_place
        interview_time = interviewed_student.interview_time
        application = interviewed_student.application
        if not application:
            message = '由于你未提交申请书，很抱歉你没有面试资格'
            return render(request)
        else:
            if not interview_place or not interview_time:
                message = '别着急，面试还没有开始哦'
            else:
                return render(request)
    # 如果得到此节面需要重新输入学号密码
    # def get(self, request):
    #     return render(request)
    # def post(self, request):
    #     interviewed_student = Freshman.objects.get(student_id=request.Post.student,
    #                                                                   name=request.Post.name)
    #     interview_place = interviewed_student.interview_place
    #     interview_time = interviewed_student.interview_time
    #     application = interviewed_student.application
    #     if not application:
    #         message = '由于你未提交申请书，很抱歉你没有面试资格'
    #         return render(request)
    #     else:
    #         if not interview_place or not interview_time:
    #             message = '别着急，面试还没有开始哦'
    #         else:
    #             return render(request)


# 面试结果查看界面
class InterviewResultView(View):
    def get(self, request):  # 显示该学生的面试结果，不可修改
        student = Freshman.objects.get(newstudent_id=request.COOKIES.get('newstudent_id', ''))
        return render(request, 'result.html', {'interview_result': student.interview_result})


# 退出函数
def log_out(request):
    response = render(request, 'login.html')
    response.delete_cookie('newstudent_id')
    response.delete_cookie('idnum')
    return response
