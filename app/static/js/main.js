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
    initAccordion();
    initConfirmations();
    initSubscriptionsCarousel();
    initReactions();
    initCommentForm();
    initSubscribeButtons();
    initThumbnailChoice();
    initCopyLink();
});


// ============================================
//   ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ
// ============================================

function initThemeToggle() {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

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

    function goToSlide(index) {
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        currentIndex = index;
        if (currentIndex >= slides.length) currentIndex = 0;
        if (currentIndex < 0) currentIndex = slides.length - 1;

        slides[currentIndex].classList.add('active');
        dots[currentIndex].classList.add('active');
    }

    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    function startAutoplay() {
        interval = setInterval(nextSlide, 5000);
    }

    function stopAutoplay() {
        clearInterval(interval);
    }

    dots.forEach((dot, index) => {
        dot.addEventListener('click', function() {
            stopAutoplay();
            goToSlide(index);
            startAutoplay();
        });
    });

    carousel.addEventListener('mouseenter', stopAutoplay);
    carousel.addEventListener('mouseleave', startAutoplay);

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

            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

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

    const fileUpload = fileInput.closest('.file-upload');
    if (!fileUpload) return;

    const fileLabel = fileUpload.querySelector('.file-label');
    const fileText = fileUpload.querySelector('.file-text');

    if (!fileLabel || !fileText) return;

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
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}


// ============================================
//   АККОРДЕОН ПОДПИСОК
// ============================================

function initAccordion() {
    const headers = document.querySelectorAll('.accordion-header');

    headers.forEach(header => {
        header.addEventListener('click', function(e) {
            if (e.target.closest('.unsub-form')) return;

            const item = this.closest('.accordion-item');
            item.classList.toggle('open');
        });
    });
}


// ============================================
//   ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ
// ============================================

function initConfirmations() {
    const clearForm = document.querySelector('.clear-history-form');
    if (clearForm) {
        clearForm.addEventListener('submit', function(e) {
            if (!confirm('Очистить всю историю просмотров?')) {
                e.preventDefault();
            }
        });
    }

    const deleteForm = document.querySelector('.delete-video-form');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            if (!confirm('Удалить это видео? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    }
}


// ============================================
//   КАРУСЕЛЬ ПОДПИСОК
// ============================================

function initSubscriptionsCarousel() {
    const bubbles = document.querySelectorAll('.channel-bubble');
    const videoBlocks = document.querySelectorAll('.channel-videos');

    if (bubbles.length === 0) return;

    bubbles.forEach(bubble => {
        bubble.addEventListener('click', function() {
            const channelId = this.dataset.channelId;

            bubbles.forEach(b => b.classList.remove('active'));
            videoBlocks.forEach(v => v.classList.remove('active'));

            this.classList.add('active');

            const targetVideos = document.querySelector(`.channel-videos[data-channel-id="${channelId}"]`);
            if (targetVideos) {
                targetVideos.classList.add('active');
            }
        });
    });
}


// ============================================
//   AJAX РЕАКЦИИ
// ============================================

function initReactions() {
    const reactionBtns = document.querySelectorAll('.reaction-ajax-btn');

    reactionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();

            const url = this.dataset.url;
            const btn = this;

            btn.style.transform = 'scale(1.2)';
            setTimeout(() => btn.style.transform = '', 150);

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateReactionUI(data);
                }
            })
            .catch(err => console.error('Ошибка:', err));
        });
    });
}

function updateReactionUI(data) {
    document.querySelectorAll('.reaction-ajax-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.reaction === data.user_reaction) {
            btn.classList.add('active');
        }
    });

    const fireCount = document.getElementById('fire-count');
    const goodCount = document.getElementById('good-count');
    const badCount = document.getElementById('bad-count');
    const karmaTotal = document.getElementById('karma-total');

    if (fireCount) fireCount.textContent = data.reactions.fire;
    if (goodCount) goodCount.textContent = data.reactions.good;
    if (badCount) badCount.textContent = data.reactions.bad;
    if (karmaTotal) karmaTotal.textContent = data.karma;
}


// ============================================
//   AJAX КОММЕНТАРИИ
// ============================================

function initCommentForm() {
    const form = document.getElementById('comment-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const textarea = form.querySelector('textarea');
        const text = textarea.value.trim();
        const url = form.dataset.url;

        if (!text) return;

        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = '⏳ Отправка...';

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addCommentToList(data.comment);
                textarea.value = '';
                updateCommentCount(1);
                showToast('Комментарий добавлен!', 'success');
            } else {
                showToast(data.error || 'Ошибка', 'danger');
            }
        })
        .catch(err => {
            console.error('Ошибка:', err);
            showToast('Ошибка отправки', 'danger');
        })
        .finally(() => {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        });
    });
}

