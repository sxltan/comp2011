/**
 * Handles the star rating feature for display-only cards.
 */
function initializeStarDisplay() {
    const starContainers = document.querySelectorAll('.star-rating');

    starContainers.forEach(starsContainer => {
        const rating = parseFloat(starsContainer.dataset.rating || 0);
        starsContainer.innerHTML = '';

        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('i');
            star.className = `fa fa-star ${i <= rating ? 'checked' : ''}`;
            starsContainer.appendChild(star);
        }
    });
}

/**
 * Initializes event listeners and dynamic features. */
document.addEventListener("DOMContentLoaded", function () {

    // Event Listener for sorting movies
    document.getElementById("sortCriteria").addEventListener("change", sortMovies);

    // Initialize star display
    initializeStarDisplay();
});

/**
 * Handles the like button click event without redirecting.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Attach event listener to each like form
    document.querySelectorAll('.like-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); 

            const movieId = form.dataset.movieId;
            const button = form.querySelector('button');
            const likeCountSpan = button.querySelector('.like-count');
            
            // Send an AJAX POST request to toggle the like status
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
            })
            .then(response => response.json())
            .then(data => {
                // Update the button class based on whether the movie is liked or not
                if (data.liked) {
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-danger');
                } else {
                    button.classList.remove('btn-danger');
                    button.classList.add('btn-outline-danger');
                }

                // Update the like count display
                likeCountSpan.textContent = data.like_count;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while liking the movie.');
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.remove();
        }, 3500);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // Event listener for showing the review and reflection modal
    document.querySelectorAll('.view-review-reflection').forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); 

            const movieId = link.dataset.movieId; 
            const modal = document.getElementById(`reviewModal-${movieId}`); 

            if (modal) {
                const bootstrapModal = new bootstrap.Modal(modal);
                bootstrapModal.show();
            }
        });
    });
});
