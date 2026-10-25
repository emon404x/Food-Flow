from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Claim
from .forms import ClaimForm, PickupVerificationForm
from .services import ClaimService
from listings.models import FoodListing


@login_required
@require_POST
def claim_create_view(request, listing_id):
    """
    Handles claiming an available food listing by a verified recipient.
    Delegates validation and atomic race condition prevention to ClaimService.
    """
    listing = FoodListing.objects.filter(pk=listing_id).first()
    if not listing:
        messages.error(request, "The requested food listing does not exist.")
        return redirect('listings:browse_food')

    if not request.user.is_recipient:
        messages.error(request, "Only registered recipients can claim food donations.")
        return redirect('listings:food_detail', pk=listing.pk)

    recipient = getattr(request.user, 'recipient_profile', None)
    if not recipient or not recipient.is_verified:
        messages.error(request, "Your recipient account is not verified yet. Verification by an administrator is required before you can claim food.")
        return redirect('listings:food_detail', pk=listing.pk)

    try:
        qty_str = request.POST.get('claimed_quantity', '').strip()
        quantity = Decimal(qty_str)
        if not quantity.is_finite() or quantity <= Decimal('0.00'):
            raise ValueError()
    except Exception:
        messages.error(request, "Please enter a valid positive numeric quantity.")
        return redirect('listings:food_detail', pk=listing_id)

    try:
        claim = ClaimService.create_claim(listing_id=listing_id, recipient=recipient, quantity=quantity)
        messages.success(
            request,
            f"Successfully reserved {claim.claimed_quantity} {claim.listing.unit} of '{claim.listing.food_name}'! "
            f"Your Pickup Code is: {claim.pickup_code}"
        )
        return redirect('claims:claim_detail', pk=claim.pk)
    except ValidationError as e:
        err_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
        messages.error(request, f"Claim failed: {err_msg}")
        return redirect('listings:food_detail', pk=listing_id)
    except Exception as e:
        messages.error(request, f"An unexpected error occurred while processing your claim: {e}")
        return redirect('listings:food_detail', pk=listing_id)


@login_required
def claims_list_view(request):
    """
    Displays claims for authenticated users:
    - Recipients: past and active claims made by them, with their 8-character pickup code.
    - Donors: incoming claims placed by recipients on their donated food listings.
    - Admins / Staff: all claims across the platform.
    """
    status_filter = request.GET.get('status', '').strip().lower()

    # Lazily update pending claims whose pickup deadline has passed
    now = timezone.now()
    Claim.objects.filter(
        status=Claim.STATUS_PENDING,
        pickup_deadline__lte=now
    ).update(status=Claim.STATUS_EXPIRED)

    if request.user.is_recipient:
        recipient = getattr(request.user, 'recipient_profile', None)
        if recipient:
            claims = Claim.objects.filter(recipient=recipient)
        else:
            claims = Claim.objects.none()
        page_title = "My Food Claims"
        page_subtitle = "Track your active reservations, pickup codes, and claim history."
    elif request.user.is_donor:
        donor = getattr(request.user, 'donor_profile', None)
        if donor:
            claims = Claim.objects.filter(listing__donor=donor)
        else:
            claims = Claim.objects.none()
        page_title = "Incoming Food Claims"
        page_subtitle = "Track food claims and reservations placed on your donated food items."
    elif request.user.is_staff:
        claims = Claim.objects.all()
        page_title = "Platform Food Claims"
        page_subtitle = "All food reservations and pickup activities across the FoodFlow platform."
    else:
        claims = Claim.objects.none()
        page_title = "Food Claims"
        page_subtitle = "Track food claims and reservations."

    claims = claims.select_related(
        'listing', 'listing__donor__user', 'listing__location', 'recipient__user'
    ).order_by('-claimed_at')

    valid_statuses = [Claim.STATUS_PENDING, Claim.STATUS_COMPLETED, Claim.STATUS_CANCELLED, Claim.STATUS_EXPIRED]
    if status_filter and status_filter in valid_statuses:
        claims = claims.filter(status=status_filter)

    context = {
        'claims': claims,
        'status_filter': status_filter,
        'page_title': page_title,
        'page_subtitle': page_subtitle,
    }
    return render(request, 'claims/my_claims.html', context)


# Maintain backward compatibility for any existing view imports
recipient_claims_list_view = claims_list_view


@login_required
def claim_detail_view(request, pk):
    """
    Displays the details of a single claim, prominently showing the 8-character pickup code.
    Accessible ONLY to the recipient who made the claim or the donor who owns the food listing.
    """
    claim = get_object_or_404(
        Claim.objects.select_related('listing__donor__user', 'listing__location', 'recipient__user'),
        pk=pk
    )

    is_claimant = (claim.recipient.user == request.user)
    is_donor_owner = (claim.listing.donor.user == request.user)

    if not (is_claimant or is_donor_owner or request.user.is_staff):
        messages.error(request, "Unauthorized: You do not have permission to view this claim.")
        return redirect('home')

    context = {
        'claim': claim,
        'is_claimant': is_claimant,
        'is_donor_owner': is_donor_owner,
    }
    return render(request, 'claims/claim_detail.html', context)


@login_required
@require_POST
def claim_cancel_view(request, pk):
    """
    Allows a recipient to cancel their own pending claim.
    """
    try:
        claim = ClaimService.cancel_claim(claim_id=pk, user=request.user)
        messages.success(request, f"Claim #{claim.id} for '{claim.listing.food_name}' was successfully cancelled.")
    except ValidationError as e:
        err_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
        messages.error(request, f"Cancellation error: {err_msg}")
    except Exception as e:
        messages.error(request, f"Error cancelling claim: {e}")

    return redirect('claims:my_claims')


@login_required
def donor_verify_pickup_view(request):
    """
    Donor page to enter and verify the 8-character pickup code presented by the recipient.
    """
    if not request.user.is_donor or not hasattr(request.user, 'donor_profile'):
        messages.error(request, "Access restricted to food donors.")
        return redirect('accounts:recipient_dashboard' if request.user.is_recipient else 'home')

    donor = request.user.donor_profile
    verified_claim = None

    if request.method == 'POST':
        form = PickupVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['pickup_code']
            try:
                verified_claim = ClaimService.verify_and_complete_pickup(
                    pickup_code=code,
                    donor_user=request.user
                )
                messages.success(
                    request,
                    f"Pickup Verified! Handover of {verified_claim.claimed_quantity} {verified_claim.listing.unit} "
                    f"of '{verified_claim.listing.food_name}' to recipient '{verified_claim.recipient.user.full_name}' is complete."
                )
                form = PickupVerificationForm()
            except ValidationError as e:
                err_msg = ', '.join(e.messages) if hasattr(e, 'messages') else str(e)
                messages.error(request, f"Verification Failed: {err_msg}")
    else:
        form = PickupVerificationForm()

    # Recent completed pickups for reference
    recent_pickups = Claim.objects.filter(
        listing__donor=donor,
        status=Claim.STATUS_COMPLETED
    ).select_related('listing', 'recipient__user').order_by('-claimed_at')[:10]

    context = {
        'form': form,
        'verified_claim': verified_claim,
        'recent_pickups': recent_pickups,
    }
    return render(request, 'claims/verify_pickup.html', context)
