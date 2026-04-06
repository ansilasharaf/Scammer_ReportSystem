from django.db import models
from  django.contrib.auth.models import User

# Create your models here.


class department_table(models.Model):
    department_name=models.CharField(max_length=100)

class course_table(models.Model):
    DEPARTMENT=models.ForeignKey(department_table,on_delete=models.CASCADE)
    course=models.CharField(max_length=100)
    number_of_sem=models.IntegerField()

class student_table(models.Model):
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.FileField()
    name=models.CharField(max_length=100)
    phone=models.BigIntegerField()
    email=models.CharField(max_length=100)
    COURSE=models.ForeignKey(course_table,on_delete=models.CASCADE)
    sem=models.CharField(max_length=50)
    gender=models.CharField(max_length=50)
    status=models.CharField(max_length=100,default="pending")

class staff_table(models.Model):
    image = models.FileField()
    LOGIN=models.ForeignKey(User,on_delete=models.CASCADE)
    DEPARTMENT=models.ForeignKey(department_table,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone=models.BigIntegerField()
    email=models.CharField(max_length=100)
    qualification=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)



class subject_table(models.Model):
    COURSE=models.ForeignKey(course_table,on_delete=models.CASCADE)
    subject_name=models.CharField(max_length=100)
    sem=models.CharField(max_length=50)
    subject_code=models.CharField(max_length=100)

class assign_subject_to_staff_table(models.Model):
    STAFF=models.ForeignKey(staff_table,on_delete=models.CASCADE)
    SUBJECT=models.ForeignKey(subject_table,on_delete=models.CASCADE)
    date=models.DateField()
    status=models.CharField(max_length=100)

class study_materials_table(models.Model):
    ASSIGN_SUBJECT_TO_STAFF=models.ForeignKey(assign_subject_to_staff_table,on_delete=models.CASCADE)
    study_material=models.FileField()
    date=models.DateField()
    title=models.CharField(max_length=100)

class chat_table(models.Model):
    FROM=models.ForeignKey(User,on_delete=models.CASCADE,related_name='fromid')
    TO=models.ForeignKey(User,on_delete=models.CASCADE,related_name='toid')
    message=models.CharField(max_length=100)
    date=models.DateField()
    status=models.CharField(max_length=100)


class links(models.Model):
    date=models.DateField()
    title=models.CharField(max_length=100)
    status=models.CharField(max_length=100,default="Active")
    link=models.CharField(max_length=100)
    STUDENT=models.ForeignKey(student_table,on_delete=models.CASCADE)



class review_table(models.Model):
    LINK=models.ForeignKey(links,on_delete=models.CASCADE)
    STUDENT=models.ForeignKey(student_table,on_delete=models.CASCADE)
    review=models.CharField(max_length=100)
    rating=models.FloatField()
    date=models.DateField()



class chatbot(models.Model):
    STUDENT=models.ForeignKey(student_table,on_delete=models.CASCADE)
    question=models.TextField()
    answer=models.TextField()
    date=models.DateField()

class ChatHistory(models.Model):
    STUDENT =models.ForeignKey(student_table, on_delete=models.CASCADE)
    role = models.CharField(max_length=10)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)







