from django import forms
from django.contrib.auth import authenticate, get_user_model

# Create your form here

User = get_user_model()


class UserLoginForm(forms.Form):
	username = forms.CharField(max_length=50)
	password = forms.CharField(widget=forms.PasswordInput)

	def clean(self, *args, **kwargs):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')

		if username and password:
			user = authenticate(username=username, password=password)
			if not user:
				raise forms.ValidationError("This user does not exist.")
			if not user.check_password(password):
				raise forms.ValidationError("Incorrect password.")
			if not user.is_active:
			    raise forms.ValidationError("The user is no longer active.")
		return super(UserLoginForm, self).clean(*args, **kwargs)		


class UserRegisterForm(forms.ModelForm):
	email = forms.EmailField(label='Email address')
	email_confirm = forms.EmailField(label='Email Comfirm')
	password = forms.CharField(widget=forms.PasswordInput)
	password_confirm = forms.CharField(widget=forms.PasswordInput)

	class Meta:
		model = User 
		fields = [
			'username',
			'email',
			'email_confirm',
			'password',
			'password_confirm',
		]

	def clean_email_confirm(self, *args, **kwargs):
		email = self.cleaned_data.get('email')
		email_confirm  =self.cleaned_data.get('email_confirm')
		if email != email_confirm:
			raise forms.ValidationError("Email must match.")
		email_qs = User.objects.filter(email=email)
		if email_qs.exists():
			raise forms.ValidationError("This email has been registerd. Choose another.")
		return email_confirm 

	def clean_password_confirm(self, *args, **kwargs):
		password = self.cleaned_data.get('password')
		password_confirm = self.cleaned_data.get('password_confirm')

		if password != password_confirm:
			raise forms.ValidationError("Password must match.")
		return password