from django.db import models

class WorkTime(models.Model):
    date = models.DateField('date')
    hours = models.FloatField(default=0)

    def __str__(self):
        return f'{self.date} - {self.hours} hours'