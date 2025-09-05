from django.db import models
from django.urls import reverse
from django.utils import timezone
import datetime
import os
from django_countries.fields import CountryField


class Position(models.Model):
    title = models.CharField(max_length=50)
    def __str__(self):
        return self.title 



class Student(models.Model):
    name = models.CharField(max_length=200, null=False)
    identityNumber = models.CharField(max_length=200, null=False)
    address = models.CharField(max_length=200, null=True)
    department = models.CharField(max_length=200, null=True)
    id = models.AutoField(primary_key=True)
    mobile= CountryField(blank=True, null=False)
    position= models.ForeignKey(Position,on_delete=models.CASCADE)
    file=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('student_edit', kwargs={'pk': self.pk})
   
