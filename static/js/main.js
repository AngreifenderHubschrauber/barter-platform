document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений через 5 секунд
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Превью изображения при вводе URL
    const imageUrlInput = document.querySelector('#id_image_url');
    if (imageUrlInput) {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'mt-2';
        previewContainer.innerHTML = '<img id="image-preview" class="img-thumbnail" style="max-width: 200px; display: none;">';
        imageUrlInput.parentNode.appendChild(previewContainer);
        
        const preview = document.getElementById('image-preview');
        
        imageUrlInput.addEventListener('input', function() {
            const url = this.value;
            if (url) {
                preview.src = url;
                preview.style.display = 'block';
                preview.onerror = function() {
                    this.style.display = 'none';
                };
            } else {
                preview.style.display = 'none';
            }
        });
    }

    // Счетчик символов для текстовых полей
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.innerHTML = `<small>0 / ${maxLength}</small>`;
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', function() {
            const length = this.value.length;
            counter.innerHTML = `<small>${length} / ${maxLength}</small>`;
        });
    });

    // Фильтрация объявлений в реальном времени
    const searchInput = document.querySelector('#id_query');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Можно добавить AJAX поиск здесь
            }, 500);
        });
    }

    // Активация tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Обработка форм с AJAX (опционально)
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalText = submitButton.innerHTML;
            
            // Показать загрузку
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Загрузка...';
            
            fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Успех
                    showNotification('success', data.message);
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                } else {
                    // Ошибка
                    showNotification('danger', data.message);
                }
            })
            .catch(error => {
                showNotification('danger', 'Произошла ошибка. Попробуйте еще раз.');
            })
            .finally(() => {
                submitButton.disabled = false;
                submitButton.innerHTML = originalText;
            });
        });
    });
});

// Функция для показа уведомлений
function showNotification(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Функция для обновления URL без перезагрузки страницы
function updateURL(params) {
    const url = new URL(window.location);
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    window.history.pushState({}, '', url);
}