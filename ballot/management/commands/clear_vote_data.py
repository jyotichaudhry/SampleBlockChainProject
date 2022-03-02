from django.core.management.base import BaseCommand
from django.db import connection, transaction

from ballot.models import Vote, VoteBackup, Block


class Command(BaseCommand):
    help = 'A description of your command'

    def handle(self, *args, **options):
        cursor = connection.cursor()

        Vote.objects.all().delete()
        VoteBackup.objects.all().delete()
        Block.objects.all().delete()

        cursor.execute("ALTER TABLE ballot_vote AUTO_INCREMENT = 1;")
        cursor.execute("ALTER TABLE ballot_votebackup AUTO_INCREMENT = 1;")
        cursor.execute("ALTER TABLE ballot_block AUTO_INCREMENT = 1;")

        row = cursor.fetchone()

        print("clear_vote.....!")
