document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.food-photo-gallery').forEach(function (gallery) {
        const mainPhoto = gallery.querySelector('img.food-detail-photo');
        const buttons = gallery.querySelectorAll('.food-photo-thumbnail');

        if (!mainPhoto) {
            return;
        }

        buttons.forEach(function (button) {
            button.addEventListener('click', function () {
                const thumbnail = button.querySelector('img');

                mainPhoto.src = thumbnail.src;
                mainPhoto.alt = thumbnail.alt;

                buttons.forEach(function (item) {
                    item.classList.remove('is-selected');
                    item.setAttribute('aria-pressed', 'false');
                });

                button.classList.add('is-selected');
                button.setAttribute('aria-pressed', 'true');
            });
        });
    });
});