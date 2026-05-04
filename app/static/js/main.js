/* app/static/js/main.js */

document.addEventListener('DOMContentLoaded', function() {
    initThemeToggle();
    initHeroCarousel();
    initMoodTabs();
    initFileUpload();
    initAvatarPreview();
    initAutoHideAlerts();
    initSubscriptionsCarousel();
    initReactions();
    initCommentForm();
    initSubscribeButtons();
    initThumbnailChoice();
    initCopyLink();
    initGlitchEffects();
    initCustomPlayer();
    initVideoUploadProgress();
    initDeleteComment();
    initQualitySelector();
    initCommentReactions();
    initCommentReplies();
    initDeleteReply();
});

// ============================================
// ТЕМА
// ============================================
function initThemeToggle() {
    var toggle = document.getElementById('themeToggle');
    if (!toggle) return;

    var savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    toggle.addEventListener('click', function() {
        var currentTheme = document.documentElement.getAttribute('data-theme');
        var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });
}

function updateThemeIcon(theme) {
    var toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    var icon = toggle.querySelector('.theme-icon');
    if (icon) {
        icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// ============================================
// HERO КАРУСЕЛЬ
// ============================================
function initHeroCarousel() {
    var carousel = document.getElementById('heroCarousel');
    if (!carousel) return;

    var slides = carousel.querySelectorAll('.hero-slide');
    var dots = document.querySelectorAll('.hero-dot');
    if (slides.length <= 1) return;

    var currentIndex = 0;
    var interval = null;

    function goToSlide(index) {
        slides.forEach(function(slide) { slide.classList.remove('active'); });
        dots.forEach(function(dot) { dot.classList.remove('active'); });
        currentIndex = index;
        if (currentIndex >= slides.length) currentIndex = 0;
        if (currentIndex < 0) currentIndex = slides.length - 1;
        slides[currentIndex].classList.add('active');
        if (dots[currentIndex]) dots[currentIndex].classList.add('active');
    }

    function nextSlide() { goToSlide(currentIndex + 1); }
    function startAutoplay() { interval = setInterval(nextSlide, 5000); }
    function stopAutoplay() { if (interval) clearInterval(interval); }

    dots.forEach(function(dot, index) {
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
// ТАБЫ НАСТРОЕНИЙ
// ============================================
function initMoodTabs() {
    var tabs = document.querySelectorAll('.mood-tab');
    var panels = document.querySelectorAll('.mood-panel');
    if (tabs.length === 0) return;

    tabs.forEach(function(tab) {
        tab.addEventListener('click', function() {
            var mood = this.getAttribute('data-mood');
            tabs.forEach(function(t) { t.classList.remove('active'); });
            panels.forEach(function(p) { p.classList.remove('active'); });
            this.classList.add('active');
            var panel = document.querySelector('.mood-panel[data-mood="' + mood + '"]');
            if (panel) panel.classList.add('active');
        });
    });
}

// ============================================
// ЗАГРУЗКА ФАЙЛОВ
// ============================================
function initFileUpload() {
    var fileInput = document.getElementById('videoInput');
    if (!fileInput) return;
    var fileUpload = fileInput.closest('.file-upload');
    if (!fileUpload) return;
    var fileLabel = fileUpload.querySelector('.file-label');
    var fileText = fileUpload.querySelector('.file-text');
    if (!fileLabel || !fileText) return;

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            var file = this.files[0];
            var sizeMB = (file.size / (1024 * 1024)).toFixed(2);
            fileText.textContent = file.name + ' (' + sizeMB + ' MB)';
            fileLabel.style.borderColor = 'var(--primary)';
        }
    });
}

// ============================================
// ПРЕВЬЮ АВАТАРА
// ============================================
function initAvatarPreview() {
    var avatarInput = document.getElementById('avatarInput');
    var avatarPreview = document.getElementById('avatarPreview');
    if (!avatarInput || !avatarPreview) return;

    avatarInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            reader.onload = function(e) { avatarPreview.src = e.target.result; };
            reader.readAsDataURL(this.files[0]);
        }
    });
}

