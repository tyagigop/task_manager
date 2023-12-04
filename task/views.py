
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
import twilio
from twilio.rest import Client

from django.utils import timezone
from datetime import timedelta
from .tasks import *
from django.http import JsonResponse

import sqlite3

import requests


account_sid = 'AC350f7216d74983430088fa7b2f6e2662'
auth_token = '84cd88946166bc0183150148e382f6fc'
client = Client(account_sid, auth_token)


def home(request):
    return render(request, 'home.html')

@csrf_exempt
def bot(request):
    message = request.POST
    user_name = message['ProfileName']
    user_message = message['Body']
    user_number = message['From']
    phone_number = user_number[12:]
    conn = sqlite3.connect('usertasks.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (phone_number,))
    user = c.fetchone()
    if user is None:
        c.execute("INSERT INTO Users (Username, Mobile_Number) VALUES (?, ?)", (user_name, phone_number))
        conn.commit()
        c.close()
        client.messages.create(
            from_='whatsapp:+917618207974',
            body="Hey "+user_name+"! Welcome to Task Manager. You can add your tasks here and we will remind you to complete them. Type 'help' to know more.",
            to=user_number
        )
        return HttpResponse("Done")
    else:
        c.close()
        conn.close()
        handle_user_response(request, user_number, user_message)


    print(phone_number)
    return HttpResponse("Done")


def add_task(request, mobile):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]
    print(user_id, user_name)
    if request.method == 'POST':
        # Check if the request contains 'mobile_number'
        tasks = []
        # Process the task form
        task_names = request.POST.getlist('task_name[]')
        completion_times = request.POST.getlist('completion_time[]')
        priorities = request.POST.getlist('priority[]')
        achievables = request.POST.getlist('achievable[]')
        specifics = request.POST.getlist('specific[]')
        print(task_names,"yes")
        # Combine the task details into a list of dictionaries
        # only dd/mm/yyyy format is accepted
        todays_date = timezone.now().strftime('%d-%m-%Y')

        

        for i in range(len(task_names)):
            c.execute("INSERT INTO Tasks (User_Id, task_name, date, Completion_time, Priority, Achievable, Specific,status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, task_names[i], todays_date, completion_times[i], priorities[i], achievables[i], specifics[i],'Incomplete'))
            conn.commit()
        
        c.close()
        tasks.append(task_names)
        tasks.append(completion_times)
        tasks.append(priorities)
        tasks.append(achievables)
        tasks.append(specifics)
        # You can now process or save the tasks, for now, let's print them
        print("Tasks:")
        for task in tasks:
            print(task)
        # You may want to save the tasks to the database or session for future use
        return redirect(reverse('view_tasks', args=[mobile]))
    c.close()
    conn.close()
    return render(request, 'add_task.html', {'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name})

import re

def add_task2 (request, mobile):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]

    if request.method == 'POST':
        tasks = request.POST.getlist('task_name')
        print(tasks)

        tasks_list = []
        for task_string in tasks:
            # Split each string in the tasks list into individual tasks
            split_tasks = re.split(',|\r\n', task_string)
            # Strip whitespace and add to the tasks_list
            tasks_list.extend([task.strip() for task in split_tasks if task.strip()])

        print(tasks_list)

        for task in tasks_list:
            # Split each task into name and completion time
            task_parts = task.split('-')
            print(task_parts)
            # Check if there are both name and completion time
            if len(task_parts) >= 2:
                task_name = task_parts[0].strip()
                completion_time = task_parts[1].strip()
                completion_time = completion_time.replace(' ', '')
                print(completion_time,task_name)

                # Check if the completion time is in the correct format
                # ... (your validation logic here)

                # Insert into database
                c.execute("INSERT INTO Tasks (User_Id, task_name, date, Completion_time, Priority, Achievable, Specific, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, task_name, timezone.now().strftime('%d-%m-%Y'), completion_time, 'Medium', 'Achievable', 'Specific', 'Incomplete'))
                conn.commit()
                



            else:
                print("Invalid task format:", task)
            
        return redirect(reverse('view_tasks', args=[mobile]))
        


    return render(request, 'add_task2.html', {'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name})




def view_tasks(request, mobile):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
        # convert selected date to dd-mm-yyyy
        # selected_date = selected_date[::-1]
        print(selected_date)
        conn = sqlite3.connect('usertasks.db')
        c = conn.cursor()
        c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
        user = c.fetchone()
        user_id = user[0]
        user_name = user[1]
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, selected_date))
        tasks = c.fetchall()
        complete_count = 0
        incomplete_count = 0
        for task in tasks:
            if task[8]=='Complete':
                complete_count+=1
            else:
                incomplete_count+=1
        
        
        c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ? ORDER BY strftime('%Y%m%d', substr(date, 7, 4) || '-' ||  substr(date, 4, 2) || '-' ||         substr(date, 1, 2)    )  DESC", (user_id,))
        unique_dates = [date[0] for date in c.fetchall()]
        c.close()

        todays_date = timezone.now().strftime('%d-%m-%Y')
        print('today date:', todays_date)

        return render(request, 'view_tasks.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name, 'date_selected': selected_date, 'completed_count': complete_count, 'incomplete_count': incomplete_count, 'unique_dates' : unique_dates, 'todays_date': todays_date})
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]
    current_date = timezone.now().strftime('%d-%m-%Y')
    c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, current_date))
    tasks = c.fetchall()
    complete_count = 0
    incomplete_count = 0
    discarded_count = 0
    for task in tasks:
        if task[8]=='Complete':
            complete_count+=1
        elif task[8]=='Discarded':
            discarded_count+=1
        else:
            incomplete_count+=1

    #  select distinct dates by user_id

    # c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ?",(user_id))
    # unique_dates = c.fetchall()
    c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ? ORDER BY strftime('%Y%m%d', substr(date, 7, 4) || '-' ||  substr(date, 4, 2) || '-' ||         substr(date, 1, 2)    )  DESC", (user_id,))
    unique_dates = [date[0] for date in c.fetchall()]

    print(unique_dates)
    print(type(unique_dates))

    

    c.close()
    conn.close()
    todays_date = timezone.now().strftime('%d-%m-%Y')
    return render(request, 'view_tasks.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name,'completed_count': complete_count, 'incomplete_count': incomplete_count, 'discarded_count': discarded_count, 'unique_dates' : unique_dates, 'date_selected':current_date, 'todays_date': todays_date})


@csrf_exempt
def update_notes(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        notes = request.POST.get('notes')

        # Update the notes in your database using task_id

        conn = sqlite3.connect('usertasks.db')
        c = conn.cursor()
        c.execute("UPDATE Tasks SET notes = ? WHERE Task_Id = ?", (notes, task_id))
        conn.commit()
        c.close()
        conn.close()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})

@csrf_exempt
def update_task(request):
    conn = sqlite3.connect('usertasks.db')
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        column = request.POST.get('column')
        value = request.POST.get('value')
        print(task_id, column, value)
        if column == 'completion_time':
            value = value.replace(' ', '')
            # check for correct format 00:00
            if len(value) != 5 or value[2] != ':':
                return JsonResponse({'status': 'error'})
            else:
                # Update the completion time in your database using task_id
                c = conn.cursor()
                c.execute("UPDATE Tasks SET Completion_time = ? WHERE Task_Id = ?", (value, task_id))
                conn.commit()
                c.close()
                conn.close()
                return JsonResponse({'status': 'success'})
        elif column == 'priority':
            c = conn.cursor()
            c.execute("UPDATE Tasks SET Priority = ? WHERE Task_Id = ?", (value, task_id))
            conn.commit()
            c.close()
            conn.close()
            return JsonResponse({'status': 'success'})
        else:
            c = conn.cursor()
            c.execute("UPDATE Tasks SET task_name = ? WHERE Task_Id = ?", (value, task_id))
            conn.commit()
            c.close()
            conn.close()
            return JsonResponse({'status': 'success'})
        


    return JsonResponse({'status': 'error'})