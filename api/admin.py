from django.contrib import admin
from . models import Resume,Skill,ExtractedSkill

class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'resume_file', 'uploaded_at', 'content')

class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)

class ExtractedSkillAdmin(admin.ModelAdmin):
    list_display = ('resume','skill')

admin.site.register(Resume, ResumeAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(ExtractedSkill, ExtractedSkillAdmin)
