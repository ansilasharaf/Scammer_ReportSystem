from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,Group

# Create your views here.
from myapp.file_chat_bot import extract_text_from_pdf
from myapp.models import *
from myapp.file_chat_bot import extract_text_from_pdf, generate_qa_pairs_from_chunks, save_qa_pairs, \
    chunk_text_intelligently

def main(request):
    # us=User.objects.exclude(id=1)
    # for i in us:
    #     i.delete()
    return render(request,"login.html")
def logout(request):
    return render(request,"login.html")



def login_get(request):
    if request.method=="POST":
        username=request.POST["username"]
        password=request.POST["password"]
        user = authenticate(request,username=username,password=password)
        if user is not None:
            if user.groups.filter(name="Admin").exists():
                login(request,user)
                return redirect('/myapp/home/')
            elif user.groups.filter(name="Student").exists():
                login(request, user)

                print(user,'uuuuuuuuuuuuuuuuuu')
                return redirect('/myapp/studenthome/')

            elif student_table.objects.filter(status__in=["pending","Rejected"]).exists():
                messages.success(request,'please wait for admin approval')
                return redirect('/myapp/login/')


        else:
            return redirect('/myapp/login/')
        return redirect('/myapp/login/')


def home(request):
    return render(request,"homepge.html")

def studenthome(request):
    return render(request,"studenthome.html")


def add_course(request):
    return render(request,"Admin/add_course.html")

def add_course_post(request):
    course_name=request.POST['course_name']
    no_sem=request.POST['no_sem']

    ob=course_table()

    ob.course=course_name
    ob.number_of_sem=no_sem
    ob.DEPARTMENT=department_table.objects.get(id=request.session['did'])
    ob.save()
    return redirect(f'/myapp/view_course/{request.session["did"]}')


def add_dept(request):
    return render(request,"Admin/add_dept.html")

def add_dept_post(request):
    dept_name=request.POST['dept_name']

    ob=department_table()
    ob.department_name=dept_name
    ob.save()
    return redirect('/myapp/view_dept/')

def add_staff(request):
    a=department_table.objects.all()
    return render(request,"Admin/add_staff.html",{'data':a})

# def add_staff_post(request):
#     image=request.FILES['image']
#     name=request.POST['name']
#     phone=request.POST['phone']
#     email=request.POST['email']
#     qualification=request.POST['qualification']
#     gender=request.POST['gender']
#     department=request.POST['department']
#     username=request.POST['username']
#     password=request.POST['password']
#
#
#
#     user=User.objects.create(
#         username=username,
#         password=make_password(password),
#         email=email,
#         first_name=request.POST.get('name')
#     )
#
#     user.groups.add(Group.objects.filter(name="Staff"))
#     user.save()
#     ob = staff_table()
#     ob.image = image
#     ob.name = name
#     ob.phone = phone
#     # ob.email = email
#     ob.qualification = qualification
#     ob.gender = gender
#     ob.LOGIN=user
#     ob.DEPARTMENT_id=department
#     ob.save()
#     return redirect('/myapp/view_staff/')



def add_staff_post(request):
    image = request.FILES['image']
    name = request.POST['name']
    phone = request.POST['phone']
    email = request.POST['email']
    qualification = request.POST['qualification']
    gender = request.POST['gender']
    department = request.POST['department']
    username = request.POST['username']
    password = request.POST['password']

    user = User.objects.create(
        username=username,
        password=make_password(password),
        email=email,
        first_name=name
    )

    # Fix: get single Group object
    staff_group = Group.objects.get(name="Staff")
    user.groups.add(staff_group)
    user.save()

    ob = staff_table()
    ob.image = image
    ob.name = name
    ob.phone = phone
    ob.email = email
    ob.qualification = qualification
    ob.gender = gender
    ob.LOGIN = user
    ob.DEPARTMENT_id = department
    ob.save()

    return redirect('/myapp/view_staff/')



def add_subject(request):
    return render(request,"Admin/add_subject.html")

def add_subject_post(request):
    sub_name=request.POST['sub_name']
    sub_code=request.POST['sub_code']
    sem=request.POST['sem']

    ob=subject_table()
    ob.COURSE=course_table.objects.get(id=request.session['cid'])
    ob.subject_name=sub_name
    ob.subject_code=sub_code
    ob.sem=sem
    ob.save()
    return redirect(f'/myapp/view_subject/{request.session["cid"]}')



