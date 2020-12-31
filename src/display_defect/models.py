from django.db import models
import jsonfield

# Create your models here.


class Main_table(models.Model):
	review_id = models.TextField()
	reviewers_score = jsonfield.JSONField(default={})
	review_closed_date = models.DateField(blank=True, default=None, null=True)

class Display_score(models.Model):
	employee_id = models.TextField()
	score = models.DecimalField(max_digits=15,decimal_places=3)
