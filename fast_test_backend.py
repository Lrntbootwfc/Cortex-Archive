# fast_test_backend.py
from django.contrib.auth.models import User
from journal_entries.models import Folder, JournalEntry

# create a user
user, _ = User.objects.get_or_create(username="testuser", email="test@test.com")
user.set_password("password123")
user.save()

# create folder tree
root = Folder.objects.create(user=user, name="Root Folder")
sub1 = Folder.objects.create(user=user, name="Sub 1", parent=root)
sub2 = Folder.objects.create(user=user, name="Sub 2", parent=root)

# create journals
j1 = JournalEntry.objects.create(user=user, title="Journal 1", folder=root)
j2 = JournalEntry.objects.create(user=user, title="Journal 2", folder=sub1)

# simulate rename, move, lock, copy
root.name = "Root Renamed"
root.save()
j1.folder = sub2
j1.save()
sub1.is_locked = True
sub1.save()
