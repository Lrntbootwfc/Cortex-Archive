from django.test import TestCase
from django.contrib.auth.models import User
from journal_entries.models import Folder, JournalEntry

class FastBackendTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="fastuser", password="123")
    
    def test_folder_and_journal_operations(self):
        root = Folder.objects.create(user=self.user, name="Root")
        sub = Folder.objects.create(user=self.user, name="Sub", parent=root)
        j = JournalEntry.objects.create(user=self.user, title="Test Journal", folder=root)

        # rename
        root.name = "Root Renamed"
        root.save()
        self.assertEqual(Folder.objects.get(id=root.id).name, "Root Renamed")

        # move journal
        j.folder = sub
        j.save()
        self.assertEqual(JournalEntry.objects.get(id=j.id).folder.id, sub.id)
