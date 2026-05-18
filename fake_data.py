
import os
from decimal import Decimal

import django
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rental_project.settings")
django.setup()

from bookings.models import Booking
from listings.models import Listing, ViewHistory
from chat.models import Chat
from reviews.models import Review
from search.models import SearchHistory
from users.models import User


faker = Faker("en_US")


DEFAULT_PASSWORD = 'qwerty123'
MONEY = Decimal('0.01')
COORDINATE = Decimal('0.01')