import uuid
import datetime

from django.db import models

from user_registration.models import User


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vote = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.CharField(max_length=112)
    block_id = models.CharField(max_length=10, null=True)

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)


class Block(models.Model):
    prev_h = models.CharField(max_length=64, blank=True)
    merkle_h = models.CharField(max_length=64, null=True, blank=True)
    block_hash = models.CharField(max_length=64, blank=True)
    nonce = models.IntegerField(null=True)
    timestamp = models.CharField(max_length=112)

    def __str__(self):
        return str(self.id)


class VoteBackup(models.Model):
    """This model acts as backup; its objects shall never be tampered."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vote = models.CharField(max_length=10)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.CharField(max_length=112, default=datetime.datetime.now().timestamp())
    block_id = models.CharField(max_length=10, null=True)

    def __str__(self):
        return "{}|{}|{}".format(self.id, self.vote, self.timestamp)
