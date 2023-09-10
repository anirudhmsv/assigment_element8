from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import *
import pandas as pd


# Create your views here.
def navbar(request):
    return render(request,"navbar.html")
def adminlogin(request):
    return render(request,"login.html")
def adminteacher(request):
    return render(request,"adminteacher.html")


def loginadmin(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/admindash')
        else:
            message = "invalid"
            return render(request,"login.html",{"message":message})
        


@login_required(login_url='/')
def admindash(request):
    tc=Teacher.objects.all().count()
    return render(request,"admindash.html",{"tc":tc})

def adminviewteacher(request):
    data_query = Teacher.objects.prefetch_related('teacher_subjects')
    print('data_query::::::',data_query)
    return render(request, "adminviewteacher.html", {'data': data_query})

import os
import shutil

@login_required(login_url='/')

def import_teachers(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        if file.name.endswith('.csv'):
            try:
                temp_dir = 'profile_pictures'
                os.makedirs(temp_dir, exist_ok=True)

                data = pd.read_csv(file)
                for index, row in data.iterrows():
                    first_name = row['First Name']
                    last_name = row['Last Name']
                    email = row['Email Address']
                    phone_number = row['Phone Number']
                    room_number = row['Room Number']
                    subjects_data = str(row['Subjects taught'])
                    subjects_taught = [subject.strip() for subject in subjects_data.split(',')]

                    profile_picture_filename = row['Profile picture']
                    if profile_picture_filename == "Â":
                        profile_picture_path = 'path_to_default_image.jpg'
                        print("profile_picture_path:::::",profile_picture_path)
                    else:
                        try:
                            source_path = os.path.join(temp_dir, profile_picture_filename)
                            print("profile_picture_path:::ttt::",profile_picture_path)
                            if not os.path.isfile(profile_picture_filename):
                                shutil.copy(source_path, profile_picture_filename)
                                profile_picture_path = source_path
                                print("profile_picture_path::ttt:::",profile_picture_path)

                        except Exception as e:
                            profile_picture_path = 'path_to_default_image.jpg'
                            print("profile_picture_path::eee:::",profile_picture_path)
                    teacher, created = Teacher.objects.get_or_create(
                        first_name=first_name,  
                        last_name=last_name,
                        email=email,
                        defaults={
                            'profile_picture': profile_picture_path,
                            'phone_number': phone_number,
                            'room_number': room_number,
                        }
                    )

                    for subject_name in subjects_taught:
                        capitalized_string = subject_name.capitalize()

                        subject, created = Subject.objects.get_or_create(name=capitalized_string)
                        TeacherSubject.objects.get_or_create(teacher=teacher, subject=subject)

        
                return redirect('/adminviewteacher')
            
            except Exception as e:
                error_message = f"Error importing data: {str(e)}"
        else:
            error_message = "Invalid file format. Please upload a CSV (.csv) file."
    else:
        error_message = None

    return render(request, 'import_page.html', {'error_message': error_message})








def edit_teacher_view(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    subjects = Subject.objects.all()
    teacher_subjects = teacher.teacher_subjects.all()
    print("Teacher Subjects:", teacher_subjects)

    if request.method == 'POST':
        teacher.first_name = request.POST.get('first_name')
        teacher.last_name = request.POST.get('last_name')
        teacher.email = request.POST.get('email')
        teacher.phone_number = request.POST.get('phone_number')
        teacher.room_number = request.POST.get('room_number')
        if request.FILES.get('profile_picture'):
            teacher.profile_picture = request.FILES['profile_picture']

        selected_subject_ids = request.POST.getlist('subjects_taught')

        existing_subject_ids = teacher.teacher_subjects.values_list('subject_id', flat=True)

        subjects_to_remove = set(existing_subject_ids) - set(selected_subject_ids)
        teacher.teacher_subjects.filter(subject_id__in=subjects_to_remove).delete()

        subjects_to_add = set(selected_subject_ids) - set(existing_subject_ids)
        for subject_id in subjects_to_add:
            subject = get_object_or_404(Subject, id=subject_id)
            teacher.teacher_subjects.create(subject=subject)
        teacher.save()
        return redirect('/adminviewteacher')
    return render(request, 'edit_teacher.html', {'teacher': teacher, 'subjects': subjects})


from django.http import HttpResponse, HttpResponseRedirect

def delete_teacher_view(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher.delete()
    return redirect('/adminviewteacher')


from django.urls import reverse

def add_teacher_view(request):
    subjects = Subject.objects.all()
    if request.method == 'POST':
        # Get the selected subjects
        subjects_taught = request.POST.getlist('subjects_taught')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        room_number = request.POST.get('room_number')
        subjects_taught = request.POST.getlist('subjects_taught')
        profile_picture = request.FILES.get('profile_picture')
        print("profile_picture::::::",profile_picture)

        if profile_picture:
            # Define the upload path and save the file
            upload_path = os.path.join('profile_pictures', profile_picture.name)

        if Teacher.objects.filter(email=email).exists():
            error_message = "A teacher with this email address already exists."
            return render(request, 'add_teacher.html', {'error_message': error_message,'subjects': subjects})
        
        # Check if the number of selected subjects exceeds 5
        if len(subjects_taught) > 5:
            error_message = "A teacher can teach no more than 5 subjects."
            return render(request, 'add_teacher.html', {'error_message': error_message,'subjects': subjects})

        teacher = Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            room_number=room_number,
            profile_picture=upload_path,
        )

        for subject_id in subjects_taught:
            subject = Subject.objects.get(pk=subject_id)
            TeacherSubject.objects.create(teacher=teacher, subject=subject)

        return redirect('/adminviewteacher')
    return render(request, 'add_teacher.html', {'subjects': subjects})

