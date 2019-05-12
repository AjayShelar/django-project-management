from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.


class CustomUserManager(UserManager):
    def create_superuser(self, username, phone_number, password, **kwargs):
        extra_fields = {'is_active': True, 'phone_number': phone_number}
        return super(CustomUserManager, self).create_superuser(username, None, password,
                                                               **extra_fields)


from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    phone_number = PhoneNumberField(unique=True)
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        'User', blank=True, null=True, related_name='created_users')
    edited_by = models.ForeignKey('User', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ('phone_number', )
    objects = CustomUserManager()

    @property
    def name_prop(self):
        return self.name()

    def clean(self):
        if not self.username:
            # Set username as phone number
            self.username = str(self.phone_number)

        if not self.password:
            self.set_unusable_password()

    @staticmethod
    def create_user(**kwargs):
        user = User(**kwargs)
        user.clean()
        user.save()
        return user

    def name(self):
        return str(self.first_name + " " + self.last_name).strip()

    def photo(self):
        try:
            return self.profile.photo.url
        except Exception as e:
            return None

    def __str__(self):
        return str(self.name() or self.phone_number.__str__())


class Departments(object):
    TECH = 'tech'
    ACCOUNTS = 'accounts'
    SALES = 'sales'


DEPARTMENTS_CHOICES = ((Departments.TECH, 'tech'),
                       (Departments.ACCOUNTS, 'accounts'), (Departments.SALES, 'SALES'))


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    photo = models.ImageField(null=True, blank=True)
    department = models.CharField(
        max_length=255, choices=DEPARTMENTS_CHOICES, blank=True, null=True, default='tech')


class Project(models.Model):
    '''
    Project
    '''
    created_by = models.ForeignKey(
        'User', blank=True, null=True, related_name='created_projects')
    edited_by = models.ForeignKey('User', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    avatar = models.ImageField(blank=True, null=True)


class Task(models.Model):
    project = models.ForeignKey(
        'Project', blank=True, null=True, related_name='projects_tasks')
    assignee = models.ForeignKey(
        'User', blank=True, null=True, related_name='assigned_tasks')
    edited_by = models.ForeignKey('User', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User, related_name='user_assigned_tickets', null=True, blank=True)


class SubTask(models.Model):
    task = models.ForeignKey(
        'Task', blank=True, null=True, related_name='tasks_subtasks')
    created_by = models.ForeignKey(
        'User', blank=True, null=True, related_name='created_tasks')
    edited_by = models.ForeignKey('User', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
