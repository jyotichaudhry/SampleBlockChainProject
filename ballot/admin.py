from django.contrib import admin

# Register your models here.
from ballot.models import Vote, Block, VoteBackup

admin.site.register(Vote)
admin.site.register(VoteBackup)
admin.site.register(Block)
