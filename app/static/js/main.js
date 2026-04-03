/* app/static/js/main.js */
/* VidSphere — Космический видеохостинг */

// ============================================
//   ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ СТРАНИЦЫ
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initHeroCarousel();
    initMoodTabs();
    initFileUpload();
    initAvatarPreview();
    initAutoHideAlerts();
});


// ============================================
//   ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ
// ============================================

function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    // Загружаем сохранённую тему
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    // Обработчик клика
    toggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
    toggle.title = theme === 'dark' ? 'Светлая тема' : 'Тёмная тема';
}


// ============================================
//   HERO КАРУСЕЛЬ
// ============================================

function initHeroCarousel() {
    const carousel = document.getElementById('heroCarousel');
    if (!carousel) return;

    const slides = carousel.querySelectorAll('.hero-slide');
    const dots = document.querySelectorAll('.hero-dot');

    if (slides.length <= 1) return;

    let currentIndex = 0;
    let interval;

    // Функция переключения слайда
    function goToSlide(index) {
        // Убираем активный класс со всех
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        // Устанавливаем новый индекс
        currentIndex = index;
        if (currentIndex >= slides.length) currentIndex = 0;
        if (currentIndex < 0) currentIndex = slides.length - 1;

        // Активируем нужный слайд
        slides[currentIndex].classList.add('active');
        dots[currentIndex].classList.add('active');
    }

    // Следующий слайд
    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    // Запуск автопрокрутки
    function startAutoplay() {
        interval = setInterval(nextSlide, 5000); // 5 секунд
    }

    // Остановка автопрокрутки
    function stopAutoplay() {
        clearInterval(interval);
    }

    // Клики по точкам
    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            stopAutoplay();
            goToSlide(index);
            startAutoplay();
        });
    });

    // Пауза при наведении
    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

    // Запускаем
    startAutoplay();
}


// ============================================
//   ТАБЫ НАСТРОЕНИЙ
// ============================================

function initMoodTabs() {
    const tabs = document.querySelectorAll('.mood-tab');
    const panels = document.querySelectorAll('.mood-panel');

    if (tabs.length === 0) return;

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const mood = this.getAttribute('data-mood');

            // Убираем активный класс
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            // Активируем выбранный
            this.classList.add('active');

            const targetPanel = document.querySelector(`.mood-panel[data-mood="${mood}"]`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}


// ============================================
//   ЗАГРУЗКА ФАЙЛОВ
// ============================================

function initFileUpload() {
    const fileInput = document.getElementById('videoInput');
    if (!fileInput) return;

    const fileLabel = fileInput.closest('.file-upload').querySelector('.file-label');
    const fileText = fileLabel.querySelector('.file-text');

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            fileText.textContent = `${file.name} (${sizeMB} MB)`;
            fileLabel.style.borderColor = 'var(--primary)';
            fileLabel.style.background = 'var(--bg-card-hover)';
        }
    });

    // Drag and Drop
    fileLabel.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--primary)';
        this.style.background = 'var(--bg-card-hover)';
    });

    fileLabel.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '';
        this.style.background = '';
    });

    fileLabel.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '';
        this.style.background = '';

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
}


// ============================================
//   ПРЕДПРОСМОТР АВАТАРА
// ============================================

function initAvatarPreview() {
    const avatarInput = document.getElementById('avatarInput');
    const avatarPreview = document.getElementById('avatarPreview');

    if (!avatarInput || !avatarPreview) return;

    avatarInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const reader = new FileReader();

            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
            };

            reader.readAsDataURL(this.files[0]);
        }
    });
}


// ============================================
//   АВТОСКРЫТИЕ АЛЕРТОВ
// ============================================

function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(alert => {
        // Автоскрытие через 5 секунд
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}


// ============================================
//   ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ
// ============================================

// Используется inline: onsubmit="return confirm('Удалить?')"


// ============================================
//   КОПИРОВАНИЕ ССЫЛКИ (для будущего)
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Ссылка скопирована!');
    }).catch(err => {
        console.error('Ошибка копирования:', err);
    });
}


// ============================================
//   TOAST УВЕДОМЛЕНИЯ (для будущего)
// ============================================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.animation = 'fadeIn 0.3s ease';
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}


// ============================================
//   ЛЕНИВАЯ ЗАГРУЗКА ИЗОБРАЖЕНИЙ
// ============================================

// Используется атрибут loading="lazy" в HTML


// ============================================
//   БЕСКОНЕЧНАЯ ПРОКРУТКА (для будущего)
// ============================================

function initInfiniteScroll(callback) {
    let loading = false;

    window.addEventListener('scroll', function() {
        if (loading) return;

        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;

        // Если до конца страницы осталось меньше 200px
        if (scrollTop + windowHeight >= documentHeight - 200) {
            loading = true;
            callback().finally(() => {
                loading = false;
            });
        }
    });
}