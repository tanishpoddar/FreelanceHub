// Portfolio Editor JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop functionality
    initializeSortable();
    
    // Initialize form handling
    initializeForms();
    
    // Initialize modals
    initializeModals();
});

// CSRF Token handling
function getCSRFToken() {
    const tokenInput = document.querySelector('input[name="csrf_token"]');
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    
    console.log('Token input found:', !!tokenInput);
    console.log('Meta token found:', !!metaToken);
    
    if (tokenInput) {
        console.log('Using input token');
        return tokenInput.value;
    } else if (metaToken) {
        console.log('Using meta token');
        return metaToken.getAttribute('content');
    } else {
        console.error('No CSRF token found!');
        return '';
    }
}

// Initialize Sortable.js for drag and drop
function initializeSortable() {
    // Projects sorting
    const projectsContainer = document.getElementById('projects-container');
    if (projectsContainer) {
        new Sortable(projectsContainer, {
            animation: 150,
            handle: '.drag-handle',
            onEnd: function(evt) {
                updateOrder('projects', evt.oldIndex, evt.newIndex);
            }
        });
    }
    
    // Skills sorting
    const skillsContainer = document.getElementById('skills-container');
    if (skillsContainer) {
        new Sortable(skillsContainer, {
            animation: 150,
            handle: '.drag-handle',
            onEnd: function(evt) {
                updateOrder('skills', evt.oldIndex, evt.newIndex);
            }
        });
    }
    
    // Testimonials sorting
    const testimonialsContainer = document.getElementById('testimonials-container');
    if (testimonialsContainer) {
        new Sortable(testimonialsContainer, {
            animation: 150,
            handle: '.drag-handle',
            onEnd: function(evt) {
                updateOrder('testimonials', evt.oldIndex, evt.newIndex);
            }
        });
    }
}

// Update order after drag and drop
function updateOrder(type, oldIndex, newIndex) {
    const items = document.querySelectorAll(`.${type.slice(0, -1)}-item`);
    const itemIds = Array.from(items).map(item => item.dataset.id);
    
    fetch(`/portfolio/update-order`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            type: type,
            item_ids: itemIds
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Order updated successfully', 'success');
        } else {
            showNotification('Failed to update order', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating order:', error);
        showNotification('Error updating order', 'error');
    });
}

// Initialize form handling
function initializeForms() {
    // Project form
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', handleProjectSubmit);
    }
    
    // Skill form
    const skillForm = document.getElementById('skillForm');
    if (skillForm) {
        skillForm.addEventListener('submit', handleSkillSubmit);
    }
    
    // Testimonial form
    const testimonialForm = document.getElementById('testimonialForm');
    if (testimonialForm) {
        testimonialForm.addEventListener('submit', handleTestimonialSubmit);
    }
}

