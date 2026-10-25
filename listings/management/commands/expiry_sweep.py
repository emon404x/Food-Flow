import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from listings.models import FoodListing
from claims.models import Claim
from notifications.services import NotificationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sweeps database for expired food listings and pending claims past their deadline."

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(self.style.NOTICE(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Starting FoodFlow Expiry Sweep..."))

        expired_listings_count = 0
        expired_claims_count = 0

        # 1. Sweep expired Food Listings
        expired_listings = FoodListing.objects.filter(
            expires_at__lte=now,
            status__in=[FoodListing.STATUS_AVAILABLE, FoodListing.STATUS_CLAIMED]
        )

        for listing in expired_listings:
            try:
                with transaction.atomic():
                    listing.status = FoodListing.STATUS_EXPIRED
                    listing.save(update_fields=['status', 'updated_at'])

                    # Notify recipients with pending claims
                    NotificationService.notify_listing_expired(listing)

                    # Mark pending claims on this listing as expired
                    listing.claims.filter(status=Claim.STATUS_PENDING).update(status=Claim.STATUS_EXPIRED)

                    expired_listings_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing expired listing #{listing.id}: {e}"))

        # 2. Sweep pending claims past their pickup deadline
        expired_claims = Claim.objects.filter(
            status=Claim.STATUS_PENDING,
            pickup_deadline__lte=now
        ).select_related('listing')

        for claim in expired_claims:
            try:
                with transaction.atomic():
                    claim.status = Claim.STATUS_EXPIRED
                    claim.save(update_fields=['status'])

                    # If listing was marked claimed but still unexpired, restore to available if quantity remains
                    listing = claim.listing
                    if listing.status == FoodListing.STATUS_CLAIMED and listing.expires_at > now:
                        from decimal import Decimal
                        if listing.quantity_available > Decimal('0.00'):
                            listing.status = FoodListing.STATUS_AVAILABLE
                            listing.save(update_fields=['status', 'updated_at'])

                    expired_claims_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error expiring claim #{claim.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"Expiry sweep completed successfully:\n"
            f"  - Listings marked expired: {expired_listings_count}\n"
            f"  - Pending claims timed out: {expired_claims_count}"
        ))
