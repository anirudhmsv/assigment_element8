from django.shortcuts import render, redirect
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