// ============================================
// АВТОСКРЫТИЕ АЛЕРТОВ
// ============================================
function initAutoHideAlerts() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 300);
        }, 5000);
    });
}

// ============================================
// КАРУСЕЛЬ ПОДПИСОК
// ============================================
function initSubscriptionsCarousel() {
    var bubbles = document.querySelectorAll('.channel-bubble');
    var videoBlocks = document.querySelectorAll('.channel-videos');
    if (bubbles.length === 0) return;

    bubbles.forEach(function(bubble) {
        bubble.addEventListener('click', function() {
            var channelId = this.dataset.channelId;
            bubbles.forEach(function(b) { b.classList.remove('active'); });
            videoBlocks.forEach(function(v) { v.classList.remove('active'); });
            this.classList.add('active');
            var target = document.querySelector('.channel-videos[data-channel-id="' + channelId + '"]');
            if (target) target.classList.add('active');
        });
    });
}

// ============================================
// AJAX РЕАКЦИИ НА ВИДЕО
// ============================================
function initReactions() {
    var btns = document.querySelectorAll('.reaction-ajax-btn');
    btns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var url = this.dataset.url;
            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
            })
            .then(function(r) { return r.json(); })
            .then(function(data) { if (data.success) updateReactionUI(data); })
            .catch(function(err) { console.error(err); });
        });
    });
}

function updateReactionUI(data) {
    document.querySelectorAll('.reaction-ajax-btn').forEach(function(btn) {
        btn.classList.remove('active');
        if (btn.dataset.reaction === data.user_reaction) btn.classList.add('active');
    });
    var fire = document.getElementById('fire-count');
    var good = document.getElementById('good-count');
    var bad = document.getElementById('bad-count');
    var karma = document.getElementById('karma-total');
    if (fire && data.reactions) fire.textContent = data.reactions.fire;
    if (good && data.reactions) good.textContent = data.reactions.good;
    if (bad && data.reactions) bad.textContent = data.reactions.bad;
    if (karma) karma.textContent = data.karma;
}

// ============================================
// AJAX КОММЕНТАРИИ
// ============================================
function initCommentForm() {
    var form = document.getElementById('comment-form');
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        var input = form.querySelector('.comment-input') || form.querySelector('textarea') || form.querySelector('input[type="text"]');
        if (!input) return;

        var text = input.value.trim();
        var url = form.dataset.url;
        if (!text) return;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                addCommentToList(data.comment);
                input.value = '';
                showToast('Комментарий добавлен!', 'success');
                var countEl = document.getElementById('comments-count');
                if (countEl) {
                    countEl.textContent = parseInt(countEl.textContent || 0) + 1;
                }
            }
        })
        .catch(function(err) {
            console.error(err);
            showToast('Ошибка отправки', 'danger');
        });
    });
}

