from django.contrib import admin
from .models import User, Resume, JobDescription, Analysis


admin.site.register(User)
admin.site.register(Resume)
admin.site.register(JobDescription)
admin.site.register(Analysis)