def assign_subject(request):
    # ob=assign_subject_to_staff_table.objects.get(id=id)
    obs=staff_table.objects.get(id=request.session['staff_id'] )
    ob=subject_table.objects.filter(COURSE__DEPARTMENT__id=obs.DEPARTMENT.id)
    return render(request, "Admin/assign_subject.html",{'data':ob})

def assign_subject_post(request):
    subject=request.POST['subject_id']

    ob=assign_subject_to_staff_table()
    ob.STAFF=staff_table.objects.get(id=request.session['staff_id'])
    ob.SUBJECT_id=subject
    ob.date=datetime.now()
    ob.save()
    return redirect(f'/myapp/admin_view_assigned_subject/{request.session["staff_id"]}')




def admin_view_assigned_subject(request,id):
    request.session['staff_id'] = id
    # ob=assign_subject_to_staff_table.objects.get(id=id)
    ob=assign_subject_to_staff_table.objects.filter(STAFF_id=id)
    return render(request, "Admin/view_assigned_subject.html",{'data':ob,'id':id})



def student_chat(request,id):
    request.session['tid'] = id
    tid = id
    if not tid:
        return HttpResponse("No chat target set in session.", status=400)
    try:
        to_user = User.objects.get(id=tid)
    except User.DoesNotExist:
        return HttpResponse("Target user not found.", status=404)

    return render(request, 'Student/chat.html', {
        'from_id': request.user.id,
        'to_id': tid,
        'to_name': to_user.username,
    })



def delete_assign_subject(request, id):
    a = assign_subject_to_staff_table.objects.get(id=id)
    a.delete()
    return redirect(f'/myapp/admin_view_assigned_subject/{request.session["staff_id"]}')


def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        user = request.user

        if check_password(old_password, user.password):
            user.set_password(new_password)   # ✅ CORRECT
            user.save()

            logout(request)  # optional but recommended
            messages.success(request, "Password changed successfully. Please login again.")
            return redirect('/myapp/login/')
        else:
            messages.error(request, "Current password is incorrect.")
            return redirect('/myapp/change_password/')

    return render(request, "Admin/change_password.html")




def edit_course(request,id):
    request.session['id'] = id
    ob = course_table.objects.get(id=id)
    return render(request, "Admin/edit_course.html", {'data': ob})

def edit_course_post(request):
    course_name=request.POST['course_name']
    no_sem=request.POST['no_sem']

    ob=course_table.objects.get(id=request.session['id'])
    ob.course=course_name
    ob.number_of_sem=no_sem
    ob.save()
    return redirect(f'/myapp/view_course/{request.session["did"]}')


def delete_course(request, id):
    a = course_table.objects.get(id=id)
    a.delete()
    return redirect(f'/myapp/view_course/{request.session["did"]}')

def edit_subject(request,id):
    request.session['cid'] = id
    ob=subject_table.objects.get(id=id)
    return render(request,"Admin/edit_subject.html",{'data':ob})

def edit_subject_post(request):
    sub_name=request.POST['sub_name']
    sub_code=request.POST['sub_code']
    sem=request.POST['sem']

    ob=subject_table.objects.get(id=request.session['cid'])
    ob.subject_name=sub_name
    ob.sem=sem
    ob.subject_code=sub_code
    ob.save()
    return redirect(f'/myapp/view_course/{request.session["did"]}')

def edit_staff(request,id):
    request.session['id']=id
    b=staff_table.objects.get(id=id)
    a=department_table.objects.all()
    return render(request,"Admin/edit_staff.html",{'data':b,'data2':a})

def edit_staff_post(request):
    name=request.POST['name']
    phone=request.POST['phone']
    email=request.POST['email']
    qualification=request.POST['qualification']
    gender=request.POST['gender']
    department=request.POST['department']

    ob=staff_table.objects.get(id=request.session['id'])
    if 'image' in request.FILES:
        image=request.FILES['image']
        ob.image=image
        ob.save()


    ob.name = name
    ob.phone = phone
    ob.email = email
    ob.qualification = qualification
    ob.gender = gender
    ob.DEPARTMENT_id = department
    ob.save()
    return redirect('/myapp/view_staff/')

