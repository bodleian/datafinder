from django.db import models

# Create your models here.

class SourceInfo(models.Model):
    """
    Table to store the source registration information for oaipmh
    """
    source =  models.TextField(primary_key=True)
    title =  models.TextField()
    description =  models.TextField()
    uri = models.TextField()
    notes =  models.TextField()
    #administrators =  models.TextField()
    #managers = models.TextField()
    #users =   models.TextField()
    #disk_allocation = models.IntegerField()
    activate = models.BooleanField()

class Users(models.Model):
    """
    Table to store the data-finder's users information 
    """
    
    sso_id = models.TextField(primary_key=True)
    username =  models.TextField()
    role =  models.TextField()
    email =  models.TextField()
    

class DFSessions(models.Model):
    """
    Table to store the data-finder's user session key information 
    """
    
    sso_id = models.TextField()
    session_id =   models.TextField()