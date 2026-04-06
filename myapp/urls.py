"""
URL configuration for scammerreport project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('login/', views.main),
    path('login_get/', views.login_get),
    path('logout/', views.logout),
    path('home/', views.home),
    path('add_course/', views.add_course),
    path('add_dept/', views.add_dept),
    path('add_staff/', views.add_staff),
    path('add_subject/', views.add_subject),
    path('assign_subject/', views.assign_subject),
    path('change_password/', views.change_password),
    path('edit_course/<id>', views.edit_course),
    path('edit_staff/<id>', views.edit_staff),
    path('verify_students/', views.verify_students),
    path('view_course/<id>', views.view_course),
    path('view_dept/', views.view_dept),
    path('view_review/', views.view_review),
    path('view_staff/', views.view_staff),
    path('view_stdymaterial/', views.view_stdymaterial),
    path('view_subject/<id>', views.view_subject),
    path('edit_subject/<id>', views.edit_subject),
    path('delete_subject/<id>', views.delete_subject),
    path('student_change_password/', views.student_change_password),
    path('student_register/', views.student_register),
    path('update_registration/', views.update_registration),
    path('student_view_studymaterial/', views.student_view_studymaterial),
    path('add_course_post/', views.add_course_post),
    path('add_dept_post/', views.add_dept_post),
    path('add_staff_post/', views.add_staff_post),
    path('add_subject_post/', views.add_subject_post),
    path('assign_subject_post/',views.assign_subject_post),
    path('edit_course_post/',views.edit_course_post),
    path('edit_subject_post/',views.edit_subject_post),
    path('edit_staff_post/',views.edit_staff_post),
    path('edit_dept_post/',views.edit_dept_post),
    path('delete_staff/<id>',views.delete_staff),
    # path('delete_subject/<id>',views.delete_subject),
    path('delete_course/<id>',views.delete_course),
    path('edit_dept/<id>', views.edit_dept),
    path('delete_dept/<id>', views.delete_dept),
    path('student_register/',views.student_register),
    path('student_register_post/', views.student_register_post),
    path('accept_student/<id>',views.accept_student),
    path('reject_student/<id>',views.reject_student),

    path('view_review/<id>',views.view_review),
    path('delete_assign_subject/<id>',views.delete_assign_subject),
    path('block_link/<id>',views.block_link),
    path('admin_view_shared_link/',views.admin_view_shared_link),


    path('studenthome/',views.studenthome),
    path('view_profile/',views.view_profile),
    path('edit_profile/',views.edit_profile),
    path('share_link/',views.share_link),
    path('share_link_post/',views.share_link_post),
    path('edit_link/<id>', views.edit_link),
    path('delete_link/<id>',views.delete_link),
    path('admin_view_assigned_subject/<id>',views.admin_view_assigned_subject),
    path('view_others_sharedlink/',views.view_others_sharedlink),
    path('view_shared_link/',views.view_shared_link),
    path('student_view_staff/',views.student_view_staff),
    path('edit_profile_post/', views.edit_profile_post),




    path('staff_login', views.staff_login),
    path('staff_view_profile', views.staff_view_profile),
    path('staff_view_studymaterials/', views.staff_view_studymaterials),
    path('staff_add_studymaterials/', views.staff_add_studymaterials),
    path('staff_delete_studymaterials', views.staff_delete_studymaterials),
    path('staff_chat_with_user', views.staff_chat_with_user),
    path('change_passwordpost_staff', views.change_passwordpost_staff),
    path('staff_view_subject/', views.staff_view_subject),
    path('staff_view_profile/', views.staff_view_profile),
    path('stud_ask_questions/', views.stud_ask_questions),
    path('staff_delete_studymaterial/', views.staff_delete_studymaterial),
    path('staff_update_profile/', views.staff_update_profile),
    path('staff_view_students/', views.staff_view_students),
    path('staff_view_chat/', views.staff_view_chat),
    path('staff_send_chat/', views.staff_send_chat),
    path('student_view_review/<id>', views.student_view_review),
    path('load_chatbot/<id>', views.load_chatbot),
    path('student_chat/<id>', views.student_chat),
    path('student_view_studymaterial/', views.student_view_studymaterial),
    path('staff_view_reviews/', views.staff_view_reviews),
    path('student_add_review/', views.student_add_review),
    path('stud_ask_questions/', views.stud_ask_questions),
    path('get_chat_history/', views.get_chat_history),
    path('stud_upload_file/<id>', views.stud_upload_file),
    path('chat_fetch/', views.chat_fetch),
    path('chat_send/', views.chat_send),

]
