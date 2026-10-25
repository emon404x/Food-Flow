/**
 * FoodFlow - Claims Handling Script
 * Provides user feedback, confirmation dialogs, and double-submit prevention.
 * Uses manual typing without steppers or wheel changes.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Disable mousewheel value changes on all inputs
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('wheel', (e) => {
            if (document.activeElement === input) {
                input.blur();
            }
        });
    });

    const claimForm = document.getElementById('claim-food-form');
    if (claimForm) {
        claimForm.addEventListener('submit', (e) => {
            const qtyInput = document.getElementById('id_claimed_quantity');
            const qtyVal = qtyInput ? qtyInput.value.trim() : '';
            const qty = parseFloat(qtyVal);

            if (!qtyVal || !Number.isFinite(qty) || qty < 0.10) {
                e.preventDefault();
                alert('Minimum claim quantity is 0.10.');
                return;
            }


            // Disable submit button to prevent accidental double clicks
            const submitBtn = claimForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Reserving...';
            }
        });
    }

    // Confirmation for cancelling a claim
    const cancelForms = document.querySelectorAll('.cancel-claim-form');
    cancelForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmed = confirm('Are you sure you want to cancel this claim? This will return the quantity to the donation pool.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
});
