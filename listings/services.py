"""
FoodFlow - Expiry Service
University CSE Lab Project

Handles simple expiry checking for food listings and pending claims.
"""
import logging
from django.utils import timezone
from listings.models import FoodListing
from claims.models import Claim

logger = logging.getLogger(__name__)


class ExpiryService:
    """
    Beginner-friendly service to check and mark expired listings and their pending claims.
    """

    @classmethod
    def check_and_update_listing_expiration(cls, listing):
        """
        If a listing has reached or passed its expires_at time, mark it as expired.
        Also marks any pending claims on this listing as expired.
        """
        now = timezone.now()
        if listing.expires_at <= now and listing.status in [FoodListing.STATUS_AVAILABLE, FoodListing.STATUS_CLAIMED]:
            listing.status = FoodListing.STATUS_EXPIRED
            listing.save(update_fields=['status', 'updated_at'])
            # Also expire pending claims that were never picked up
            listing.claims.filter(status=Claim.STATUS_PENDING).update(status=Claim.STATUS_EXPIRED)
            return True
        return False

    @classmethod
    def mark_all_expired(cls):
        """
        Batch sweep method used by management commands or periodic checks.
        """
        now = timezone.now()
        expired_listings = FoodListing.objects.filter(
            status__in=[FoodListing.STATUS_AVAILABLE, FoodListing.STATUS_CLAIMED],
            expires_at__lte=now
        )
        count = 0
        for listing in expired_listings:
            if cls.check_and_update_listing_expiration(listing):
                count += 1
        return count