function addCommentToList(comment) {
    var list = document.getElementById('comments-list');
    if (!list) return;

    var empty = list.querySelector('.empty-hint');
    if (empty) empty.remove();

    var html = '<div class="comment-block comment-new" id="comment-' + comment.id + '">' +
        '<div class="comment">' +
        '<div class="comment-body">' +
        '<div class="comment-header">' +
        '<span class="c-author">' + escapeHtml(comment.author.username) + '</span>' +
        '</div>' +
        '<span class="c-text">' + escapeHtml(comment.text) + '</span>' +
        '</div>' +
        '</div>' +
        '</div>';

    list.insertAdjacentHTML('afterbegin', html);

    var newComment = list.querySelector('.comment-new');
    if (newComment) {
        newComment.style.opacity = '0';
        newComment.style.transform = 'translateY(-10px)';
        setTimeout(function() {
            newComment.style.transition = 'all 0.3s ease';
            newComment.style.opacity = '1';
            newComment.style.transform = 'translateY(0)';
            newComment.classList.remove('comment-new');
        }, 10);
    }
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// AJAX ПОДПИСКИ
// ============================================
function initSubscribeButtons() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.subscribe-ajax-btn');
        if (!btn) return;
        e.preventDefault();

        var url = btn.dataset.url;
        var username = btn.dataset.username;
        btn.disabled = true;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                updateSubscribeButton(btn, username, data.is_following);
                showToast(
                    data.is_following ? 'Вы подписались на ' + username : 'Вы отписались от ' + username,
                    data.is_following ? 'success' : 'info'
                );
            }
            btn.disabled = false;
        })
        .catch(function(err) {
            console.error(err);
            btn.disabled = false;
            showToast('Ошибка', 'danger');
        });
    });
}

function updateSubscribeButton(btn, username, isFollowing) {
    if (isFollowing) {
        btn.classList.remove('not-subscribed');
        btn.classList.add('subscribed');
        btn.dataset.url = '/user/' + username + '/unfollow';
        if (btn.classList.contains('btn-sub')) {
            btn.innerHTML = '<span class="btn-text-default">✓</span><span class="btn-text-hover">✕</span>';
        } else {
            btn.innerHTML = '<span class="btn-text-default">✓ Вы подписаны</span><span class="btn-text-hover">Отписаться</span>';
        }
    } else {
        btn.classList.remove('subscribed');
        btn.classList.add('not-subscribed');
        btn.dataset.url = '/user/' + username + '/follow';
        if (btn.classList.contains('btn-sub')) {
            btn.innerHTML = '+';
        } else {
            btn.innerHTML = '+ Подписаться';
        }
    }
}

// ============================================
// ВЫБОР ОБЛОЖКИ
// ============================================
function initThumbnailChoice() {
    var cards = document.querySelectorAll('.radio-card');
    var customUpload = document.getElementById('customThumbUpload');
    if (cards.length === 0) return;

    cards.forEach(function(card) {
        card.addEventListener('click', function() {
            cards.forEach(function(c) { c.classList.remove('active'); });
            this.classList.add('active');
            if (this.dataset.target === 'custom' && customUpload) {
                customUpload.style.display = 'block';
            } else if (customUpload) {
                customUpload.style.display = 'none';
            }
        });
    });
}

// ============================================
// КОПИРОВАНИЕ ССЫЛКИ
// ============================================
function initCopyLink() {
    var btns = document.querySelectorAll('.copy-link-btn');
    btns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var url = this.dataset.url;
            navigator.clipboard.writeText(url).then(function() {
                showToast('Ссылка скопирована!', 'success');
            }).catch(function() {
                var textarea = document.createElement('textarea');
                textarea.value = url;
                document.body.appendChild(textarea);
                textarea.select();
                document.execCommand('copy');
                document.body.removeChild(textarea);
                showToast('Ссылка скопирована!', 'success');
            });
        });
    });
}

// ============================================
// ГЛИТЧ-ЭФФЕКТЫ
// ============================================
function initGlitchEffects() {
    var glitchElements = document.querySelectorAll('.glitch-hover');
    glitchElements.forEach(function(el) {
        el.addEventListener('mouseenter', function() {
            this.classList.add('glitching');
            var self = this;
            setTimeout(function() {
                self.classList.remove('glitching');
            }, 300);
        });
    });
}

