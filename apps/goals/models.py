from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import extras
import bcrypt, re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def validateReg(self,request):
        errors = self.validate_inputs(request)
        if errors:
            return (False,errors)
        user_list = User.objects.filter(email=request.POST['email'].lower())
        if len(user_list)>0:
            errors.append("Email already exists")
            return (False, errors)
        else:
            pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())

            user = self.create(first_name=request.POST['first_name'],last_name=request.POST['last_name'],email=request.POST['email'].lower(),pw_hash=pw_hash)
            return (True,user)


    def validateLogin(self, request):
        errors = []
        user_list = User.objects.filter(email=request.POST['email'].lower())
        if len(user_list)<1:
            errors.append("Email/Password doesn't match!")
            return (False, errors)
        else:
            password = request.POST['password'].encode()
            if user_list[0].pw_hash == bcrypt.hashpw(password,user_list[0].pw_hash.encode()):
                return (True,user_list[0])
            else:
                errors.append("Email//Password doesn't match!")
                return (False,errors)

    def validate_inputs(self, request):
        errors = []
        if len(request.POST['first_name']) < 3 or len(request.POST['last_name']) < 3:
            errors.append("Please enter a first/last name that is longer than 2 characters")
        elif request.POST['first_name'].isalpha() == False or request.POST['last_name'].isalpha() == False:
            errors.append("Only use letter characters for first/last name field")
        if len(request.POST['email'])<1:
            errors.append("Please enter an email")
        if not EMAIL_REGEX.match(request.POST['email']):
            errors.append("Invalid email entered")
        if len(request.POST['password']) < 8 or request.POST['password'] != request.POST['confirm_pw']:
            errors.append("Passwords must match and be at least 8 characters.")
        return errors

class GoalManager(models.Manager):
    def validate_inputs(self, request):
        errors = []
        if len(request.POST['name']) < 3:
            errors.append("Please enter a Goal name that is longer than 2 characters")
        if len(request.POST['description']) < 1:
            errors.append("Please enter a description")
        if len(request.POST['mini_name']) < 3:
            errors.append("You must enter a mini-goal for your Goal")
        # if len(request.POST['mini_description']) < 3:
        #     errors.append("You must enter a mini-goal description for your Goal")
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    pw_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Goal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    user = models.ForeignKey(User)
    progress = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GoalManager()


class MiniGoal(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    user = models.ForeignKey(User)
    goal = models.ForeignKey(Goal)
    note = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Time(models.Model):
    increment = models.IntegerField()
    repeat_times = models.IntegerField()
    time_type = models.CharField(max_length=100)
    repeating = models.CharField(max_length=10)
    minigoal = models.ForeignKey(MiniGoal)
