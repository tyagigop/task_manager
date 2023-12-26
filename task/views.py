
from django.shortcuts import render, HttpResponse, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
import twilio
from twilio.rest import Client

from django.utils import timezone
from datetime import timedelta
from .tasks import *
from .train import *
from django.http import JsonResponse

import sqlite3

import requests


account_sid = 'xxxx'
auth_token = 'xxxx'
client = Client(account_sid, auth_token)


def home(request):
    # get_data()
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
from datetime import datetime

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
        checkboxes = request.POST.getlist('accountability-partner')
        print(checkboxes)
        if len(checkboxes) > 0:
            msg = "Hey, "+user_name+" wants accountability partner.His number is "+mobile+"."
            nums = ['whatsapp:+918958028105','whatsapp:+919354964467','whatsapp:+918882567801']
            for i in nums:
                client.messages.create(
                    from_='whatsapp:+917618207974',
                    body=msg,
                    to=i
                )
                break
            subject = 'ACCOUNTABILITY PARTNER REQUEST'
            message = (
                f'-----------------------\n'
                f'   🌟{user_name} wants accountability partner.'
                f'   🌟His number is {mobile}.\n'
                f'-----------------------\n'
                )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ["hemantty0208@gmail.com","prabhat.sharma@reminthealth.com","anurag.mittal@reminthealth.com"]
            send_mail(subject, message,from_email, recipient_list)

        tasks_list = []
        for task_string in tasks:
            # Split each string in the tasks list into individual tasks
            split_tasks = re.split('\r\n', task_string)
            print(split_tasks)
            # Strip whitespace and add to the tasks_list
            tasks_list.extend([task.strip() for task in split_tasks if task.strip()])

        # print(tasks_list)


        for task in tasks_list:
            pattern = r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?:\s?[AP]M)?\b'
            match = re.search(pattern, task)
        
            if match:
                time_str = match.group()
                try:
                    # Parsing the time string in 12-hour format
                    due_time = datetime.strptime(time_str, '%I:%M %p').time()
                except ValueError:
                    # Handling 24-hour format if the above fails
                    due_time = datetime.strptime(time_str, '%H:%M').time()
                
                # only hh:mm format is accepted
                due_time = due_time.strftime('%H:%M')
                c.execute("INSERT INTO Tasks (User_Id, task_name, date, Completion_time, Priority, Achievable, Specific, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, task, timezone.now().strftime('%d-%m-%Y'), due_time, 'Medium', 'Achievable', 'Specific', 'Incomplete'))
                conn.commit()
                
                print(due_time)
            else:
                print('No time found in task:', task)
                c.execute("INSERT INTO Tasks (User_Id, task_name, date, Completion_time, Priority, Achievable, Specific, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, task, timezone.now().strftime('%d-%m-%Y'), '21:00', 'Medium', 'Achievable', 'Specific', 'Incomplete'))
                conn.commit()
        c.close()
        conn.close()
        return redirect(reverse('view_tasks', args=[mobile]))
        
    c.close()
    conn.close()

    return render(request, 'add_task2.html', {'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name})




def view_tasks(request, mobile):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
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
        completed_tasks = []
        total_tasks = []
        discarded_tasks = []
        for date in unique_dates:
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Complete'))
            completed_tasks.append(len(c.fetchall()))
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, date))
            total_tasks.append(len(c.fetchall()))
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Discarded'))
            discarded_tasks.append(len(c.fetchall()))

        c.close()

        todays_date = timezone.now().strftime('%d-%m-%Y')
        # print('today date:', todays_date)
        return render(request, 'view_tasks2.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name, 'date_selected': selected_date, 'completed_count': complete_count, 'incomplete_count': incomplete_count, 'unique_dates' : unique_dates, 'todays_date': todays_date, 'completed_tasks': completed_tasks, 'total_tasks': total_tasks, 'discarded_tasks': discarded_tasks})
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]
    current_date = timezone.now().strftime('%d-%m-%Y')
    c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, current_date, ))
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
    c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ? ORDER BY strftime('%Y%m%d', substr(date, 7, 4) || '-' ||  substr(date, 4, 2) || '-' ||         substr(date, 1, 2)    )  DESC", (user_id,))
    unique_dates = [date[0] for date in c.fetchall()]

    completed_tasks = []
    total_tasks = []
    discarded_tasks = []
    for date in unique_dates:
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Complete'))
        completed_tasks.append(len(c.fetchall()))
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, date))
        total_tasks.append(len(c.fetchall()))
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Discarded'))
        discarded_tasks.append(len(c.fetchall()))
    c.close()
    conn.close()
    todays_date = timezone.now().strftime('%d-%m-%Y')
    return render(request, 'view_tasks2.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name,'completed_count': complete_count, 'incomplete_count': incomplete_count, 'discarded_count': discarded_count, 'unique_dates' : unique_dates, 'date_selected':current_date, 'todays_date': todays_date, 'completed_tasks': completed_tasks, 'total_tasks': total_tasks, 'discarded_tasks': discarded_tasks})

from django.views.decorators.http import require_POST

@require_POST
def save_tasks(request, mobile):
    # print("POST data:", request.POST)
    task_id_test = 0
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        print(form_type)
        if form_type == 'save_tasks':
            for key, value in request.POST.items():
                # Ignore CSRF token and other non-task related fields
                
                if key not in ['csrfmiddlewaretoken']:
                    field, task_id = key.rsplit('_', 1)
                    print(field, task_id, value)
                    if field == 'task_name':
                        task_id_test = task_id
                        c.execute("UPDATE Tasks SET task_name = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
                    elif field == 'completion_time':
                        c.execute("UPDATE Tasks SET Completion_time = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
                    elif field == 'priority':
                        c.execute("UPDATE Tasks SET Priority = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
                    elif field == 'completed':
                        c.execute("UPDATE Tasks SET status = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
                    elif field == 'notes':
                        c.execute("UPDATE Tasks SET notes = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
                    elif field == 'periodicity':
                    
                        c.execute("UPDATE Tasks SET Periodicity = ? WHERE Task_Id = ?", (value, task_id))
                        conn.commit()
        else:
            print('Invalid form type')
    c.execute("SELECT * FROM Tasks WHERE Task_Id = ? AND Periodicity = ?", (task_id_test, 'Once'))
    task = c.fetchone()
    if task is None:
        c.close()
        conn.close()
        return redirect(reverse('view_periodic_tasks', args=[mobile]))
    c.close()
    conn.close()
    return redirect(reverse('view_tasks', args=[mobile]))


def view_users(request):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users")
    users = c.fetchall()
    c.close()
    conn.close()
    # print(users)
    return render(request, 'view_users.html', {'users': users})

def view_logs(request,user_id):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    # select all data with unique dates
    c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ? ORDER BY strftime('%Y%m%d', substr(date, 7, 4) || '-' ||  substr(date, 4, 2) || '-' ||         substr(date, 1, 2)    )  DESC", (user_id,))
    unique_dates = [date[0] for date in c.fetchall()]
    # print(unique_dates)

    task_data = []
    for date in unique_dates:
        c.execute("SELECT COUNT(*) FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, date))
        total_tasks = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Complete'))
        completed_tasks = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Discarded'))
        discarded_tasks = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Incomplete'))
        incomplete_tasks = c.fetchone()[0]
        task_data.append([date, total_tasks, completed_tasks, discarded_tasks, incomplete_tasks])
    # print(task_data)

    c.execute("SELECT * FROM Users WHERE User_Id = ?", (user_id,))
    user = c.fetchone()
    user_name = user[1]
    user_number = user[2]
    c.close()
    conn.close()
    return render(request, 'view_logs.html', {'unique_dates': unique_dates, 'user_id': user_id, 'task_data': task_data, 'user_name': user_name, 'user_number': user_number})



def view_periodic_tasks(request, mobile):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]
    c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND Periodicity != ?", (user_id, 'Once'))
    tasks = c.fetchall()
    daily_tasks = []
    weekly_tasks = []
    monthly_tasks = []
    for task in tasks:
        temp = []
        temp.append(task[2])
        temp.append(task[3])
        temp.append(task[4])
        temp.append(task[5])
        temp.append(task[9])
        temp.append(task[0])
        # print(temp)
        if task[10] == 'Daily':
            daily_tasks.append(temp)
        elif task[10] == 'Weekly':
            weekly_tasks.append(temp)
        elif task[10] == 'Monthly':
            monthly_tasks.append(temp)
    c.close()
    conn.close()
    return render(request, 'periodic_tasks.html', {'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name, 'daily_tasks': daily_tasks, 'weekly_tasks': weekly_tasks, 'monthly_tasks': monthly_tasks})

from django.core.mail import send_mail
from django.conf import settings

@csrf_exempt
def feedback(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        feedback = request.POST.get('feedback')
        suggestions = request.POST.get('suggestions')
        username = request.POST.get('username')

        subject = 'Task Manager Feedback Received'
        message = (
            f'-----------------------\n'
            f'   🌟 Feedback Received 🌟\n'
            f'-----------------------\n'
            f'From: {username}\n'
            f'Mobile Number: {mobile}\n'
            f'\n📝 Feedback:\n{feedback}\n'
            f'\n💡 Suggestions:\n{suggestions}\n'
            f'-----------------------'
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ["hemantty0208@gmail.com"]
        send_mail(subject, message,from_email, recipient_list)

        return HttpResponse('Feedback submitted successfully.')
    
    return render(request, 'feedback.html')

@csrf_exempt
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        subject = 'Task Manager Contact Received'
        message = (
            f'-----------------------\n'
            f'   🌟 Contact Received 🌟\n'
            f'-----------------------\n'
            f'From: {name}\n'
            f'Mobile Number/Email: {mobile}\n'
            f'\n📝 Message:\n{message}\n'
            f'-----------------------'
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ["hemantty0208@gmail.com"]
        send_mail(subject, message,from_email, recipient_list)

        return HttpResponse('Contact submitted successfully.')
    return render(request, 'contact.html')


def view_tasks2(request, mobile):
    if request.method == 'POST':
        selected_date = request.POST.get('selected_date')
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
        completed_tasks = []
        total_tasks = []
        discarded_tasks = []
        for date in unique_dates:
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Complete'))
            completed_tasks.append(len(c.fetchall()))
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, date))
            total_tasks.append(len(c.fetchall()))
            c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Discarded'))
            discarded_tasks.append(len(c.fetchall()))

        c.close()

        todays_date = timezone.now().strftime('%d-%m-%Y')
        # print('today date:', todays_date)
        return render(request, 'view_tasks.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name, 'date_selected': selected_date, 'completed_count': complete_count, 'incomplete_count': incomplete_count, 'unique_dates' : unique_dates, 'todays_date': todays_date, 'completed_tasks': completed_tasks, 'total_tasks': total_tasks, 'discarded_tasks': discarded_tasks})
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Users WHERE mobile_number = ?", (mobile,))
    user = c.fetchone()
    user_id = user[0]
    user_name = user[1]
    current_date = timezone.now().strftime('%d-%m-%Y')
    c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, current_date, ))
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
    c.execute("SELECT DISTINCT date FROM Tasks WHERE User_Id = ? ORDER BY strftime('%Y%m%d', substr(date, 7, 4) || '-' ||  substr(date, 4, 2) || '-' ||         substr(date, 1, 2)    )  DESC", (user_id,))
    unique_dates = [date[0] for date in c.fetchall()]

    completed_tasks = []
    total_tasks = []
    discarded_tasks = []
    for date in unique_dates:
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Complete'))
        completed_tasks.append(len(c.fetchall()))
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ?", (user_id, date))
        total_tasks.append(len(c.fetchall()))
        c.execute("SELECT * FROM Tasks WHERE User_Id = ? AND date = ? AND status = ?", (user_id, date, 'Discarded'))
        discarded_tasks.append(len(c.fetchall()))
    c.close()
    conn.close()
    todays_date = timezone.now().strftime('%d-%m-%Y')
    return render(request, 'view_tasks.html', {'tasks': tasks, 'mobile_number': mobile, 'user_id': user_id, 'user_name': user_name,'completed_count': complete_count, 'incomplete_count': incomplete_count, 'discarded_count': discarded_count, 'unique_dates' : unique_dates, 'date_selected':current_date, 'todays_date': todays_date, 'completed_tasks': completed_tasks, 'total_tasks': total_tasks, 'discarded_tasks': discarded_tasks})


def view_task_details(request, task_id):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Tasks WHERE Task_Id = ?", (task_id,))
    task = c.fetchone()
    c.close()
    conn.close()
    # print(task)
    return render(request, 'view_task_details.html', {'task': task})

@csrf_exempt
def update_task_details(request, task_id):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Tasks WHERE Task_Id = ?", (task_id,))
    task = c.fetchone()
    user_id = task[1]
    c.execute("SELECT * FROM Users WHERE User_Id = ?", (user_id,))
    user = c.fetchone()
    user_name = user[1]
    phone_number = user[2]
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        completion_time = request.POST.get('completion_time')
        priority = request.POST.get('priority')
        notes = request.POST.get('notes')
        periodicity = request.POST.get('periodicity')
        status = request.POST.get('status')
        c.execute("UPDATE Tasks SET task_name = ?, Completion_time = ?, Priority = ?, notes = ?, Periodicity = ?, status = ? WHERE Task_Id = ?", (task_name, completion_time, priority, notes, periodicity, status, task_id))
        conn.commit()
        c.close()
        conn.close()
        return JsonResponse({'status': 'success', 'task_id': task_id})
        return redirect(reverse('view_tasks', args=[phone_number]))
    c.close()
    conn.close()
    
    return render(request, 'update_task_details.html', {'task_id': task_id})


def delete_task(request, task_id):
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Tasks WHERE Task_Id = ?", (task_id,))
    task = c.fetchone()
    user_id = task[1]
    c.execute("SELECT * FROM Users WHERE User_Id = ?", (user_id,))
    user = c.fetchone()
    mobile = user[2]

    c.execute("DELETE FROM Tasks WHERE Task_Id = ?", (task_id,))
    conn.commit()
    c.close()
    conn.close()
    return redirect(reverse('view_tasks', args=[mobile]))

import json
from django.http import JsonResponse

@csrf_exempt
def update_task_status(request):
    task = request.POST.get('task_id')
    status = request.POST.get('status')
    # name = request.form.get('name')
    conn = sqlite3.connect('usertasks.db')
    c = conn.cursor()
    c.execute("UPDATE Tasks SET status = ? WHERE Task_Id = ?", (status, task))
    conn.commit()
    c.close()
    conn.close()


    print(f"Task {task} status updated to {status}")

    # If you're updating the task via AJAX, it's better to return a JSON response.
    # If you want to keep the redirect, you can uncomment the next line.
    #return redirect(url_for('task_user_display', last_user=name))
    
    return JsonResponse({'status': 'success', 'task': task, 'status': status})



# from django.http import JsonResponse
from .models import ClickEvent

def save_click_event(request):
    # return JsonResponse('yes')
    page_name = request.GET.get('page_name')
    element_name = request.GET.get('element_name')
    element_type = request.GET.get('element_type')

    click_date = request.GET.get('click_date')
    click_time = request.GET.get('click_time')
    country = request.GET.get('country', 'NOT FOUND')
    city = request.GET.get('city', 'NOT FOUND')
    region = request.GET.get('region', 'NOT FOUND')

    

    click_event = ClickEvent(
        page_name=page_name,
        clicked_element_name=element_name,
        clicked_element_type=element_type,
        city=city,
        region=region,
        country=country,
    )
    
    # Save the instance to the database
    click_event.save()
    # Return a JsonResponse
    return JsonResponse({"message": "Click event data saved successfully!"})


import requests
from django.http import JsonResponse

def get_country(request):
    user_ip = get_client_ip(request)
    # user_ip = '59.183.57.119'
    token = '9ddbc2d21b954f'  # Replace with your IPinfo token
    # response = requests.get(f'https://ipinfo.io/{user_ip}?token={token}')
    response = requests.get(f'https://ipinfo.io/{user_ip}/json?token=9ddbc2d21b954f')
    data = response.json()
    # print(data)
    country = data.get('country')
    city = data.get('city')
    region = data.get('region')
    return JsonResponse({'country': country, 'city': city, 'region': region})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

import datetime
from django.db.models import Q
def view_ClickEvent(request):
    queryset = ClickEvent.objects.all()
    
    countries = queryset.values_list('country', flat=True).distinct()

    # Filter logic
    country = request.GET.get('country')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')



    if country:
        # This will execute if country is not an empty string
        print(country)
        queryset = queryset.filter(country=country)
    # else:
    #     # This will execute if country is an empty string (e.g., not provided in the request)
    #     queryset = queryset.filter(country__isnull=True)


    if start_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        queryset = queryset.filter(click_date__gte=start_date)

    if end_date:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        queryset = queryset.filter(click_date__lte=end_date)

    context = {
        'query': queryset,
        'countries': countries
    }
    
    return render(request, 'click_event.html', context)


def custom_404(request, exception):
    return render(request, '404.html', {}, status=404)