// ============================================
// КАСТОМНЫЙ ВИДЕО ПЛЕЕР
// ============================================
function initCustomPlayer() {
    var player = document.getElementById('customPlayer');
    var video = document.getElementById('videoElement');
    if (!player || !video) return;

    var playPauseBtn = document.getElementById('playPauseBtn');
    var bigPlayBtn = document.getElementById('bigPlayBtn');
    var stopBtn = document.getElementById('stopBtn');
    var rewindBtn = document.getElementById('rewindBtn');
    var forwardBtn = document.getElementById('forwardBtn');
    var muteBtn = document.getElementById('muteBtn');
    var volumeSlider = document.getElementById('volumeSlider');
    var progressWrap = document.getElementById('progressWrap');
    var progressBar = document.getElementById('progressBar');
    var progressBuffered = document.getElementById('progressBuffered');
    var progressTooltip = document.getElementById('progressTooltip');
    var currentTimeEl = document.getElementById('currentTime');
    var durationEl = document.getElementById('duration');
    var speedBtn = document.getElementById('speedBtn');
    var speedMenu = document.getElementById('speedMenu');
    var pipBtn = document.getElementById('pipBtn');
    var fullscreenBtn = document.getElementById('fullscreenBtn');
    var wideBtn = document.getElementById('wideBtn');
    var watchContainer = document.querySelector('.watch-compact');

    function formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        var mins = Math.floor(seconds / 60);
        var secs = Math.floor(seconds % 60);
        return mins + ':' + (secs < 10 ? '0' : '') + secs;
    }

    function togglePlay() {
        if (video.paused) { video.play(); } else { video.pause(); }
    }

    if (playPauseBtn) playPauseBtn.addEventListener('click', togglePlay);
    if (bigPlayBtn) bigPlayBtn.addEventListener('click', togglePlay);

    video.addEventListener('click', function(e) {
        if (e.target === video) togglePlay();
    });

    video.addEventListener('play', function() { player.classList.add('playing'); });
    video.addEventListener('pause', function() { player.classList.remove('playing'); });
    video.addEventListener('ended', function() { player.classList.remove('playing'); });

    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            video.pause();
            video.currentTime = 0;
            player.classList.remove('playing');
        });
    }

    if (rewindBtn) {
        rewindBtn.addEventListener('click', function() {
            video.currentTime = Math.max(0, video.currentTime - 10);
        });
    }

    if (forwardBtn) {
        forwardBtn.addEventListener('click', function() {
            video.currentTime = Math.min(video.duration || 0, video.currentTime + 10);
        });
    }

    if (muteBtn) {
        muteBtn.addEventListener('click', function() {
            video.muted = !video.muted;
            player.classList.toggle('muted', video.muted);
            if (volumeSlider) volumeSlider.value = video.muted ? 0 : video.volume * 100;
        });
    }

    if (volumeSlider) {
        volumeSlider.addEventListener('input', function() {
            video.volume = this.value / 100;
            video.muted = this.value == 0;
            player.classList.toggle('muted', video.muted);
        });
    }

    video.addEventListener('timeupdate', function() {
        if (progressBar && video.duration) {
            progressBar.style.width = (video.currentTime / video.duration) * 100 + '%';
        }
        if (currentTimeEl) currentTimeEl.textContent = formatTime(video.currentTime);
    });

    video.addEventListener('loadedmetadata', function() {
        if (durationEl) durationEl.textContent = formatTime(video.duration);
    });

    video.addEventListener('progress', function() {
        if (progressBuffered && video.buffered.length > 0) {
            var buffered = video.buffered.end(video.buffered.length - 1);
            progressBuffered.style.width = (buffered / video.duration) * 100 + '%';
        }
    });

    if (progressWrap) {
        progressWrap.addEventListener('click', function(e) {
            var rect = this.getBoundingClientRect();
            video.currentTime = ((e.clientX - rect.left) / rect.width) * video.duration;
        });

        progressWrap.addEventListener('mousemove', function(e) {
            if (progressTooltip && video.duration) {
                var rect = this.getBoundingClientRect();
                var time = ((e.clientX - rect.left) / rect.width) * video.duration;
                progressTooltip.textContent = formatTime(time);
                progressTooltip.style.left = (e.clientX - rect.left) + 'px';
            }
        });
    }

    if (speedMenu) {
        var speedBtns = speedMenu.querySelectorAll('button');
        speedBtns.forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                var speed = parseFloat(this.dataset.speed);
                video.playbackRate = speed;
                if (speedBtn) speedBtn.textContent = speed + 'x';
                speedBtns.forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');
            });
        });
    }

    if (pipBtn) {
        if (!('pictureInPictureEnabled' in document) || !document.pictureInPictureEnabled) {
            pipBtn.style.display = 'none';
        } else {
            pipBtn.addEventListener('click', function() {
                if (document.pictureInPictureElement) {
                    document.exitPictureInPicture().catch(function(err) { console.log(err); });
                } else {
                    video.requestPictureInPicture().catch(function(err) {
                        showToast('PiP не поддерживается', 'warning');
                    });
                }
            });
        }
    }

    function toggleFullscreen() {
        var isFs = document.fullscreenElement || document.webkitFullscreenElement ||
                   document.mozFullScreenElement || document.msFullscreenElement;
        if (!isFs) {
            if (player.requestFullscreen) player.requestFullscreen();
            else if (player.webkitRequestFullscreen) player.webkitRequestFullscreen();
            else if (player.mozRequestFullScreen) player.mozRequestFullScreen();
            else if (player.msRequestFullscreen) player.msRequestFullscreen();
        } else {
            if (document.exitFullscreen) document.exitFullscreen();
            else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
            else if (document.mozCancelFullScreen) document.mozCancelFullScreen();
            else if (document.msExitFullscreen) document.msExitFullscreen();
        }
    }

    if (fullscreenBtn) fullscreenBtn.addEventListener('click', toggleFullscreen);
    video.addEventListener('dblclick', toggleFullscreen);

    function onFullscreenChange() {
        var isFs = document.fullscreenElement || document.webkitFullscreenElement ||
                   document.mozFullScreenElement || document.msFullscreenElement;
        player.classList.toggle('fullscreen', !!isFs);
    }

    document.addEventListener('fullscreenchange', onFullscreenChange);
    document.addEventListener('webkitfullscreenchange', onFullscreenChange);
    document.addEventListener('mozfullscreenchange', onFullscreenChange);
    document.addEventListener('MSFullscreenChange', onFullscreenChange);

    if (wideBtn && watchContainer) {
        wideBtn.addEventListener('click', function() {
            watchContainer.classList.toggle('wide-mode');
            this.classList.toggle('active');
            this.textContent = watchContainer.classList.contains('wide-mode') ? '⬄' : '⬌';
            this.title = watchContainer.classList.contains('wide-mode') ? 'Обычный режим' : 'Широкий режим';
        });
    }

    video.addEventListener('waiting', function() { player.classList.add('loading'); });
    video.addEventListener('canplay', function() { player.classList.remove('loading'); });
    video.addEventListener('error', function() {
        player.classList.remove('loading');
        showToast('Ошибка загрузки видео', 'danger');
    });

    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (!document.getElementById('customPlayer')) return;

        switch(e.code) {
            case 'Space': e.preventDefault(); togglePlay(); break;
            case 'ArrowLeft': e.preventDefault(); video.currentTime = Math.max(0, video.currentTime - 5); break;
            case 'ArrowRight': e.preventDefault(); video.currentTime = Math.min(video.duration || 0, video.currentTime + 5); break;
            case 'ArrowUp': e.preventDefault(); video.volume = Math.min(1, video.volume + 0.1); if (volumeSlider) volumeSlider.value = video.volume * 100; break;
            case 'ArrowDown': e.preventDefault(); video.volume = Math.max(0, video.volume - 0.1); if (volumeSlider) volumeSlider.value = video.volume * 100; break;
            case 'KeyM': video.muted = !video.muted; player.classList.toggle('muted', video.muted); if (volumeSlider) volumeSlider.value = video.muted ? 0 : video.volume * 100; break;
            case 'KeyF': toggleFullscreen(); break;
            case 'KeyW': if (wideBtn) wideBtn.click(); break;
            case 'Escape': if (document.fullscreenElement) document.exitFullscreen(); break;
        }
    });

    video.play().catch(function() { player.classList.remove('playing'); });
}

