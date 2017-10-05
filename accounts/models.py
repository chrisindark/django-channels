from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import uuid


# Create your models here.
class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        pass


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    avatar = models.ImageField(blank=True, null=True, upload_to=user_directory_path)
