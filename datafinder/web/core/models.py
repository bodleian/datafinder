from django.db import models

# Create your models here.

class SourceInfo(models.Model):
    """
    Table to store the source registration information for oaipmh
    """
    
    id = models.AutoField(primary_key=True)
    silo =  models.TextField()
    title =  models.TextField()
    description =  models.TextField()
    notes =  models.TextField()
    administrators =  models.TextField()
    managers = models.TextField()
    users =   models.TextField()
    disk_allocation = models.IntegerField()
    activate = models.BooleanField()


    #__tablename__ = 'SourceInfo'
    # columns
#    id = Column(Integer, autoincrement=True, primary_key=True)
#    silo = Column(Unicode(50),nullable=False)
#    title = Column(Unicode(75),nullable=False)
#    description = Column(Unicode(255))
#    notes = Column(Unicode(255))
#    administrators = Column(Unicode(255))
#    managers = Column(Unicode(255))
#    users = Column(Unicode(255))
#    disk_allocation = Column(Integer(10))
#    activate = Column(Boolean)