// ============================================
// TOAST УВЕДОМЛЕНИЯ
// ============================================
function showToast(message, type) {
    var existing = document.querySelectorAll('.toast');
    existing.forEach(function(t) { t.remove(); });

    var toast = document.createElement('div');
    toast.className = 'toast toast-' + (type || 'info');
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(function() { toast.classList.add('show'); }, 10);
    setTimeout(function() {
        toast.classList.remove('show');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

// ============================================
// ИНДИКАТОР ЗАГРУЗКИ ВИДЕО
// ============================================
function initVideoUploadProgress() {
    var uploadForm = document.getElementById('uploadForm');
    var uploadBtn = document.getElementById('uploadBtn');
    var progressDiv = document.getElementById('upload-progress');

    if (!uploadForm || !uploadBtn || !progressDiv) return;

    uploadForm.addEventListener('submit', function(e) {
        var videoInput = document.getElementById('videoInput');
        if (videoInput && videoInput.files.length > 0) {
            progressDiv.style.display = 'block';
            uploadBtn.disabled = true;
            uploadBtn.textContent = '⏳ Загрузка...';
            setTimeout(function() {
                progressDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    });
}

// ============================================
// УДАЛЕНИЕ КОММЕНТАРИЯ
// ============================================
function initDeleteComment() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-delete-comment');
        if (!btn) return;
        e.preventDefault();

        if (!confirm('Удалить комментарий?')) return;

        var url = btn.dataset.url;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                var comment = document.getElementById('comment-' + data.comment_id);
                if (comment) {
                    comment.classList.add('deleting');
                    setTimeout(function() {
                        comment.remove();
                        var countEl = document.getElementById('comments-count');
                        if (countEl) countEl.textContent = parseInt(countEl.textContent) - 1;
                        var list = document.getElementById('comments-list');
                        if (list && list.children.length === 0) {
                            list.innerHTML = '<p class="empty-hint">// Пусто</p>';
                        }
                    }, 300);
                    showToast('Комментарий удалён', 'info');
                }
            } else {
                showToast('Ошибка удаления', 'danger');
            }
        })
        .catch(function(err) {
            console.error(err);
            showToast('Ошибка', 'danger');
        });
    });
}

