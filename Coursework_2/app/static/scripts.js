/**
 * Filters movies based on the search input value.
 */
function filterMovies() {
    const searchInput = document.getElementById("searchInput").value.toLowerCase();
    const movieCards = document.querySelectorAll(".card");

    movieCards.forEach(card => {
        const title = card.querySelector(".card-title").innerText.toLowerCase();

        let isVisible = true;

        // Only show cards that match the search input in the title
        if (searchInput && !title.includes(searchInput)) {
            isVisible = false;
        }

        card.style.display = isVisible ? "" : "none";
    });
}

/**
 * Sorts movies based on the selected criteria.
 */
function sortMovies() {
    const sortCriteria = document.getElementById("sortCriteria").value;
    const movieList = document.getElementById("movieList");
    const movieCards = Array.from(movieList.getElementsByClassName("card"));

    movieCards.sort((a, b) => {
        let aValue, bValue;

        switch (sortCriteria) {
            case "title":
                aValue = a.querySelector(".card-title").innerText.toLowerCase();
                bValue = b.querySelector(".card-title").innerText.toLowerCase();
                break;
            case "rating":
                aValue = parseFloat(a.querySelector(".card-rating").dataset.rating || 0);
                bValue = parseFloat(b.querySelector(".card-rating").dataset.rating || 0);
                break;
            case "watch_date":
                aValue = new Date(a.querySelector(".card-watch-date").innerText);
                bValue = new Date(b.querySelector(".card-watch-date").innerText);
                break;
            default:
                return 0;
        }

        if (aValue < bValue) return -1;
        if (aValue > bValue) return 1;
        return 0;
    });

    movieCards.forEach(card => movieList.appendChild(card));
}

/**
 * Handles the star rating feature for display-only cards.
 */
function initializeStarDisplay() {
    const starContainers = document.querySelectorAll('.star-rating');

    starContainers.forEach(starsContainer => {
        const rating = parseFloat(starsContainer.dataset.rating || 0);
        starsContainer.innerHTML = ''; // Clear any existing stars

        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('i');
            star.className = `fa fa-star ${i <= rating ? 'checked' : ''}`;
            starsContainer.appendChild(star);
        }
    });
}

/**
 * Initializes event listeners and dynamic features.
 */
document.addEventListener("DOMContentLoaded", function () {
    // Event Listener for filtering movies by search input
    document.getElementById("searchInput").addEventListener("input", filterMovies);

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
            event.preventDefault();  // Prevent the form from submitting normally

            const movieId = form.dataset.movieId;  // Get the movie ID
            const button = form.querySelector('button');  // Get the button
            const likeCountSpan = button.querySelector('.like-count');  // Get the like count display
            
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
            event.preventDefault(); // Prevent default link behavior

            const movieId = link.dataset.movieId; // Get the movie ID
            const modal = document.getElementById(`reviewModal-${movieId}`); // Get the modal element

            if (modal) {
                const bootstrapModal = new bootstrap.Modal(modal); // Initialize Bootstrap modal
                bootstrapModal.show(); // Show the modal
            }
        });
    });
});