// Handle project form submission
function handleProjectSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';
    
    fetch(event.target.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Project added successfully', 'success');
            closeProjectModal();
            location.reload(); // Reload to show new project
        } else {
            showNotification(data.message || 'Failed to add project', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding project:', error);
        showNotification('Error adding project', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

// Handle skill form submission
function handleSkillSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';
    
    fetch(event.target.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Skill added successfully', 'success');
            closeSkillModal();
            location.reload(); // Reload to show new skill
        } else {
            showNotification(data.message || 'Failed to add skill', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding skill:', error);
        showNotification('Error adding skill', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

// Handle testimonial form submission
function handleTestimonialSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const submitButton = event.target.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';
    
    fetch(event.target.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Testimonial added successfully', 'success');
            closeTestimonialModal();
            location.reload(); // Reload to show new testimonial
        } else {
            showNotification(data.message || 'Failed to add testimonial', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding testimonial:', error);
        showNotification('Error adding testimonial', 'error');
    })
    .finally(() => {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
    });
}

// Initialize modals
function initializeModals() {
    // Close modals when clicking outside
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('fixed')) {
            closeAllModals();
        }
    });
    
    // Close modals with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
}

// Modal functions
function openProjectModal() {
    document.getElementById('projectModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeProjectModal() {
    document.getElementById('projectModal').classList.add('hidden');
    document.getElementById('projectForm').reset();
    document.body.style.overflow = 'auto';
}

function openSkillModal() {
    document.getElementById('skillModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeSkillModal() {
    document.getElementById('skillModal').classList.add('hidden');
    document.getElementById('skillForm').reset();
    document.body.style.overflow = 'auto';
}

function openTestimonialModal() {
    document.getElementById('testimonialModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeTestimonialModal() {
    document.getElementById('testimonialModal').classList.add('hidden');
    document.getElementById('testimonialForm').reset();
    document.body.style.overflow = 'auto';
}

function closeAllModals() {
    closeProjectModal();
    closeSkillModal();
    closeTestimonialModal();
}

// Edit functions
function editProject(projectId) {
    // Redirect to edit project page or open edit modal
    window.location.href = `/portfolio/edit-project/${projectId}`;
}

function editSkill(skillId) {
    // Redirect to edit skill page or open edit modal
    window.location.href = `/portfolio/edit-skill/${skillId}`;
}

function editTestimonial(testimonialId) {
    // Redirect to edit testimonial page or open edit modal
    window.location.href = `/portfolio/edit-testimonial/${testimonialId}`;
}

// Delete functions
function deleteProject(projectId) {
    if (confirm('Are you sure you want to delete this project?')) {
        fetch(`/portfolio/delete-project/${projectId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Project deleted successfully', 'success');
                location.reload();
            } else {
                showNotification(data.message || 'Failed to delete project', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting project:', error);
            showNotification('Error deleting project', 'error');
        });
    }
}

function deleteSkill(skillId) {
    if (confirm('Are you sure you want to delete this skill?')) {
        fetch(`/portfolio/delete-skill/${skillId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Skill deleted successfully', 'success');
                location.reload();
            } else {
                showNotification(data.message || 'Failed to delete skill', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting skill:', error);
            showNotification('Error deleting skill', 'error');
        });
    }
}

function deleteTestimonial(testimonialId) {
    if (confirm('Are you sure you want to delete this testimonial?')) {
        fetch(`/portfolio/delete-testimonial/${testimonialId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Testimonial deleted successfully', 'success');
                location.reload();
            } else {
                showNotification(data.message || 'Failed to delete testimonial', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting testimonial:', error);
            showNotification('Error deleting testimonial', 'error');
        });
    }
}

// Publish portfolio
function publishPortfolio() {
    console.log('Publish portfolio function called');
    console.log('CSRF Token:', getCSRFToken());
    
    if (confirm('Are you sure you want to publish your portfolio? This will make it visible to the public.')) {
        console.log('User confirmed, sending request...');
        
        fetch('/portfolio/publish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                showNotification('Portfolio published successfully!', 'success');
                // Delay reload to show notification longer
                setTimeout(() => {
                    location.reload();
                }, 2000); // Wait 2 seconds before reloading
            } else {
                showNotification(data.message || 'Failed to publish portfolio', 'error');
            }
        })
        .catch(error => {
            console.error('Error publishing portfolio:', error);
            showNotification('Error publishing portfolio', 'error');
        });
    } else {
        console.log('User cancelled publish');
    }
}

// Unpublish portfolio
function unpublishPortfolio() {
    console.log('Unpublish portfolio function called');
    
    if (confirm('Are you sure you want to unpublish your portfolio? This will make it private and not visible to the public.')) {
        console.log('User confirmed, sending request...');
        
        fetch('/portfolio/unpublish', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            if (data.success) {
                showNotification('Portfolio unpublished successfully!', 'success');
                // Delay reload to show notification longer
                setTimeout(() => {
                    location.reload();
                }, 2000); // Wait 2 seconds before reloading
            } else {
                showNotification(data.message || 'Failed to unpublish portfolio', 'error');
            }
        })
        .catch(error => {
            console.error('Error unpublishing portfolio:', error);
            showNotification('Error unpublishing portfolio', 'error');
        });
    } else {
        console.log('User cancelled unpublish');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification fixed top-4 right-4 z-50 p-4 rounded-md shadow-lg max-w-sm transform transition-all duration-300 translate-x-full`;
    
    // Set notification content based on type
    let bgColor, textColor, icon;
    switch (type) {
        case 'success':
            bgColor = 'bg-green-500';
            textColor = 'text-white';
            icon = '✓';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            icon = '✕';
            break;
        case 'warning':
            bgColor = 'bg-yellow-500';
            textColor = 'text-white';
            icon = '⚠';
            break;
        default:
            bgColor = 'bg-blue-500';
            textColor = 'text-white';
            icon = 'ℹ';
    }
    
    notification.className += ` ${bgColor} ${textColor}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="mr-2">${icon}</span>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-auto text-white hover:text-gray-200">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 8 seconds (longer for important actions)
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('translate-x-full');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 8000);
}

// Form validation helpers
function validateRequiredFields(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// File upload helpers
function validateFileSize(file, maxSizeMB = 2) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
        showNotification(`File size must be less than ${maxSizeMB}MB`, 'error');
        return false;
    }
    return true;
}

function validateImageFile(file) {
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please select a valid image file (JPEG, PNG, GIF, or WebP)', 'error');
        return false;
    }
    return true;
}

// Add file validation to file inputs
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                if (!validateImageFile(file)) {
                    this.value = '';
                    return;
                }
                if (!validateFileSize(file)) {
                    this.value = '';
                    return;
                }
            }
        });
    });
});

// Export functions for global access
window.openProjectModal = openProjectModal;
window.closeProjectModal = closeProjectModal;
window.openSkillModal = openSkillModal;
window.closeSkillModal = closeSkillModal;
window.openTestimonialModal = openTestimonialModal;
window.closeTestimonialModal = closeTestimonialModal;
window.editProject = editProject;
window.editSkill = editSkill;
window.editTestimonial = editTestimonial;
window.deleteProject = deleteProject;
window.deleteSkill = deleteSkill;
window.deleteTestimonial = deleteTestimonial;
window.publishPortfolio = publishPortfolio;
window.unpublishPortfolio = unpublishPortfolio; 