// ============================================
// ВЫБОР КАЧЕСТВА ВИДЕО
// ============================================
function initQualitySelector() {
    var qualityMenu = document.getElementById('qualityMenu');
    var qualityBtn = document.getElementById('qualityBtn');
    var video = document.getElementById('videoElement');

    if (!qualityMenu || !qualityBtn || !video) return;

    var qualityBtns = qualityMenu.querySelectorAll('button');

    if (qualityBtns.length > 0) {
        qualityBtns[0].classList.add('active');
        qualityBtn.textContent = '⚙️ ' + qualityBtns[0].dataset.quality;
    }

    qualityBtns.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();

            var quality = this.dataset.quality;
            var url = this.dataset.url;
            var currentTime = video.currentTime;
            var wasPlaying = !video.paused;

            video.src = url;
            video.load();

            video.addEventListener('loadedmetadata', function() {
                video.currentTime = currentTime;
                if (wasPlaying) video.play();
            }, { once: true });

            qualityBtns.forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            qualityBtn.textContent = '⚙️ ' + quality;
            showToast('Качество: ' + quality, 'info');
        });
    });
}

// ============================================
// РЕАКЦИИ НА КОММЕНТАРИИ
// ============================================
function initCommentReactions() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.comment-react-btn');
        if (!btn) return;
        e.preventDefault();

        var url = btn.dataset.url;
        var commentId = btn.dataset.commentId;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                var block = document.getElementById('comment-' + commentId);
                if (!block) return;

                var likeBtn = block.querySelector('.like-btn');
                var dislikeBtn = block.querySelector('.dislike-btn');

                if (likeBtn) {
                    likeBtn.classList.remove('active');
                    likeBtn.querySelector('.like-count').textContent = data.likes;
                }
                if (dislikeBtn) {
                    dislikeBtn.classList.remove('active');
                    dislikeBtn.querySelector('.dislike-count').textContent = data.dislikes;
                }

                if (data.user_reaction === 'like' && likeBtn) likeBtn.classList.add('active');
                else if (data.user_reaction === 'dislike' && dislikeBtn) dislikeBtn.classList.add('active');
            }
        })
        .catch(function(err) { console.error(err); });
    });
}

