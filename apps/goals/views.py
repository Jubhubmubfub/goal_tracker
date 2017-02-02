from django.shortcuts import render, redirect
from .models import User, Goal, MiniGoal, Time
from django.contrib import messages
from datetime import datetime


# Create your views here.

# =========================================================
#                   HTML VIEWS
# =========================================================

def index(request):
    return render(request,'goals/index.html')

def dashboard(request):
    if 'user' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=request.session['user']['id'])
        goals = Goal.objects.filter(user_id=request.session['user']['id'])
        minigoals = MiniGoal.objects.filter(user_id=request.session['user']['id'])
        times = Time.objects.filter(minigoal__user_id=request.session['user']['id'])
        recent = find_recent_goal(request)
        if recent[0] == True:
            recent = recent[1]
        else:
            recent = {
                'name':"No goals made yet"
            }
        current = find_current_goal(request)
        if current[0] ==True:
            current = current[1]
        else:
            current = {
                'name':"No goals made yet"
            }
        # time_since = find_last_completed_time(request)
        context = {
            'user':user,
            'recent':recent,
            'current':current,
            'goals':goals,
            'minigoals':minigoals,
            'times':times
        }
        return render(request,'goals/dashboard.html',context)

def new_goal(request):
    if 'user' not in request.session:
        return redirect('/')
    else:
        numbers = range(1,32)
        numbers2 = range(1,11)
        times = ['hours','days','weeks','months','years']
        context = {
            'numbers':numbers,
            'numbers2':numbers2,
            'times': times
        }
        return render(request,'goals/new_goal.html',context)

def goal(request,goal_id):
    if 'user' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=request.session['user']['id'])
        goal = Goal.objects.get(id=goal_id)
        minigoals = MiniGoal.objects.filter(goal_id=goal_id)
        times = Time.objects.filter(minigoal__goal_id=goal_id)
        status = {
            'Pending':"Pending",
            'Active':"Active",
            'Finished':"Finished"
            }
        total_minigoals=len(minigoals)
        count = 0
        for minigoal in minigoals:
            if minigoal.status=="Finished":
                count+=1
        goal.progress = int(count/float(total_minigoals)*100)
        goal.save()
        context = {
            'status':status,
            'count':count,
            'total_minigoals':total_minigoals,
            'user':user,
            'goal':goal,
            'minigoals':minigoals,
            'times':times
        }
        return render(request, 'goals/goal.html',context)

def goal_log(request):
    if 'user' not in request.session:
        return redirect('/')
    else:
        goals = Goal.objects.filter(user_id=request.session['user']['id'])
        minigoals = MiniGoal.objects.filter(user_id= request.session['user']['id']).order_by('-finished_at')
        print minigoals
        goals2 = range(26)
        finished = {'Finished':"Finished"}
        context = {
            'goals':goals,
            'finished':finished,
            'minigoals':minigoals
        }
        return render(request, 'goals/goal_log.html',context)

# =========================================================
#                   LOGIN AND REGISTRATION
# =========================================================

def register(request):
    result = User.objects.validateReg(request)
    if result[0]==False:
        print_messages(request, result[1])
        return redirect('/')
    else:
        return log_user_in(request,result[1])

def login(request):
    result = User.objects.validateLogin(request)
    if result[0]==False:
        print_messages(request, result[1])
        return redirect('/')
    return log_user_in(request,result[1])


def log_user_in(request,user):
    request.session['user'] = {
        'id':user.id,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'email':user.email,
    }
    messages.add_message(request, messages.INFO, "successfully logged in!")
    return redirect('/dashboard')

def logout(request):
    request.session.pop('user')
    return redirect('/')

def print_messages(request, message_list):
    for message in message_list:
        messages.add_message(request, messages.INFO, message)

# =========================================================
#                  DASHBOARD LOGIC
# =========================================================

def find_recent_goal(request):
    minigoals = MiniGoal.objects.filter(user_id=request.session['user']['id'])
    if len(minigoals) < 1:
        return (False,"no goals yet")
    else:
        most_recent_goal = minigoals[0].finished_at
        recent = minigoals[0]
        for minigoal in minigoals:
            most_recent = minigoal
            if minigoal.finished_at > most_recent_goal:
                most_recent_goal = minigoal.finished_at
                most_recent = minigoal
            return (True, most_recent)


def find_current_goal(request):
    minigoals = MiniGoal.objects.filter(user_id=request.session['user']['id'])
    if not minigoals:
        return (False,"no goals yet")
    else:
        current_goal = minigoals[0].started_at
        current = minigoals[0]
        for minigoal in minigoals:
            if minigoal.started_at > current_goal:
                current_goal = minigoal.started_at
                current = minigoal
        return (True,current)

# def find_last_completed_time(request):
    # recent = find_recent_goal(request)
    # now = datetime.now()
    # time_since = now - recent.finished_at
    # return time_since


# =========================================================
#                  TRACK NEW GOAL PAGE
# =========================================================

def create_goal(request):
    errors = Goal.objects.validate_inputs(request)
    if errors:
        print_messages(request,errors)
        return redirect('/new_goal')
    else:
        user = User.objects.get(id=request.session['user']['id'])
        newGoal = Goal.objects.create(name=request.POST['name'],description=request.POST['description'],user=user,progress=0)

        # create new minigoal for each iteration of repeating
        if request.POST['repeating'] == "Yes":
            for i in range(int(request.POST['repeat_times'])):
                NewMiniGoal = MiniGoal.objects.create(name=request.POST['mini_name'],description=request.POST['mini_description'], goal=newGoal, user=user,status="Pending")
                Time.objects.create(increment=request.POST['time_increment'],repeat_times=request.POST['repeat_times'],time_type=request.POST['time'],repeating=request.POST['repeating'],minigoal=NewMiniGoal)
            return redirect('/dashboard')

        # create just one minigoal
        else:
            NewMiniGoal = MiniGoal.objects.create(name=request.POST['mini_name'],description=request.POST['mini_description'], goal=newGoal, user=user,status="Pending")
            Time.objects.create(increment=request.POST['time_increment'],repeat_times=request.POST['repeat_times'],time_type=request.POST['time'],repeating=request.POST['repeating'],minigoal=NewMiniGoal)
            return redirect('/dashboard')

# =========================================================
#                       GOAL PAGE
# =========================================================

def update(request,goal_id,minigoal_id,update):
    if update=="Finish":
        minigoal = MiniGoal.objects.get(id=minigoal_id)
        minigoal.status = "Finished"
        minigoal.finished_at = datetime.now()
        note = request.POST['note']
        minigoal.note = note
        minigoal.save()
        return redirect('/goal/{}'.format(goal_id))
    elif update=="Activate":
        minigoal = MiniGoal.objects.get(id=minigoal_id)
        minigoal.status = "Active"
        minigoal.started_at = datetime.now()
        minigoal.save()
        return redirect('/goal/{}'.format(goal_id))