def delete_staff(request,id):
    a=staff_table.objects.get(id=id)
    a.delete()
    return redirect('/myapp/view_staff/')


def edit_dept(request,id):
    request.session['id'] = id
    ob = department_table.objects.get(id=id)
    return render(request,"Admin/edit_dept.html",{'data': ob})


def edit_dept_post(request):
    dept_name=request.POST['dept_name']

    ob=department_table.objects.get(id=request.session['id'])
    ob.department_name=dept_name
    ob.save()
    return redirect('/myapp/view_dept/')

def delete_dept(request,id):
    a=department_table.objects.get(id=id)
    a.delete()
    return redirect('/myapp/view_dept/')


def verify_students(request):
    a=student_table.objects.all()
    return render(request,"Admin/verify_students.html",{'data':a})


def accept_student(request,id):
    student_table.objects.filter(LOGIN_id=id).update(status="Accepted")
    return redirect('/myapp/verify_students/')

def reject_student(request,id):
    student_table.objects.filter(LOGIN_id=id).update(status="Rejected")
    return redirect('/myapp/verify_students/')

def view_course(request,id):
    request.session['did']=id
    ob = course_table.objects.filter(DEPARTMENT_id=id)
    return render(request,"Admin/view_course.html",{'data':ob})

def view_subject(request,id):
    request.session['cid']=id
    ob = subject_table.objects.filter(COURSE_id=id)
    return render(request,"Admin/view_subject.html",{'data':ob,'course':request.session['did']})

def delete_subject(request, id):
    ob = subject_table.objects.get(id=id)
    ob.delete()
    cid = request.session['cid']
    return redirect('/myapp/view_subject/' + str(cid))


def view_dept(request):
    ob=department_table.objects.all()
    return render(request,"Admin/view_dept.html",{'data':ob})


def admin_view_shared_link(request):
    ob=links.objects.filter(STUDENT__LOGIN_id=request.user.id)
    return render(request,"Admin/view_sharedlink.html",{'data':ob})


def view_review(request,id):
    data=review_table.objects.filter(LINK_id=id)
    return render(request,"Admin/view_review.html",{"data":data})

def block_link(request,id):
    a=links.objects.filter(id=id).update(status="block")
    messages.success(request,"Link Blocked Success")
    return redirect('/myapp/admin_view_shared_link/')




def view_stdymaterial(request):
    data=study_materials_table.objects.all()
    return render(request, "Admin/view_stdymaterial.html",{"data":data})

def view_staff(request):
    ob=staff_table.objects.all()
    return render(request,"Admin/view_staff.html",{'data':ob})

def update_registration(request):
    return render(request, "Student/edit_profile.html")

def student_change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        user = request.user

        if check_password(old_password, user.password):
            user.set_password(new_password)   # ✅ CORRECT
            user.save()

            logout(request)  # optional but recommended
            messages.success(request, "Password changed successfully. Please login again.")
            return redirect('/myapp/login/')
        else:
            messages.error(request, "Current password is incorrect.")
            return redirect('/myapp/student_change_password/')

    return render(request, "Student/change_pswrd.html")

def student_register(request):
    ob = course_table.objects.all()
    return render(request,"Student/student_register.html",{'data':ob})

def student_register_post(request):
    image=request.FILES['image']
    name=request.POST['name']
    phone=request.POST['phone']
    email=request.POST['email']
    gender=request.POST['gender']
    course=request.POST['course']
    sem=request.POST['sem']
    username=request.POST['username']
    password=request.POST['password']

    user = User.objects.create(
        username=username,
        password=make_password(password),
        email=email,
        first_name=password
    )
    user.save()
    user.groups.add(Group.objects.get(name="Student"))
    ob = student_table()
    ob.image = image
    ob.name = name
    ob.phone = phone
    ob.email = email
    ob.gender = gender
    ob.sem=sem
    ob.COURSE_id=course
    ob.LOGIN = user
    ob.save()
    return redirect('/myapp/login/')

def view_profile(request):
    print(request.user.id,'llllllllllllll')
    a=student_table.objects.get(LOGIN=request.user.id)
    return render(request,"Student/view_profile.html",{'data':a})

