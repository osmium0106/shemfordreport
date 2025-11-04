$(document).ready(function() {
    // Handle class selection change
    $('#classSelect').change(function() {
        const selectedClass = $(this).val();
        const rollSelect = $('#rollSelect');
        const submitBtn = $('#submitBtn');
        const loadingIndicator = $('#loadingIndicator');
        
        if (selectedClass) {
            // Show loading indicator
            loadingIndicator.show();
            rollSelect.prop('disabled', true);
            submitBtn.prop('disabled', true);
            
            // Clear previous options
            rollSelect.html('<option value="">Loading students...</option>');
            
            // Fetch students for selected class
            $.ajax({
                url: `/api/students/${encodeURIComponent(selectedClass)}`,
                method: 'GET',
                success: function(response) {
                    // Clear loading option
                    rollSelect.empty();
                    rollSelect.append('<option value="">Select roll number...</option>');
                    
                    // Check if response is successful and has students
                    if (response.success && response.students && response.students.length > 0) {
                        // Populate with students
                        response.students.forEach(function(student) {
                            const rollNumber = student['Roll Number'];
                            const name = student['Name'];
                            const optionText = `${rollNumber} - ${name}`;
                            rollSelect.append(`<option value="${rollNumber}">${optionText}</option>`);
                        });
                        
                        // Enable roll number selection
                        rollSelect.prop('disabled', false);
                    } else {
                        rollSelect.append('<option value="">No students found</option>');
                    }
                    
                    loadingIndicator.hide();
                },
                error: function(xhr, status, error) {
                    console.error('Error fetching students:', error);
                    rollSelect.html('<option value="">Error loading students</option>');
                    loadingIndicator.hide();
                    alert('Error loading students. Please try again.');
                }
            });
        } else {
            // Reset roll number dropdown
            rollSelect.html('<option value="">First select a class...</option>');
            rollSelect.prop('disabled', true);
            submitBtn.prop('disabled', true);
        }
    });
    
    // Handle roll number selection change
    $('#rollSelect').change(function() {
        const selectedRoll = $(this).val();
        const submitBtn = $('#submitBtn');
        
        if (selectedRoll) {
            submitBtn.prop('disabled', false);
        } else {
            submitBtn.prop('disabled', true);
        }
    });
    
    // Handle form submission
    $('#studentForm').submit(function(e) {
        e.preventDefault();
        
        const selectedClass = $('#classSelect').val();
        const selectedRoll = $('#rollSelect').val();
        
        if (selectedClass && selectedRoll) {
            // Show loading state
            const submitBtn = $('#submitBtn');
            const originalText = submitBtn.html();
            submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Generating Report...');
            submitBtn.prop('disabled', true);
            
            // Redirect to report page
            window.location.href = `/report/${encodeURIComponent(selectedClass)}/${encodeURIComponent(selectedRoll)}`;
        } else {
            alert('Please select both class and roll number.');
        }
    });
    
    // Add smooth animations
    $('.card').addClass('fade-in');
    
    // Handle responsive table scrolling
    $(window).resize(function() {
        adjustTableResponsiveness();
    });
    
    function adjustTableResponsiveness() {
        if ($(window).width() < 768) {
            $('.table-responsive').addClass('small-screen');
        } else {
            $('.table-responsive').removeClass('small-screen');
        }
    }
    
    // Initial call
    adjustTableResponsiveness();
});

// Utility function to show success message
function showSuccessMessage(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    $('.container').prepend(alertHtml);
    
    // Auto dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

// Utility function to show error message
function showErrorMessage(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    $('.container').prepend(alertHtml);
    
    // Auto dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').alert('close');
    }, 5000);
}

// Function to validate form before submission
function validateForm() {
    const classValue = $('#classSelect').val();
    const rollValue = $('#rollSelect').val();
    
    if (!classValue) {
        showErrorMessage('Please select a class.');
        return false;
    }
    
    if (!rollValue) {
        showErrorMessage('Please select a roll number.');
        return false;
    }
    
    return true;
}

// Add keyboard shortcuts
$(document).keydown(function(e) {
    // Ctrl + R for generate report (if form is valid)
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        if (validateForm()) {
            $('#studentForm').submit();
        }
    }
    
    // Escape to clear form
    if (e.key === 'Escape') {
        $('#classSelect').val('').trigger('change');
    }
});

// Add tooltips for better UX
$(function () {
    $('[data-bs-toggle="tooltip"]').tooltip();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}