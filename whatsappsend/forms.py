"""create a form for sending whatsapp message, which contains file fields which will be used to upload the csv file and message field which will be used to enter the message to be sent to the users and option dropdown to ask whether they wanto send messages now or schedule the message."""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _



class SendMessageForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    # time = forms.DateTimeField(required=False)
    def clean_file(self):
        file = self.files.get('file', False)
        if not file:
            raise forms.ValidationError("Please select a file.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        option = cleaned_data.get("option")
        time = cleaned_data.get("time")
        if option == "schedule" and not time:
            raise ValidationError(_("Please enter the time to send the message"))
        return cleaned_data

class MessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))
    string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    # time = forms.DateTimeField(required=False)


from django.forms import formset_factory

class MessageFormText(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

MessageFormSet = formset_factory(MessageFormText, extra=1)

class UnreadResponseForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    image = forms.ImageField(required=False ,widget=forms.FileInput(attrs={'class': 'form-control'}))