// ============================================
// ОТВЕТЫ НА КОММЕНТАРИИ
// ============================================
function initCommentReplies() {
    // Показать/скрыть форму ответа
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.comment-reply-toggle');
        if (!btn) return;

        var commentId = btn.dataset.commentId;
        var formWrap = document.getElementById('reply-form-' + commentId);

        if (formWrap) {
            var isVisible = formWrap.style.display !== 'none';
            formWrap.style.display = isVisible ? 'none' : 'block';
            if (!isVisible) {
                var input = formWrap.querySelector('.reply-input');
                if (input) input.focus();
            }
        }
    });

    // Отправка ответа
    document.addEventListener('submit', function(e) {
        var form = e.target.closest('.reply-form');
        if (!form) return;
        e.preventDefault();

        if (!form.dataset.commentId) return;

        var input = form.querySelector('.reply-input');
        var text = input ? input.value.trim() : '';
        var url = form.dataset.url;
        var commentId = form.dataset.commentId;

        if (!text) return;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                var repliesList = document.getElementById('replies-' + commentId);
                if (repliesList) {
                    var html = '<div class="reply" id="reply-' + data.reply.id + '">' +
                        '<div class="comment-body">' +
                        '<div class="comment-header">' +
                        '<span class="c-author">' + escapeHtml(data.reply.author.username) + '</span>' +
                        '<span class="c-date">' + data.reply.created_at + '</span>' +
                        '</div>' +
                        '<span class="c-text">' + escapeHtml(data.reply.text) + '</span>' +
                        '</div>' +
                        '</div>';
                    repliesList.insertAdjacentHTML('beforeend', html);
                }

                if (input) input.value = '';
                var formWrap = document.getElementById('reply-form-' + commentId);
                if (formWrap) formWrap.style.display = 'none';

                var toggleBtn = document.querySelector('.comment-reply-toggle[data-comment-id="' + commentId + '"]');
                if (toggleBtn) {
                    var count = repliesList ? repliesList.children.length : 1;
                    toggleBtn.textContent = '💬 Ответить (' + count + ')';
                }

                showToast('Ответ добавлен!', 'success');
            }
        })
        .catch(function(err) {
            console.error(err);
            showToast('Ошибка отправки', 'danger');
        });
    });
}

// ============================================
// УДАЛЕНИЕ ОТВЕТА
// ============================================
function initDeleteReply() {
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-delete-reply');
        if (!btn) return;
        e.preventDefault();

        if (!confirm('Удалить ответ?')) return;

        var url = btn.dataset.url;
        var replyId = btn.dataset.replyId;

        fetch(url, {
            method: 'POST',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json' }
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.success) {
                var reply = document.getElementById('reply-' + data.reply_id);
                if (reply) {
                    reply.classList.add('deleting');
                    setTimeout(function() { reply.remove(); }, 300);
                }
                showToast('Ответ удалён', 'info');
            }
        })
        .catch(function(err) {
            console.error(err);
            showToast('Ошибка', 'danger');
        });
    });
}