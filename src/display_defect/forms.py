from django import forms

class DateInput(forms.DateInput):
	input_type = 'date'


class GetDateForm(forms.Form):
	my_date_field = forms.DateField(widget=DateInput)
