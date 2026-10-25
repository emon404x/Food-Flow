from django.db import models


class Location(models.Model):
    """
    Location model to represent physical locations for Donors, Recipients, and Food Listings.
    Reused via get_or_create to prevent redundant location entries.
    Postal code has been removed for simplicity.
    """
    address = models.CharField(max_length=255, help_text="Street address or building details")
    area = models.CharField(max_length=100, db_index=True, help_text="Neighborhood or area name")
    city = models.CharField(max_length=100, db_index=True, help_text="City name")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        indexes = [
            models.Index(fields=['area'], name='loc_area_idx'),
            models.Index(fields=['city'], name='loc_city_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['address', 'area', 'city'],
                name='unique_location_address'
            )
        ]

    def __str__(self):
        parts = [self.address, self.area, self.city]
        return ", ".join(filter(None, parts))

    @classmethod
    def get_or_create_location(cls, address, area, city):
        """
        Safely retrieves or creates a Location instance based on address, area, and city.
        Normalizes strings to avoid duplicate entries.
        """
        clean_addr = (address or '').strip()
        clean_area = (area or '').strip()
        clean_city = (city or '').strip()

        loc = cls.objects.filter(
            address__iexact=clean_addr,
            area__iexact=clean_area,
            city__iexact=clean_city
        ).first()

        if not loc:
            loc = cls.objects.create(
                address=clean_addr,
                area=clean_area,
                city=clean_city
            )
        return loc
