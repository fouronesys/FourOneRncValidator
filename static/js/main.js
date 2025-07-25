// Four One RNC Validator - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initRNCValidator();
    initNameSearch();
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

function initNameSearch() {
    const nameInput = document.getElementById('name-input');
    const nameForm = document.getElementById('name-search-form');
    const suggestionsDropdown = document.getElementById('suggestions-dropdown');
    
    if (!nameInput || !nameForm) return;
    
    let searchTimeout;
    let currentQuery = '';
    
    // Handle input changes for autocomplete
    nameInput.addEventListener('input', function(e) {
        const query = e.target.value.trim();
        currentQuery = query;
        
        // Clear existing timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Hide suggestions if query is too short
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        // Debounce the search
        searchTimeout = setTimeout(() => {
            if (currentQuery === query) { // Only search if query hasn't changed
                searchByName(query, true); // true for autocomplete mode
            }
        }, 300);
    });
    
    // Handle form submission
    nameForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = nameInput.value.trim();
        
        if (!query) {
            showNameError('Por favor ingresa al menos 2 caracteres para buscar');
            return;
        }
        
        if (query.length < 2) {
            showNameError('La búsqueda debe tener al menos 2 caracteres');
            return;
        }
        
        hideSuggestions();
        searchByName(query, false); // false for full search mode
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!nameInput.contains(e.target) && !suggestionsDropdown.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Handle keyboard navigation in suggestions
    nameInput.addEventListener('keydown', function(e) {
        const suggestions = suggestionsDropdown.querySelectorAll('.dropdown-item');
        if (suggestions.length === 0) return;
        
        let activeIndex = -1;
        suggestions.forEach((item, index) => {
            if (item.classList.contains('active')) {
                activeIndex = index;
            }
        });
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = activeIndex < suggestions.length - 1 ? activeIndex + 1 : 0;
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = activeIndex > 0 ? activeIndex - 1 : suggestions.length - 1;
        } else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            suggestions[activeIndex].click();
            return;
        } else if (e.key === 'Escape') {
            hideSuggestions();
            return;
        }
        
        // Update active state
        suggestions.forEach((item, index) => {
            item.classList.toggle('active', index === activeIndex);
        });
    });
}

function searchByName(query, isAutocomplete = false) {
    const nameResults = document.getElementById('name-results');
    const nameLoading = document.getElementById('name-loading');
    const suggestionsDropdown = document.getElementById('suggestions-dropdown');
    
    if (!isAutocomplete) {
        // Show loading for full search
        if (nameResults) nameResults.style.display = 'none';
        if (nameLoading) nameLoading.style.display = 'block';
    }
    
    // Make API call
    const limit = isAutocomplete ? 8 : 10;
    fetch(`/api/search-by-name?q=${encodeURIComponent(query)}&limit=${limit}`)
        .then(response => {
            return response.json().then(data => {
                return { status: response.status, data: data };
            });
        })
        .then(result => {
            if (!isAutocomplete) {
                hideNameLoading();
            }
            
            if (result.status === 200 && result.data.suggestions && result.data.suggestions.length > 0) {
                if (isAutocomplete) {
                    showSuggestions(result.data.suggestions);
                } else {
                    showNameResults(result.data);
                }
            } else {
                if (isAutocomplete) {
                    hideSuggestions();
                } else {
                    showNameNotFound(result.data);
                }
            }
        })
        .catch(error => {
            if (!isAutocomplete) {
                hideNameLoading();
            }
            console.error('Name Search API Error:', error);
            if (!isAutocomplete) {
                showNameError('Error de conexión. Por favor intenta nuevamente.');
            } else {
                hideSuggestions();
            }
        });
}

function showSuggestions(suggestions) {
    const suggestionsDropdown = document.getElementById('suggestions-dropdown');
    if (!suggestionsDropdown) return;
    
    let html = '';
    suggestions.forEach(suggestion => {
        html += `
            <div class="dropdown-item" onclick="selectSuggestion('${escapeHtml(suggestion.nombre)}', '${suggestion.rnc}')">
                <div class="fw-bold">${escapeHtml(suggestion.nombre)}</div>
                <div class="text-muted small">
                    RNC: ${suggestion.rnc} 
                    ${suggestion.estado ? `• ${escapeHtml(suggestion.estado)}` : ''}
                </div>
                ${suggestion.actividad_economica ? `<div class="text-muted small">${escapeHtml(suggestion.actividad_economica)}</div>` : ''}
            </div>
        `;
    });
    
    suggestionsDropdown.innerHTML = html;
    suggestionsDropdown.classList.add('show');
}

