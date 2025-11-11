/**
 * Sistema de Agendamentos - CMFAM/UEPB
 * Main JavaScript file for interactivity
 */

// Document ready handler
$(document).ready(function() {
    console.log('Sistema de Agendamentos initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize auto-dismiss for alerts
    initializeAlertAutoDismiss();
    
    // Initialize table sorting (if needed)
    initializeTableEnhancements();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    // Add 'was-validated' class to forms on submit
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Reservation form specific validations
    const reservaForm = document.getElementById('reservaForm');
    if (reservaForm) {
        reservaForm.addEventListener('submit', function(e) {
            const dataInicio = new Date(document.getElementById('data_inicio').value);
            const dataFim = new Date(document.getElementById('data_fim').value);
            
            if (dataFim <= dataInicio) {
                e.preventDefault();
                alert('A data de término deve ser posterior à data de início!');
                return false;
            }
        });
    }
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initializeAlertAutoDismiss() {
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(function(alert) {
        if (alert.classList.contains('alert-success')) {
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

/**
 * Initialize table enhancements
 */
function initializeTableEnhancements() {
    // Add search functionality to tables
    const tables = document.querySelectorAll('.table');
    tables.forEach(function(table) {
        // Add hover effect enhancement
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
            });
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });
}

/**
 * Format date to Brazilian format
 */
function formatDateBR(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

/**
 * Format time to HH:MM
 */
function formatTime(dateString) {
    const date = new Date(dateString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * Confirm action with user
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Show loading spinner
 */
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center my-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2">Carregando...</p>
            </div>
        `;
    }
}

/**
 * Hide loading spinner
 */
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

/**
 * Display error message
 */
function showError(message, elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="bi bi-exclamation-triangle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

/**
 * Display success message
 */
function showSuccess(message, elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-success alert-dismissible fade show" role="alert">
                <i class="bi bi-check-circle"></i> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

/**
 * Check for time conflicts (client-side validation)
 */
function checkTimeConflict(equipamentoId, dataInicio, dataFim, callback) {
    fetch(`/api/reservas/${equipamentoId}`)
        .then(response => response.json())
        .then(data => {
            const start = new Date(dataInicio);
            const end = new Date(dataFim);
            
            const hasConflict = data.some(reserva => {
                if (reserva.status === 'cancelada') return false;
                
                const resStart = new Date(reserva.start);
                const resEnd = new Date(reserva.end);
                
                return (
                    (start >= resStart && start < resEnd) ||
                    (end > resStart && end <= resEnd) ||
                    (start <= resStart && end >= resEnd)
                );
            });
            
            callback(hasConflict);
        })
        .catch(error => {
            console.error('Error checking conflicts:', error);
            callback(false);
        });
}

/**
 * Update navigation active state
 */
function updateNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(function(link) {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Call updateNavigation on page load
updateNavigation();

/**
 * Smooth scroll to top
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Add scroll to top button if page is long
window.addEventListener('scroll', function() {
    if (document.body.scrollHeight > window.innerHeight * 2) {
        // Could add a floating "back to top" button here
    }
});

/**
 * Export table data to CSV (utility function)
 */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(function(col) {
            csvRow.push(col.innerText);
        });
        csv.push(csvRow.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
});

// Log when scripts are loaded
console.log('Main JavaScript loaded successfully');
