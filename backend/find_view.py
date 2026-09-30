import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import core.views
print("Catalog is in:", core.views.Catalog.__module__)
print("Me is in:", core.views.Me.__module__)
