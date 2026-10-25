from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from locations.models import Location
from claims.models import Claim
from claims.forms import ClaimForm
from notifications.services import NotificationService
from .models import FoodListing, FoodPhoto
from .forms import FoodListingForm, FoodPhotoForm
from .services import ExpiryService


# ==========================================
# DONOR VIEWS
# ==========================================

@login_required
def donor_listings_list_view(request):
    """
    Displays all listings created by the logged-in donor with status filtering.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted to food donors.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    donor = request.user.donor_profile
    status_filter = request.GET.get('status', '').strip().lower()

    # Lazily update status for listings whose expiry has passed
    now = timezone.now()
    FoodListing.objects.filter(
        donor=donor,
        expires_at__lte=now,
        status__in=[FoodListing.STATUS_AVAILABLE, FoodListing.STATUS_CLAIMED]
    ).update(status=FoodListing.STATUS_EXPIRED)
    
    listings = FoodListing.objects.filter(donor=donor).select_related(
        'location'
    ).prefetch_related('claims')

    valid_statuses = [
        FoodListing.STATUS_AVAILABLE,
        FoodListing.STATUS_CLAIMED,
        FoodListing.STATUS_COMPLETED,
        FoodListing.STATUS_EXPIRED,
    ]
    if status_filter and status_filter in valid_statuses:
        listings = listings.filter(status=status_filter)

    context = {
        'listings': listings,
        'status_filter': status_filter,
    }
    return render(request, 'listings/my_listings.html', context)


@login_required
def donor_listing_create_view(request):
    """
    Handles surplus food listing creation, location lookup, and recipient matching alerts.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted to food donors.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    donor = request.user.donor_profile

    if request.method == 'POST':
        form = FoodListingForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Location reuse / creation safely
                    location = Location.get_or_create_location(
                        address=form.cleaned_data['address'],
                        area=form.cleaned_data['area'],
                        city=form.cleaned_data['city']
                    )

                    # 2. Save Listing
                    listing = form.save(commit=False)
                    listing.donor = donor
                    listing.location = location
                    listing.status = FoodListing.STATUS_AVAILABLE
                    listing.save()

                    # Save the optional first photo
                    photo = form.cleaned_data.get('photo')

                    if photo:
                        FoodPhoto.objects.create(
                            listing=listing,
                            image=photo
                        )

                    # 3. Notify matching verified recipients in same area/city
                    NotificationService.notify_new_listing(listing)
                    messages.success(request, f"Food listing '{listing.food_name}' published successfully!")

                    return redirect('listings:donor_listing_detail', pk=listing.pk)

            except Exception as e:
                messages.error(request, f"Error saving food listing: {e}")
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        # Pre-fill with donor's default location
        initial_data = {}
        if donor.location:
            initial_data = {
                'address': donor.location.address,
                'area': donor.location.area,
                'city': donor.location.city,
            }
        form = FoodListingForm(initial=initial_data)

    return render(request, 'listings/listing_form.html', {'form': form, 'is_edit': False})


@login_required
def donor_listing_detail_view(request, pk):
    """
    Detailed view for Donors to inspect their listing and active claims.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted to food donors.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    listing = get_object_or_404(
        FoodListing.objects.select_related('donor__user', 'location'),
        pk=pk
    )

    # Verify donor ownership
    if listing.donor.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized: You do not own this listing.")
        return redirect('listings:donor_listings')

    claims = listing.claims.all().select_related('recipient__user').order_by('-claimed_at')

    context = {
        'listing': listing,
        'claims': claims,
    }
    return render(request, 'listings/listing_detail_donor.html', context)


@login_required
def donor_listing_edit_view(request, pk):
    """
    Allows donors to edit their own active food listings.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted to food donors.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    listing = get_object_or_404(FoodListing, pk=pk)

    # Check donor ownership
    if listing.donor.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized: You cannot edit someone else's listing.")
        return redirect('listings:donor_listings')

    if listing.status in [FoodListing.STATUS_COMPLETED, FoodListing.STATUS_EXPIRED]:
        messages.error(request, f"Cannot edit a listing that is {listing.get_status_display().lower()}.")
        return redirect('listings:donor_listing_detail', pk=listing.pk)

    if request.method == 'POST':
        form = FoodListingForm(request.POST, instance=listing)
        if form.is_valid():
            with transaction.atomic():
                location = Location.get_or_create_location(
                    address=form.cleaned_data['address'],
                    area=form.cleaned_data['area'],
                    city=form.cleaned_data['city']
                )
                listing = form.save(commit=False)
                listing.location = location
                listing.save()

                messages.success(request, f"Food listing '{listing.food_name}' updated successfully.")
                return redirect('listings:donor_listing_detail', pk=listing.pk)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        initial_data = {
            'address': listing.location.address,
            'area': listing.location.area,
            'city': listing.location.city,
            'expires_at': timezone.localtime(listing.expires_at).strftime('%Y-%m-%dT%H:%M')
        }
        form = FoodListingForm(instance=listing, initial=initial_data)

    return render(request, 'listings/listing_form.html', {'form': form, 'is_edit': True, 'listing': listing})