def edit_profile(request):
    c=course_table.objects.all()
    a=student_table.objects.get(LOGIN=request.user.id)
    return render(request,"Student/edit_profile.html",{'data':a,'data2':c})



def edit_profile_post(request):
    name = request.POST['name']
    phone = request.POST['phone']
    email = request.POST['email']
    gender = request.POST['gender']
    course = request.POST['course']
    sem = request.POST['sem']


    ob = student_table.objects.get(LOGIN=request.user.id)

    if 'image' in request.FILES:
        image = request.FILES['image']

        ob.image = image
        ob.save()

    ob.name = name
    ob.phone = phone
    ob.email = email
    ob.gender = gender
    ob.sem = sem
    ob.COURSE_id = course
    ob.save()
    return redirect('/myapp/view_profile/')



def share_link(request):
    return render(request,"Student/share_link.html")

# def share_link_post(request):
#     title=request.POST['title']
#     link=request.POST['link']
#     ob=links()
#     ob.title=title
#     ob.date=datetime.now().today()
#     ob.link=link
#     ob.status="pending"
#     ob.STUDENT=student_table.objects.get(LOGIN_id=request.user.id)
#     ob.save()
#     return redirect('/myapp/view_shared_link/')

from django.http import HttpResponse
from datetime import datetime

from django.http import HttpResponse
from datetime import datetime
from .models import links, student_table
from .phishing_transformer import predict_url


def share_link_post(request):

    title = request.POST['title']
    link = request.POST['link']

    # Run phishing detection
    result = predict_url(link)

    status = result[0]
    message = result[1]

    print(status)

    # If malicious
    if status == "unsafe":
        return HttpResponse(f"""
        <script>
        alert('⚠️ Malicious Link Detected: {message}');
        window.location='/myapp/view_shared_link/';
        </script>
        """)

    # If safe
    else:
        ob = links()
        ob.title = title
        ob.date = datetime.now()
        ob.link = link
        ob.status = "pending"
        ob.STUDENT = student_table.objects.get(LOGIN_id=request.user.id)
        ob.save()

        return HttpResponse("""
        <script>
        alert('✅ Link shared successfully');
        window.location='/myapp/view_shared_link/';
        </script>
        """)



def edit_link(request,id):
    ob = links.objects.get(id=id)

    if request.method=="POST":
        title = request.POST['title']
        link = request.POST['link']
        ob = links.objects.get(id=id)
        ob.title = title
        ob.date = datetime.now().today()
        ob.link = link
        ob.status = "pending"
        ob.save()
        return redirect('/myapp/view_shared_link/')

    return render(request,"Student/edit_link.html",{"data":ob})


def delete_link(request,id):
    ob = links.objects.get(id=id)

    ob.delete()
    return redirect('/myapp/view_shared_link/')




def view_shared_link(request):
    data=links.objects.filter(STUDENT__LOGIN_id=request.user.id)
    return render(request,"Student/view_shared_link.html",{"data":data})

def view_others_sharedlink(request):
    data = links.objects.exclude(STUDENT__LOGIN_id=request.user.id)
    return render(request, "Student/view_others_sharedlink.html", {"data": data})



def student_view_review(request,id):
    request.session['link_id']=id
    data=review_table.objects.filter(LINK__id=id)
    return render(request,"Student/view_review.html",{"data":data})


def student_send_review(request,id):
    ob = review_table.objects.get(id=id)

    if request.method=="POST":
        title = request.POST['title']
        link = request.POST['link']
        ob = links.objects.get(id=id)
        ob.title = title
        ob.date = datetime.now().today()
        ob.link = link
        ob.status = "pending"
        ob.save()
        return redirect('/myapp/view_shared_link/')

    return render(request,"Student/edit_link.html",{"data":ob})





def student_view_staff(request):
    ob=student_table.objects.get(LOGIN__id=request.user.id)
    data=staff_table.objects.filter(DEPARTMENT__id=ob.COURSE.DEPARTMENT.id)
    return render(request,"Student/view_staff.html",{"data":data})

def student_view_studymaterial(request):

    std=student_table.objects.get(LOGIN=request.user.id).COURSE
    sem=student_table.objects.get(LOGIN=request.user.id).sem
    a=study_materials_table.objects.filter(ASSIGN_SUBJECT_TO_STAFF__SUBJECT__COURSE_id=std,ASSIGN_SUBJECT_TO_STAFF__SUBJECT__sem=sem)
    return render(request, "Student/view_studymaterial.html",{'data':a})


