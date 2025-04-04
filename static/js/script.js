/**
 * WiseWheel Car Rental - Main JavaScript File
 * Contains all interactive functionality for the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // ======================
    // Password Visibility Toggle
    // ======================
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const passwordField = this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');
            
            // Toggle field type
            const type = passwordField.type === 'password' ? 'text' : 'password';
            passwordField.type = type;
            
            // Toggle icon
            icon.classList.toggle('fa-eye');
            icon.classList.toggle('fa-eye-slash');
            
            // Update aria-label for accessibility
            const state = type === 'password' ? 'Show' : 'Hide';
            this.setAttribute('aria-label', `${state} password`);
        });
    });

    // ======================
    // Car Search and Filter System
    // ======================
    const setupCarFilters = () => {
        const carsContainer = document.getElementById('carsContainer');
        if (!carsContainer) return;

        const filters = {
            search: document.getElementById('carSearch'),
            price: document.getElementById('priceFilter'),
            type: document.getElementById('typeFilter'),
            year: document.getElementById('yearFilter'),
            reset: document.getElementById('resetFilters')
        };

        const filterCars = () => {
            const searchTerm = filters.search.value.toLowerCase();
            const priceRange = filters.price.value;
            const typeValue = filters.type.value.toLowerCase();
            const yearRange = filters.year.value;

            document.querySelectorAll('#carsContainer .col-lg-4').forEach(card => {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const type = card.querySelector('.text-muted').textContent.toLowerCase();
                const price = parseFloat(card.querySelector('.text-primary').textContent.replace('$', ''));
                const yearText = card.querySelector('.text-muted').textContent;
                const year = parseInt(yearText.match(/\d{4}/)[0]);
                const description = card.querySelector('.card-text')?.textContent.toLowerCase() || '';

                // Apply all filters
                const matchesSearch = title.includes(searchTerm) || description.includes(searchTerm);
                const matchesPrice = !priceRange || checkPriceRange(price, priceRange);
                const matchesType = !typeValue || type.includes(typeValue);
                const matchesYear = !yearRange || checkYearRange(year, yearRange);

                card.style.display = matchesSearch && matchesPrice && matchesType && matchesYear 
                    ? 'block' 
                    : 'none';
            });
        };

        const checkPriceRange = (price, range) => {
            const [min, max] = range.split('-').map(Number);
            return max ? price >= min && price <= max : price >= min;
        };

        const checkYearRange = (year, range) => {
            const [min, max] = range.split('-').map(Number);
            return max ? year >= min && year <= max : year >= min;
        };

        // Event listeners
        Object.values(filters).forEach(filter => {
            if (filter) filter.addEventListener('input', filterCars);
        });

        if (filters.reset) {
            filters.reset.addEventListener('click', () => {
                filters.search.value = '';
                filters.price.value = '';
                filters.type.value = '';
                filters.year.value = '';
                filterCars();
            });
        }
    };

    // ======================
    // Date Picker and Price Calculation
    // ======================
    const setupDatePickers = () => {
        const startDateInput = document.getElementById('startDate');
        const endDateInput = document.getElementById('endDate');
        const totalPriceElement = document.getElementById('totalPrice');
        const rentalDaysElement = document.getElementById('rentalDays');

        if (!startDateInput || !endDateInput) return;

        // Initialize min dates
        const today = new Date().toISOString().split('T')[0];
        startDateInput.min = today;
        endDateInput.min = today;

        // Update end date min when start date changes
        startDateInput.addEventListener('change', function() {
            endDateInput.min = this.value;
            calculatePrice();
        });

        endDateInput.addEventListener('change', calculatePrice);

        function calculatePrice() {
            if (startDateInput.value && endDateInput.value && totalPriceElement) {
                const pricePerDay = parseFloat(totalPriceElement.dataset.pricePerDay || 0);
                const startDate = new Date(startDateInput.value);
                const endDate = new Date(endDateInput.value);
                
                // Calculate difference in days
                const timeDiff = endDate - startDate;
                const daysDiff = Math.ceil(timeDiff / (1000 * 60 * 60 * 24)) + 1;
                
                if (daysDiff > 0) {
                    const totalPrice = daysDiff * pricePerDay;
                    totalPriceElement.textContent = `$${totalPrice.toFixed(2)}`;
                    if (rentalDaysElement) {
                        rentalDaysElement.textContent = `${daysDiff} day${daysDiff !== 1 ? 's' : ''}`;
                    }
                }
            }
        }

        // Initialize if Flatpickr is available
        if (typeof flatpickr !== 'undefined') {
            flatpickr("#startDate", {
                minDate: "today",
                dateFormat: "Y-m-d",
                onChange: function(selectedDates, dateStr) {
                    flatpickr("#endDate", {
                        minDate: dateStr,
                        dateFormat: "Y-m-d"
                    });
                    calculatePrice();
                }
            });
            
            flatpickr("#endDate", {
                minDate: "today",
                dateFormat: "Y-m-d",
                onChange: calculatePrice
            });
        }
    };

    // ======================
    // Initialize all functionality
    // ======================
    setupCarFilters();
    setupDatePickers();

    // ======================
    // Toast Notifications
    // ======================
    const showToast = (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type}`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        toastContainer.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    };

    const createToastContainer = () => {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1100';
        document.body.appendChild(container);
        return container;
    };

    // Expose to global scope for use with Flask flash messages
    window.showToast = showToast;
});

// Initialize Bootstrap tooltips if available
if (typeof bootstrap !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });
}
