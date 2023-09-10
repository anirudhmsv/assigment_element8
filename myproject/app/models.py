from django.db import models
# Create your models here.

class Teacher(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    room_number = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher,related_name='teacher_subjects', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,related_name='teacher_subjects', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject')