def student_add_review(request):
    try:
        lid = request.session.get('link_id')
        if not lid:
            return JsonResponse({'status': 'error', 'message': 'Not logged in'})

        student = student_table.objects.get(LOGIN_id=request.user.id)


        link_id = request.session.get('link_id')
        if not link_id:
            return JsonResponse({'status': 'error', 'message': 'No active link in session'})

        link = links.objects.get(id=link_id)

        review_text = request.POST.get('review', '').strip()
        rating = request.POST.get('rating', '0')

        if not review_text:
            return JsonResponse({'status': 'error', 'message': 'Review cannot be empty'})

        try:
            rating = float(rating)
            if not (0 <= rating <= 5):
                raise ValueError
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Rating must be 0–5'})

        if review_table.objects.filter(STUDENT=student, LINK=link).exists():
            return JsonResponse({'status': 'error', 'message': 'You have already reviewed this'})

        review_table.objects.create(
            LINK=link,
            STUDENT=student,
            review=review_text,
            rating=rating,
            date=datetime.today(),
        )

        return JsonResponse({'status': 'ok', 'message': 'Review submitted'})

    except student_table.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student not found'})
    except links.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Link not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def staff_view_reviews(request):
    try:
        reviews = review_table.objects.select_related('STUDENT', 'LINK').filter(LINK__id=request.session['link_id']).order_by('-date')

        data = []
        for r in reviews:
            data.append({
                'id': r.id,
                'review': r.review,
                'rating': float(r.rating),
                'date': str(r.date),
                'student_name': r.STUDENT.name,
                'student_email': r.STUDENT.email,
                'student_img': r.STUDENT.image.url if r.STUDENT.image else '',
                'link': r.LINK.id,
            })

        return JsonResponse({'status': 'ok', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


#####################################



def staff_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        if user.groups.filter(name="Staff").exists():
            login(request, user)
            return JsonResponse({'status': 'ok','type':'Staff','lid':user.id})
        else:
            return JsonResponse({'status': 'ok','type':'unknown','lid':user.id})
    else:

        return JsonResponse({'task':'invalid'})


def staff_view_profile(request):
    lid=request.POST['lid']
    a=staff_table.objects.get(LOGIN=lid)
    return JsonResponse({
        'status':'ok',
        'name':a.name,
        'image':a.image.url,
        'phone':a.phone,
        'email':a.email,
        'qualification':a.qualification,
        'gender':a.gender,
        'department':a.DEPARTMENT.department_name})


def edit_profile_flutter(request):
    name = request.POST['name']
    image = request.POST['image']
    phone = request.POST['phone']
    email = request.POST['email']
    qualification = request.POST['qualification']
    gender = request.POST['gender']
    department = request.POST['department']


    ob = staff_table.objects.get(LOGIN=request.user.id)

    if 'image' in request.FILES:
        image = request.FILES['image']

        ob.image = image
        ob.save()

    ob.name = name
    ob.image = image
    ob.phone = phone
    ob.email = email
    ob.qualification = qualification
    ob.gender = gender
    ob.department = department
    ob.save()
    return JsonResponse({'status': 'ok', })




def staff_view_studymaterials(request):
    sid = request.POST['sid']
    ob = study_materials_table.objects.filter(
        ASSIGN_SUBJECT_TO_STAFF__SUBJECT_id=sid
    )

    mdata = []

    for i in ob:
        data = {
            'date': i.date,
            'file': request.build_absolute_uri(i.study_material.url),
            'title': i.title,
            'id': i.id
        }
        mdata.append(data)

    return JsonResponse({'status': 'ok', 'data': mdata})



def staff_add_studymaterials(request):
    sid=request.POST['sid']
    study_material = request.FILES["study_material"]
    title = request.POST["title"]
    ob=study_materials_table()
    ob.study_material=study_material
    ob.ASSIGN_SUBJECT_TO_STAFF=assign_subject_to_staff_table.objects.get(SUBJECT_id=sid)
    ob.title=title
    ob.date=datetime.now()
    ob.save()
    return JsonResponse({'status':'ok'})

def staff_delete_studymaterials(request):
    id=request.POST['id']
    a = study_materials_table.objects.get(id=id)
    a.delete()
    return JsonResponse({'status':'ok'})

def staff_chat_with_user(request):
    return JsonResponse({'status':'ok'})

def change_passwordpost_staff(request):
    oldpassword=request.POST['oldpassword']
    newpassword=request.POST['newpassword']
    confirmpassword=request.POST['confirmpassword']
    lid=request.POST['lid']
    print(oldpassword,newpassword,confirmpassword,lid)
    p=User.objects.get(id=lid).password
    print(request.user)
    f=check_password(oldpassword,p)
    if f:
        user=User.objects.get(id=lid)
        user.set_password(newpassword)
        user.save()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'no'})