@login_required
@require_POST
def donor_listing_delete_view(request, pk):
    """
    Allows donors to delete their own food listing if no active or completed claims exist.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    listing = get_object_or_404(FoodListing, pk=pk)

    if listing.donor.user != request.user and not request.user.is_staff:
        messages.error(request, "Unauthorized: You cannot delete this listing.")
        return redirect('listings:donor_listings')

    food_title = listing.food_name
    listing.delete()
    messages.success(request, f"Listing '{food_title}' has been deleted.")
    return redirect('listings:donor_listings')


# ==========================================
# RECIPIENT VIEWS
# ==========================================

def recipient_browse_view(request):
    """
    Recipient Food Browse page:
    Returns ONLY available, unexpired food donations.
    Supports search by keyword, area, and city.
    """
    listings = FoodListing.visible_to_recipients()

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        listings = listings.filter(
            Q(food_name__icontains=q) |
            Q(description__icontains=q) |
            Q(location__area__icontains=q) |
            Q(location__city__icontains=q)
        )

    # City filter
    city = request.GET.get('city', '').strip()
    if city:
        listings = listings.filter(location__city__iexact=city)

    # Area filter
    area = request.GET.get('area', '').strip()
    if area:
        listings = listings.filter(location__area__iexact=area)

    # Distinct locations for filter dropdowns
    available_cities = Location.objects.filter(listings__in=FoodListing.visible_to_recipients()).values_list('city', flat=True).distinct().order_by('city')
    available_areas = Location.objects.filter(listings__in=FoodListing.visible_to_recipients()).values_list('area', flat=True).distinct().order_by('area')

    context = {
        'listings': listings,
        'q': q,
        'selected_city': city,
        'selected_area': area,
        'available_cities': available_cities,
        'available_areas': available_areas,
    }
    return render(request, 'listings/browse.html', context)


def recipient_food_detail_view(request, pk):
    """
    Detailed food view for recipients showing remaining shelf life countdown,
    quantity available, and embedded ClaimForm for verified recipients.
    """
    listing = get_object_or_404(
        FoodListing.objects.select_related('donor__user', 'location'),
        pk=pk
    )

    available_qty = listing.quantity_available
    is_claimable = (
        listing.status == FoodListing.STATUS_AVAILABLE
        and not listing.is_expired
        and available_qty > Decimal('0.00')
    )

    is_recipient = request.user.is_authenticated and request.user.is_recipient
    is_verified_recipient = is_recipient and hasattr(request.user, 'recipient_profile') and request.user.recipient_profile.is_verified

    claim_form = None
    if is_recipient and is_claimable:
        claim_form = ClaimForm(max_available=available_qty, unit=listing.unit)

    context = {
        'listing': listing,
        'available_qty': available_qty,
        'is_claimable': is_claimable,
        'is_recipient': is_recipient,
        'is_verified_recipient': is_verified_recipient,
        'claim_form': claim_form,
    }
    return render(request, 'listings/food_detail_recipient.html', context)

# ==========================================
# DONOR FOOD PHOTO VIEWS
# ==========================================

@login_required
def donor_photo_list_view(request, listing_id):
    listing = get_object_or_404(
        FoodListing,
        pk=listing_id,
        donor__user=request.user,
    )

    return render(request, 'listings/photo_list.html', {
        'listing': listing,
        'photos': listing.photos.all(),
    })


@login_required
def donor_photo_add_view(request, listing_id):
    listing = get_object_or_404(
        FoodListing,
        pk=listing_id,
        donor__user=request.user,
    )

    if request.method == 'POST':
        form = FoodPhotoForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                # Lock this listing while checking its photo limit.
                listing = get_object_or_404(
                    FoodListing.objects.select_for_update(),
                    pk=listing_id,
                    donor__user=request.user,
                )

                if listing.photos.count() >= 5:
                    form.add_error(
                        None,
                        "You can add a maximum of 5 photos per listing.",
                    )
                else:
                    photo = form.save(commit=False)
                    photo.listing = listing
                    photo.save()

                    messages.success(
                        request,
                        "Photo added successfully.",
                    )

                    return redirect(
                        'listings:donor_photo_list',
                        listing_id=listing.pk,
                    )
    else:
        form = FoodPhotoForm()

    return render(request, 'listings/photo_form.html', {
        'listing': listing,
        'form': form,
        'is_edit': False,
    })


@login_required
def donor_photo_edit_view(request, photo_id):
    photo = get_object_or_404(
        FoodPhoto.objects.select_related('listing'),
        pk=photo_id,
        listing__donor__user=request.user,
    )

    if request.method == 'POST':
        form = FoodPhotoForm(
            request.POST,
            request.FILES,
            instance=photo,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Photo updated successfully.",
            )

            return redirect(
                'listings:donor_photo_list',
                listing_id=photo.listing_id,
            )
    else:
        form = FoodPhotoForm(instance=photo)

    return render(request, 'listings/photo_form.html', {
        'listing': photo.listing,
        'photo': photo,
        'form': form,
        'is_edit': True,
    })


@login_required
def donor_photo_delete_view(request, photo_id):
    photo = get_object_or_404(
        FoodPhoto.objects.select_related('listing'),
        pk=photo_id,
        listing__donor__user=request.user,
    )

    listing = photo.listing

    if request.method == 'POST':
        photo.delete()

        messages.success(
            request,
            "Photo deleted successfully.",
        )

        return redirect(
            'listings:donor_photo_list',
            listing_id=listing.pk,
        )

    return render(request, 'listings/photo_confirm_delete.html', {
        'listing': listing,
        'photo': photo,
    })