import logging
from typing import List
from django.db.models import QuerySet

logger = logging.getLogger(__name__)


class LocationMatchingService:
    """
    Service responsible for matching available food listings to nearby verified recipients.
    First looks in the exact area; if fewer than 5 matches, falls back to the entire city.
    """

    @classmethod
    def find_matching_recipients(cls, location) -> QuerySet:
        """
        Find verified recipients matching the given location (area/city).
        Returns a Django QuerySet of Recipient objects.
        """
        from accounts.models import Recipient

        if not location or not (location.city or '').strip():
            return Recipient.objects.none()

        clean_city = location.city.strip()
        clean_area = (location.area or '').strip()

        # Step 1: If area is specified, query verified recipients in the exact area and city
        if clean_area:
            area_recipients = Recipient.objects.filter(
                is_verified=True,
                location__area__iexact=clean_area,
                location__city__iexact=clean_city
            ).select_related('user', 'location')

            count = area_recipients.count()
            if count >= 5:
                return area_recipients

        # Step 2: Fall back to entire city
        return Recipient.objects.filter(
            is_verified=True,
            location__city__iexact=clean_city
        ).select_related('user', 'location')

