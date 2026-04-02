function switchTab(name, btn) {
  document.querySelectorAll('.tab-pane-content').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-pill').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  btn.classList.add('active');
}

document.querySelectorAll('.js-cart-form').forEach(form => {
  form.addEventListener('submit', function() {
    const btn = this.querySelector('.add-cart-btn');
    btn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Added!';
    btn.style.background = 'var(--accent)';
    setTimeout(() => {
      btn.innerHTML = '<i class="bi bi-bag-plus"></i> Add to Cart';
      btn.style.background = '';
    }, 2000);
  });
});

const starRating = document.getElementById('starRating');
const ratingInput = document.getElementById('review-rating-input');
const submitBtn = document.getElementById('submitReview');

if (starRating) {
  const stars = starRating.querySelectorAll('.star-btn');
  
  const initialRating = parseInt(ratingInput.value) || 0;
  updateStars(initialRating);
  
  stars.forEach((star, index) => {
    star.addEventListener('click', () => {
      const value = index + 1;
      ratingInput.value = value;
      updateStars(value);
      submitBtn.disabled = false;
    });
    
    star.addEventListener('mouseenter', () => {
      stars.forEach((s, i) => {
        s.querySelector('i').className = i <= index ? 'bi bi-star-fill' : 'bi bi-star';
      });
    });
  });
  
  starRating.addEventListener('mouseleave', () => {
    updateStars(parseInt(ratingInput.value) || 0);
  });
  
  function updateStars(rating) {
    stars.forEach((star, i) => {
      star.querySelector('i').className = i < rating ? 'bi bi-star-fill' : 'bi bi-star';
    });
  }
  
  if (ratingInput.value > 0) {
    submitBtn.disabled = false;
  }
}
