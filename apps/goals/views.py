from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'goals/index.html')

def dashboard(request):
    return render(request,'goals/dashboard.html')

def new_goal(request):
    numbers = range(1,32)
    numbers2 = range(1,11)
    times = ['hours','days','weeks','months','years']
    context = {
        'numbers':numbers,
        'numbers2':numbers2,
        'times': times
    }
    return render(request,'goals/new_goal.html',context)

def goal(request):
    return render(request, 'goals/goal.html')
