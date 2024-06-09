document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.faq details').forEach((item) => {
        item.addEventListener('toggle', (event) => {
            if (event.target.open) {
                document.querySelectorAll('.faq details').forEach((otherItem) => {
                    if (otherItem !== event.target) {
                        otherItem.removeAttribute('open');
                    }
                });
            }
        });
    });
});

