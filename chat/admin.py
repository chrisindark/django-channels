from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(
    Thread,
    list_display=["id", "title", "slug"],
    list_display_links=["id", "title"],
    ordering=["title"],
    prepopulated_fields={"slug": ("title",)},
)

admin.site.register(
    Message,
    list_display=["id", "thread", "content"],
    ordering=["-id"],
)

admin.site.register(
    Room,
    list_display=["id", "title", "staff_only"],
    list_display_links=["id", "title"],
)