def staff_view_subject(request):
    lid = request.POST.get('lid')

    staff = staff_table.objects.get(LOGIN_id=lid)
    assignments = assign_subject_to_staff_table.objects.filter(STAFF=staff)

    data = []
    for a in assignments:
        sub = a.SUBJECT
        data.append({
            'id': sub.id,
            'subject': sub.subject_name,
            'course': sub.COURSE.course,
            'sem': sub.sem,
            'assigned_date': str(a.date),
        })

    return JsonResponse({'status': 'ok', 'data': data})


def staff_delete_studymaterial(request):
    print(request.POST)
    ob=study_materials_table.objects.get(id=request.POST['id'])
    ob.delete()
    return JsonResponse({'status': 'ok'})



#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================

import os
import json
import pdfplumber
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Use your Gemini Config
GEMINI_API_KEY = "AIzaSyAuSprjUEoavVr38OacNUw4gMG-qOif2_Q"  # Keep your key safe!
client = genai.Client(api_key=GEMINI_API_KEY)
QA_PAIRS_FILE = os.path.join(settings.BASE_DIR, "Al_qa_pairs.json")

# ----------------------------
# View 1: Upload and Generate KB
# ----------------------------
def stud_upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            text = extract_text_from_pdf(file_path)
            chunks = chunk_text_intelligently(text, chunk_size=10000, overlap=500)
            qa_pairs = generate_qa_pairs_from_chunks(chunks, 10)
            save_qa_pairs(qa_pairs)

            if os.path.exists(file_path): os.remove(file_path)
            return JsonResponse({'status': 'ok', 'message': 'Knowledge Base Updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'failed'})


# ----------------------------
# View 2: Ask Questions (The Bot)
# ----------------------------

def stud_ask_questions(request):
    if request.method == 'POST':
        question = request.POST['question']
        lid = request.POST['lid']

        if not question:
            return JsonResponse({'status': 'error', 'message': 'No question provided'})
        ChatHistory.objects.create(
            STUDENT=student_table.objects.get(LOGIN=lid),
            role='user',
            message=question
        )
        if not os.path.exists(QA_PAIRS_FILE):
            answer = "I haven't been trained on any documents yet. Please upload a PDF first!"
        else:
            try:
                with open(QA_PAIRS_FILE, "r", encoding="utf-8") as f:
                    qa_pairs = json.load(f)

                if not qa_pairs:
                    answer = "My knowledge base is empty."
                else:
                    # Semantic Search using TF-IDF
                    questions_list = [pair['question'] for pair in qa_pairs]
                    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))

                    # Fit and transform the KB questions
                    question_vectors = vectorizer.fit_transform(questions_list)
                    # Transform the user's current question
                    query_vector = vectorizer.transform([question])

                    # Calculate Cosine Similarity
                    similarities = cosine_similarity(query_vector, question_vectors)[0]

                    # Get top 3 most relevant context pieces
                    top_indices = np.argsort(similarities)[-3:][::-1]

                    context_parts = []
                    for idx in top_indices:
                        if similarities[idx] > 0.1:  # Threshold to ensure relevance
                            context_parts.append(
                                f"Context Question: {qa_pairs[idx]['question']}\n"
                                f"Context Answer: {qa_pairs[idx]['answer']}"
                            )

                    context = "\n\n".join(context_parts)

                    # 3. GENERATION: Call Gemini with Context
                    prompt = f"""
                    You are a helpful Study Assistant. Answer the student's question based on the provided context from their uploaded documents.

                    Context from Documents:
                    {context if context else "No direct matches found in documents."}

                    Student Question: {question}

                    Instructions:
                    - If the context helps, use it.
                    - If the context doesn't help, use your general knowledge but mention it's not in the document.
                    - Keep the tone professional and supportive.
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    answer = response.text.strip()

            except Exception as e:
                print(f"Error processing: {e}")
                answer = "Sorry, I encountered an error while searching my knowledge base."

        # 4. PERSISTENCE: Save the Bot's answer to the database
        ChatHistory.objects.create(
            STUDENT=student_table.objects.get(LOGIN=lid),
            role='bot',
            message=answer
        )

        return JsonResponse({
            'status': 'ok',
            'answer': answer
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_chat_history(request):
    lid = request.POST['lid']
    history = ChatHistory.objects.filter(STUDENT__LOGIN_id=lid)
    chat_list = []
    for chat in history:
        chat_list.append({
            'role': chat.role,
            'text': chat.message
        })
    return JsonResponse({'status': 'ok', 'data': chat_list})


def staff_update_profile(request):
   print(request.POST)
   print(request.FILES)
   ob=staff_table.objects.get(LOGIN__id=request.POST['lid'])
   ob.name=request.POST['name']
   ob.phone=request.POST['phone']
   ob.email=request.POST['email']
   ob.qualification=request.POST['qualification']
   ob.gender=request.POST['gender']
   ob.save()
   return JsonResponse({'status': 'ok'})

def staff_view_students(request):
   print(request.POST)
   print(request.FILES)
   sid=request.POST['sid']
   obs=subject_table.objects.get(id=sid)
   ob=student_table.objects.filter(COURSE__id=obs.COURSE.id,sem=obs.sem)
   data=[]
   for i in ob:
       data.append({"id":i.id,"lid":i.LOGIN.id,"name":i.name,"img":i.image.url,"email":i.email})

   return JsonResponse({'status': 'ok',"data":data})


def staff_view_chat(request):
    sender_id = request.POST.get('sender_id')
    receiver_id = request.POST.get('receiver_id')

    try:
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        # Get all messages between the two users (both directions)
        messages = chat_table.objects.filter(
            FROM=sender, TO=receiver
        ) | chat_table.objects.filter(
            FROM=receiver, TO=sender
        )
        messages = messages.order_by('date', 'id')

        data = []
        for msg in messages:
            data.append({
                'id': msg.id,
                'sender_id': msg.FROM.id,
                'receiver_id': msg.TO.id,
                'message': msg.message,
                'date': str(msg.date),
                'status': msg.status,
            })

        return JsonResponse({'status': 'ok', 'data': data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def staff_send_chat(request):
    sender_id = request.POST.get('sender_id')
    receiver_id = request.POST.get('receiver_id')
    message = request.POST.get('message')

    try:
        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        chat_table.objects.create(
            FROM=sender,
            TO=receiver,
            message=message,
            date=datetime.today(),
            status='sent',
        )

        return JsonResponse({'status': 'ok', 'message': 'Message sent'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})






#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================
#================================================MAIN===================================================================

import os
import json
import pdfplumber
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from google import genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Use your Gemini Config
GEMINI_API_KEY = "AIzaSyAgyhiX1QMXB_E5vGBYE1ikyW4qkInM5F4"  # Keep your key safe!
client = genai.Client(api_key=GEMINI_API_KEY)
QA_PAIRS_FILE = os.path.join(settings.BASE_DIR, "Al_qa_pairs.json")

# ----------------------------
# View 1: Upload and Generate KB
# ----------------------------

def load_chatbot(request,id):
    request.session['smid']=id
    return render(request,"Student/chatbot.html")

def stud_upload_file(request,id):
        ob=study_materials_table.objects.get(id=id)
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)

        file_path = fs.path(str(ob.study_material))

        try:
            text = extract_text_from_pdf(file_path)
            chunks = chunk_text_intelligently(text, chunk_size=10000, overlap=500)
            qa_pairs = generate_qa_pairs_from_chunks(chunks, 10)
            save_qa_pairs(qa_pairs)

            if os.path.exists(file_path): os.remove(file_path)
            return JsonResponse({'status': 'ok', 'message': 'Knowledge Base Updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})



# ----------------------------
# View 2: Ask Questions (The Bot)
# ----------------------------

def stud_ask_questions(request):
    if request.method == 'POST':
        question = request.POST['question']
        lid = request.user.id

        if not question:
            return JsonResponse({'status': 'error', 'message': 'No question provided'})
        ChatHistory.objects.create(
            STUDENT=student_table.objects.get(LOGIN=lid),
            role='user',
            message=question
        )
        if not os.path.exists(QA_PAIRS_FILE):
            answer = "I haven't been trained on any documents yet. Please upload a PDF first!"
        else:
            try:
                with open(QA_PAIRS_FILE, "r", encoding="utf-8") as f:
                    qa_pairs = json.load(f)

                if not qa_pairs:
                    answer = "My knowledge base is empty."
                else:
                    # Semantic Search using TF-IDF
                    questions_list = [pair['question'] for pair in qa_pairs]
                    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))

                    # Fit and transform the KB questions
                    question_vectors = vectorizer.fit_transform(questions_list)
                    # Transform the user's current question
                    query_vector = vectorizer.transform([question])

                    # Calculate Cosine Similarity
                    similarities = cosine_similarity(query_vector, question_vectors)[0]

                    # Get top 3 most relevant context pieces
                    top_indices = np.argsort(similarities)[-3:][::-1]

                    context_parts = []
                    for idx in top_indices:
                        if similarities[idx] > 0.1:  # Threshold to ensure relevance
                            context_parts.append(
                                f"Context Question: {qa_pairs[idx]['question']}\n"
                                f"Context Answer: {qa_pairs[idx]['answer']}"
                            )

                    context = "\n\n".join(context_parts)

                    # 3. GENERATION: Call Gemini with Context
                    prompt = f"""
                    You are a helpful Study Assistant. Answer the student's question based on the provided context from their uploaded documents.

                    Context from Documents:
                    {context if context else "No direct matches found in documents."}

                    Student Question: {question}

                    Instructions:
                    - If the context helps, use it.
                    - If the context doesn't help, use your general knowledge but mention it's not in the document.
                    - Keep the tone professional and supportive.
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )
                    answer = response.text.strip()

            except Exception as e:
                print(f"Error processing: {e}")
                answer = "Sorry, I encountered an error while searching my knowledge base."

        # 4. PERSISTENCE: Save the Bot's answer to the database
        ChatHistory.objects.create(
            STUDENT=student_table.objects.get(LOGIN=lid),
            role='bot',
            message=answer
        )

        return JsonResponse({
            'status': 'ok',
            'answer': answer
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def get_chat_history(request):
    lid = request.POST['lid']
    history = ChatHistory.objects.filter(STUDENT__LOGIN_id=lid)
    chat_list = []
    for chat in history:
        chat_list.append({
            'role': chat.role,
            'text': chat.message
        })
    return JsonResponse({'status': 'ok', 'data': chat_list})


def chat_send(request):
    """POST: save a new message."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'})

    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'status': 'error', 'message': 'Empty message'})

    tid = request.session.get('tid')
    if not tid:
        return JsonResponse({'status': 'error', 'message': 'No target in session'})

    try:
        from_user = User.objects.get(id=request.user.id)
        to_user = User.objects.get(id=tid)
        chat_table.objects.create(
            FROM=from_user, TO=to_user,
            message=message, date=datetime.today(), status='sent',
        )
        return JsonResponse({'status': 'ok'})
    except User.DoesNotExist as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def chat_fetch(request):
    """POST: fetch all messages between FROM (session user) and TO (session tid)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'})

    tid = request.session.get('tid')
    from_id = request.user.id

    if not tid:
        return JsonResponse({'status': 'error', 'message': 'No target in session'})

    msgs = (
        chat_table.objects.filter(FROM_id=from_id, TO_id=tid) |
        chat_table.objects.filter(FROM_id=tid, TO_id=from_id)
    ).order_by('date', 'id')

    data = [{
        'id': m.id,
        'from_id': m.FROM_id,
        'message': m.message,
        'date': str(m.date),
        'status': m.status,
        'is_me': m.FROM_id == from_id,
    } for m in msgs]

    return JsonResponse({'status': 'ok', 'data': data})