function addCommentToList(comment) {
    const list = document.getElementById('comments-list');
    if (!list) return;

    const emptyMsg = list.querySelector('.empty');
    if (emptyMsg) emptyMsg.remove();

    const html = `
        <div class="comment-item" data-id="${comment.id}" style="animation: fadeSlideIn 0.3s ease;">
            <a href="/user/${comment.author.username}">
                <img
                    src="/static/uploads/avatars/${comment.author.avatar}"
                    class="comment-avatar"
                    onerror="this.src='/static/img/default_avatar.svg'"
                >
            </a>
            <div class="comment-body">
                <div class="comment-head">
                    <a href="/user/${comment.author.username}" class="comment-author">
                        ${comment.author.username}
                    </a>
                    <span class="comment-date">${comment.created_at}</span>
                </div>
                <p class="comment-text">${escapeHtml(comment.text)}</p>
            </div>
        </div>
    `;

    list.insertAdjacentHTML('afterbegin', html);
}

function updateCommentCount(delta) {
    const counter = document.getElementById('comments-count');
    if (counter) {
        const current = parseInt(counter.textContent) || 0;
        counter.textContent = current + delta;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


// ============================================
//   AJAX ПОДПИСКИ
// ============================================

function initSubscribeButtons() {
    document.addEventListener('click', function(e) {
        const btn = e.target.closest('.subscribe-ajax-btn');
        if (!btn) return;

        e.preventDefault();

        const url = btn.dataset.url;
        const username = btn.dataset.username;

        btn.style.transform = 'scale(0.95)';
        btn.disabled = true;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSubscribeUI(btn, data, username);

                if (data.is_following) {
                    showToast(`Вы подписались на ${username}!`, 'success');
                } else {
                    showToast(`Вы отписались от ${username}`, 'info');
                }
            }
        })
        .catch(err => {
            console.error('Ошибка:', err);
            showToast('Ошибка подписки', 'danger');
        })
        .finally(() => {
            btn.style.transform = '';
            btn.disabled = false;
        });
    });
}

function updateSubscribeUI(btn, data, username) {
    const isFollowing = data.is_following;
    const followersCount = data.followers_count;

    if (isFollowing) {
        btn.classList.remove('not-subscribed');
        btn.classList.add('subscribed');
        btn.dataset.url = `/user/${username}/unfollow`;
        btn.innerHTML = `
            <span class="btn-text-default">✓ Подписан</span>
            <span class="btn-text-hover">Отписаться</span>
        `;
    } else {
        btn.classList.remove('subscribed');
        btn.classList.add('not-subscribed');
        btn.dataset.url = `/user/${username}/follow`;
        btn.innerHTML = '+ Подписаться';
    }

    const subsCounter = document.querySelector('.watch-author-subs, .profile-subs-count');
    if (subsCounter && subsCounter.dataset.username === username) {
        subsCounter.textContent = `${followersCount} подписчиков`;
    }
}


// ============================================
//   ВЫБОР ОБЛОЖКИ
// ============================================

function initThumbnailChoice() {
    const radioCards = document.querySelectorAll('.radio-card');
    const customUpload = document.getElementById('customThumbUpload');
    const thumbInput = document.getElementById('thumbInput');
    const thumbPreview = document.getElementById('thumbPreview');
    const thumbPreviewImg = document.getElementById('thumbPreviewImg');
    const thumbFileName = document.getElementById('thumbFileName');

    if (radioCards.length === 0) return;

    radioCards.forEach(card => {
        card.addEventListener('click', function() {
            radioCards.forEach(c => c.classList.remove('active'));
            this.classList.add('active');

            const target = this.dataset.target;

            if (target === 'custom' && customUpload) {
                customUpload.style.display = 'block';
            } else if (customUpload) {
                customUpload.style.display = 'none';
                if (thumbInput) thumbInput.value = '';
                if (thumbPreview) thumbPreview.style.display = 'none';
                if (thumbFileName) thumbFileName.textContent = 'Выберите изображение';
            }
        });
    });

    if (thumbInput) {
        thumbInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                if (thumbFileName) thumbFileName.textContent = file.name;

                const reader = new FileReader();
                reader.onload = function(e) {
                    if (thumbPreviewImg) thumbPreviewImg.src = e.target.result;
                    if (thumbPreview) thumbPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}


// ============================================
//   КОПИРОВАНИЕ ССЫЛКИ НА ВИДЕО
// ============================================

function initCopyLink() {
    const copyBtns = document.querySelectorAll('.copy-link-btn');

    copyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.dataset.url;

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(() => {
                    showCopySuccess(btn);
                }).catch(err => {
                    fallbackCopy(url, btn);
                });
            } else {
                fallbackCopy(url, btn);
            }
        });
    });
}

function showCopySuccess(btn) {
    const originalText = btn.textContent;
    btn.textContent = '✅ Скопировано!';
    btn.style.borderColor = 'var(--success)';
    btn.style.color = 'var(--success)';

    showToast('Ссылка скопирована!', 'success');

    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.borderColor = '';
        btn.style.color = '';
    }, 2000);
}

function fallbackCopy(text, btn) {
    const input = document.createElement('input');
    input.value = text;
    input.style.position = 'fixed';
    input.style.opacity = '0';
    document.body.appendChild(input);
    input.select();

    try {
        document.execCommand('copy');
        showCopySuccess(btn);
    } catch (err) {
        showToast('Не удалось скопировать', 'danger');
    }

    document.body.removeChild(input);
}


// ============================================
//   TOAST УВЕДОМЛЕНИЯ
// ============================================

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}