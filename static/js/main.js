// Four One RNC Validator - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initRNCValidator();
    initSmoothScrolling();
    initTooltips();
});

function initRNCValidator() {
    const form = document.getElementById('rnc-form');
    const input = document.getElementById('rnc-input');
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    
    if (!form || !input) return;
    
    // Format RNC input (only numbers, max 11 digits)
    input.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, ''); // Remove non-digits
        if (value.length > 11) {
            value = value.slice(0, 11);
        }
        e.target.value = value;
    });
    
    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const rnc = input.value.trim();
        
        if (!rnc) {
            showError('Por favor ingresa un RNC válido');
            return;
        }
        
        if (rnc.length !== 9 && rnc.length !== 11) {
            showError('El RNC debe tener 9 o 11 dígitos');
            return;
        }
        
        validateRNC(rnc);
    });
}

function validateRNC(rnc) {
    const results = document.getElementById('results');
    const loading = document.getElementById('loading');
    
    // Show loading
    if (results) results.style.display = 'none';
    if (loading) loading.style.display = 'block';
    
    // Make API call
    fetch(`/api/info/${rnc}`)
        .then(response => {
            return response.json().then(data => {
                return { status: response.status, data: data };
            });
        })
        .then(result => {
            hideLoading();
            
            if (result.status === 200 && result.data.exists) {
                showSuccess(result.data);
            } else {
                showNotFound(result.data);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('API Error:', error);
            showError('Error de conexión. Por favor intenta nuevamente.');
        });
}

function showSuccess(data) {
    const results = document.getElementById('results');
    const alert = document.getElementById('result-alert');
    const content = document.getElementById('result-content');
    
    if (!results || !alert || !content) return;
    
    alert.className = 'alert alert-success';
    
    let html = `
        <div class="d-flex align-items-center mb-3">
            <i class="fas fa-check-circle fa-2x text-success me-3"></i>
            <div>
                <h5 class="mb-1">RNC Válido</h5>
                <p class="mb-0">RNC <strong>${data.rnc}</strong> encontrado en la base de datos</p>
            </div>
        </div>
    `;
    
    if (data.data && Object.keys(data.data).length > 0) {
        html += '<div class="mt-3"><h6>Información disponible:</h6><div class="row">';
        
        Object.entries(data.data).forEach(([key, value]) => {
            if (value && value.toString().trim()) {
                const displayKey = formatFieldName(key);
                html += `
                    <div class="col-sm-6 mb-2">
                        <small class="text-muted">${displayKey}:</small><br>
                        <strong>${escapeHtml(value)}</strong>
                    </div>
                `;
            }
        });
        
        html += '</div></div>';
    }
    
    content.innerHTML = html;
    results.style.display = 'block';
    results.classList.add('fade-in');
}

function showNotFound(data) {
    const results = document.getElementById('results');
    const alert = document.getElementById('result-alert');
    const content = document.getElementById('result-content');
    
    if (!results || !alert || !content) return;
    
    alert.className = 'alert alert-warning';
    content.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle fa-2x text-warning me-3"></i>
            <div>
                <h5 class="mb-1">RNC No Encontrado</h5>
                <p class="mb-0">${data.message || 'El RNC no fue encontrado en la base de datos'}</p>
            </div>
        </div>
    `;
    
    results.style.display = 'block';
    results.classList.add('fade-in');
}

function showError(message) {
    const results = document.getElementById('results');
    const alert = document.getElementById('result-alert');
    const content = document.getElementById('result-content');
    
    if (!results || !alert || !content) return;
    
    alert.className = 'alert alert-danger';
    content.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-times-circle fa-2x text-danger me-3"></i>
            <div>
                <h5 class="mb-1">Error</h5>
                <p class="mb-0">${message}</p>
            </div>
        </div>
    `;
    
    results.style.display = 'block';
    results.classList.add('fade-in');
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

function formatFieldName(fieldName) {
    // Convert field names to readable format
    const fieldMap = {
        'nombre': 'Nombre',
        'estado': 'Estado',
        'categoria': 'Categoría',
        'regimen': 'Régimen',
        'tipo': 'Tipo',
        'actividad': 'Actividad Económica',
        'direccion': 'Dirección',
        'telefono': 'Teléfono',
        'email': 'Email'
    };
    
    const lowerField = fieldName.toLowerCase();
    return fieldMap[lowerField] || fieldName.charAt(0).toUpperCase() + fieldName.slice(1);
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function initSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function initTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Utility functions for API testing (can be used in browser console)
window.FourOneAPI = {
    validate: function(rnc) {
        return fetch(`/api/validate/${rnc}`)
            .then(response => response.json())
            .then(data => {
                console.log('Validation result:', data);
                return data;
            });
    },
    
    getInfo: function(rnc) {
        return fetch(`/api/info/${rnc}`)
            .then(response => response.json())
            .then(data => {
                console.log('RNC info:', data);
                return data;
            });
    },
    
    search: function(rncs) {
        return fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rncs: rncs })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Search results:', data);
            return data;
        });
    },
    
    status: function() {
        return fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('API status:', data);
                return data;
            });
    }
};

// Add some helpful console messages
console.log('🛡️ Four One RNC Validator loaded successfully!');
console.log('💡 Try using FourOneAPI.validate("12345678901") in the console');