function hideSuggestions() {
    const suggestionsDropdown = document.getElementById('suggestions-dropdown');
    if (suggestionsDropdown) {
        suggestionsDropdown.classList.remove('show');
        suggestionsDropdown.innerHTML = '';
    }
}

function selectSuggestion(name, rnc) {
    const nameInput = document.getElementById('name-input');
    if (nameInput) {
        nameInput.value = name;
    }
    hideSuggestions();
    
    // Optionally, trigger a full search or show RNC details
    searchByName(name, false);
}

function showNameResults(data) {
    const nameResults = document.getElementById('name-results');
    const alert = document.getElementById('name-result-alert');
    const content = document.getElementById('name-result-content');
    
    if (!nameResults || !alert || !content) return;
    
    alert.className = 'alert alert-success';
    
    let html = `
        <div class="d-flex align-items-center mb-3">
            <i class="fas fa-building fa-2x text-success me-3"></i>
            <div>
                <h5 class="mb-1">Búsqueda Exitosa</h5>
                <p class="mb-0">Se encontraron ${data.total_found} empresa(s) que coinciden con "${data.query}"</p>
            </div>
        </div>
    `;
    
    if (data.suggestions && data.suggestions.length > 0) {
        html += '<div class="mt-3">';
        data.suggestions.forEach(company => {
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h6 class="card-title mb-1">${escapeHtml(company.nombre)}</h6>
                                <p class="text-muted small mb-1">RNC: <strong>${company.rnc}</strong></p>
                                ${company.estado ? `<span class="badge bg-${company.estado === 'ACTIVE' ? 'success' : 'warning'}">${escapeHtml(company.estado)}</span>` : ''}
                            </div>
                            <div class="col-md-4 text-end">
                                <button class="btn btn-sm btn-outline-primary" onclick="validateRNC('${company.rnc}')">
                                    <i class="fas fa-search me-1"></i>Ver Detalles
                                </button>
                            </div>
                        </div>
                        ${company.actividad_economica ? `<div class="mt-2"><small class="text-muted">${escapeHtml(company.actividad_economica)}</small></div>` : ''}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    content.innerHTML = html;
    nameResults.style.display = 'block';
    nameResults.classList.add('fade-in');
}

function showNameNotFound(data) {
    const nameResults = document.getElementById('name-results');
    const alert = document.getElementById('name-result-alert');
    const content = document.getElementById('name-result-content');
    
    if (!nameResults || !alert || !content) return;
    
    alert.className = 'alert alert-warning';
    content.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle fa-2x text-warning me-3"></i>
            <div>
                <h5 class="mb-1">Sin Resultados</h5>
                <p class="mb-0">${data.message || 'No se encontraron empresas que coincidan con tu búsqueda'}</p>
            </div>
        </div>
    `;
    
    nameResults.style.display = 'block';
    nameResults.classList.add('fade-in');
}

function showNameError(message) {
    const nameResults = document.getElementById('name-results');
    const alert = document.getElementById('name-result-alert');
    const content = document.getElementById('name-result-content');
    
    if (!nameResults || !alert || !content) return;
    
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
    
    nameResults.style.display = 'block';
    nameResults.classList.add('fade-in');
}

function hideNameLoading() {
    const nameLoading = document.getElementById('name-loading');
    if (nameLoading) {
        nameLoading.style.display = 'none';
    }
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
    },
    
    searchByName: function(query, limit = 10) {
        return fetch(`/api/search-by-name?q=${encodeURIComponent(query)}&limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                console.log('Name search results:', data);
                return data;
            });
    }
};

// Add some helpful console messages
console.log('🛡️ Four One RNC Validator loaded successfully!');
console.log('💡 Try using FourOneAPI.validate("12345678901") in the console');
