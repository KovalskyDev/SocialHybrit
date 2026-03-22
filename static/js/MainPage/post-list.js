// 1. Получение CSRF-токена
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 2. Универсальная AJAX функция для лайка
async function sendLikeRequest(form) {
    if (!form) return;
    const url = form.getAttribute('action');
    const formData = new FormData(form);
    const postId = form.dataset.postId;
    const countSpan = document.getElementById(`likes-count-${postId}`);
    const btn = form.querySelector('.like-button');

    if (countSpan) countSpan.classList.add('updating');

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });
        const data = await response.json();
        setTimeout(() => {
            if (countSpan) {
                countSpan.innerText = data.likes_count;
                countSpan.classList.remove('updating');
            }
            if (btn) {
                btn.innerHTML = data.liked 
                    ? '<i class="bi bi-heart-fill fs-4 text-danger"></i>' 
                    : '<i class="bi bi-heart fs-4 hover-red"></i>';
            }
        }, 100);
    } catch (error) {
        if (countSpan) countSpan.classList.remove('updating');
        console.error('Ошибка лайка:', error);
    }
}


// 3. AJAX функция для избранного
async function sendFavoriteRequest(form) {
    if (!form) return;

    const url = form.getAttribute('action');
    const btn = form.querySelector('.favorite-button');

    btn.disabled = true;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest', 
                'X-CSRFToken': getCookie('csrftoken'), 
            }
        });

        if (!response.ok) throw new Error('Ошибка сети');

        const data = await response.json(); 

        if (data.favourited) {
            btn.innerHTML = '<i class="bi bi-bookmark-fill fs-4 fav-icon"></i>';
        } else {
            btn.innerHTML = '<i class="bi bi-bookmark fs-4 fav-icon"></i>';
        }
    } catch (error) {
        console.error('Ошибка добавления в избранное:', error);
    } finally {
        btn.disabled = false; 
    }
}

// 4. Функция переключения видимости комментов
function toggleComments(postId) {
    const section = document.getElementById('comments-section-' + postId);
    if (!section) return;
    section.style.display = (section.style.display === 'none' || section.style.display === '') ? 'block' : 'none';
}

// Функция плавного обновления чисел
function updateValueWithAnim(el, newValue) {
    if (el && el.innerText != newValue) {
        el.style.transition = "opacity 0.2s ease";
        el.style.opacity = "0"; 
        setTimeout(() => {
            el.innerText = newValue;
            el.style.opacity = "1";
        }, 200);
    }
}

// --- 4. ГЛАВНАЯ ИНИЦИАЛИЗАЦИЯ ---
document.addEventListener("DOMContentLoaded", function() {
    console.log("SocialHybrit JS: Full System Initialized");
    
    let lastCheckTime = new Date().toISOString();
    let page = 1;
    let emptyPage = false;
    let blockRequest = false;

    const sentinel = document.getElementById('loading-sentinel');
    const container = document.getElementById('post-container');
    const loader = document.getElementById('loader');
    const endOfFeed = document.getElementById('end-of-feed');

    // --- РЕАЛТАЙМ ОБНОВЛЕНИЯ (HEARTBEAT) ---
    async function startSocialHeartbeat() {
        setInterval(async () => {
            if (document.hidden) return;

            const postElements = document.querySelectorAll('.post-item');
            const ids = Array.from(postElements).map(el => el.dataset.postId).filter(id => id);
            if (ids.length === 0) return;

            try {
                const response = await fetch(`/api/get_updates/?ids=${ids.join(',')}&last_check=${lastCheckTime}`);
                if (!response.ok) return;
                const data = await response.json();
                
                // 1. ЛОГИКА УДАЛЕНИЯ ПОСТОВ
                ids.forEach(id => {
                    if (!data.stats[id]) { 
                        const postEl = document.getElementById(`post-${id}`);
                        if (postEl && !postEl.classList.contains('is-deleted')) {
                            postEl.style.height = postEl.offsetHeight + 'px';
                            postEl.classList.add('is-deleted');
                            postEl.innerHTML = `
                                <div class="deleted-post-placeholder text-center p-4">
                                    <i class="bi bi-trash3 fs-2 mb-2"></i>
                                    <p class="fw-bold mb-0">Цей пост був видалений</p>
                                </div>`;
                        }
                    }
                });

                lastCheckTime = new Date().toISOString();

                // 2. ВСТАВКА НОВЫХ КОММЕНТАРИЕВ
                for (const [postId, html] of Object.entries(data.new_replies)) {
                    const list = document.querySelector(`#comments-section-${postId} .replies-list`);
                    if (list) {
                        const emptyMsg = list.querySelector('.empty-replies-msg');
                        if (emptyMsg) emptyMsg.remove();
                        
                        list.insertAdjacentHTML('beforeend', html);
                        
                        list.querySelectorAll('.reply-item[style*="opacity: 0"]').forEach(el => {
                            setTimeout(() => { 
                                el.style.opacity = '1'; 
                                el.style.transform = 'translateX(0)'; 
                            }, 50);
                        });
                    }
                }

                // 3. ОБНОВЛЕНИЕ СЧЕТЧИКОВ И ТИХАЯ ЧИСТКА КОММЕНТОВ
                for (const [id, stat] of Object.entries(data.stats)) {
                    const lCount = document.getElementById(`likes-count-${id}`);
                    const rCount = document.getElementById(`replies-count-${id}`);
                    if (lCount) updateValueWithAnim(lCount, stat.likes);
                    if (rCount) updateValueWithAnim(rCount, stat.replies);

                    // Тихая синхронизация списка комментов (только если плашка закрыта)
                    const section = document.getElementById('comments-section-' + id);
                    if (section && (section.style.display === 'none' || section.style.display === '')) {
                        const list = section.querySelector('.replies-list');
                        if (list && stat.active_replies) {
                            const currentItems = list.querySelectorAll('.reply-item');
                            currentItems.forEach(reply => {
                                if (!reply.id) return;
                                const rId = parseInt(reply.id.replace('reply-', '')); 
                                if (!isNaN(rId) && !stat.active_replies.includes(rId)) {
                                    reply.remove();
                                }
                            });

                            // Возвращаем заглушку, только если реально всё удалилось
                            if (list.querySelectorAll('.reply-item').length === 0 && !list.querySelector('.empty-replies-msg')) {
                                list.innerHTML = '<p class="empty-replies-msg small text-muted text-center py-2">Ще немає коментарів...</p>';
                            }
                        }
                    }
                }
            } catch (e) { console.error("Heartbeat error:", e); }
        }, 3000);
    }

    startSocialHeartbeat();

    // --- БЕСКОНЕЧНЫЙ СКРОЛЛ ---
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !blockRequest && !emptyPage) loadMorePosts();
    }, { threshold: 0.1, rootMargin: "200px" });

    if (sentinel) observer.observe(sentinel);

    async function loadMorePosts() {
        blockRequest = true;
        page++;
        if (loader) loader.classList.remove('d-none');
        try {
            const response = await fetch(`?page=${page}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
            const data = await response.json();
            
            if (!data.html || data.html.trim() === "") {
                stopScrolling(); // Вызываем остановку
            } else {
                container.insertAdjacentHTML('beforeend', data.html);
                if (!data.has_next) {
                    stopScrolling(); // Вызываем остановку
                } else {
                    setTimeout(() => { blockRequest = false; }, 100);
                }
            }
        } catch (e) { blockRequest = false; } finally {
            if (loader) loader.classList.add('d-none');
        }
    }

    function stopScrolling() {
        emptyPage = true;
        if (sentinel) {
            observer.unobserve(sentinel); // Отключаем слежку, экономим ресурсы браузера
            sentinel.remove(); // Вообще удаляем зону загрузки
        }
        if (endOfFeed) {
            endOfFeed.classList.remove('d-none');
            // Небольшая задержка для плавного появления
            setTimeout(() => { endOfFeed.style.opacity = '1'; }, 2500);
        }
    }

    // --- ОТПРАВКА КОММЕНТАРИЯ ---
    async function handleCommentSubmit(form) {
        const url = form.action;
        const formData = new FormData(form);
        const replyList = form.closest('.post-item').querySelector('.replies-list');
        const textarea = form.querySelector('textarea');
        const submitBtn = form.querySelector('button[type="submit"]');

        if (!textarea.value.trim() || (submitBtn && submitBtn.disabled)) return;
        if (submitBtn) submitBtn.disabled = true;

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            if (response.ok) {
                const data = await response.json();
                const emptyMsg = replyList.querySelector('.empty-replies-msg');
                if (emptyMsg) emptyMsg.remove();


                replyList.insertAdjacentHTML('beforeend', data.html);

                // Анимация (находим последний добавленный элемент)
                const newEl = replyList.lastElementChild;
                setTimeout(() => {
                    newEl.style.opacity = '1';
                    newEl.style.transform = 'translateX(0)';
                }, 3);

                form.reset();
                textarea.style.height = 'auto';
                lastCheckTime = new Date().toISOString();
            }
        } catch (error) { console.error('Comment error:', error); } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    }

    // --- ДЕЛЕГИРОВАНИЕ ---
    document.addEventListener('click', async function(e) {
        const target = e.target;
        
        // Свернуть/развернуть текст
        if (target.classList.contains('read-more-btn') || target.classList.contains('read-less-btn')) {
            const p = target.closest('.post-caption');
            p.querySelector('.about-short').classList.toggle('d-none');
            p.querySelector('.about-full').classList.toggle('d-none');
            if (target.classList.contains('read-less-btn')) {
                p.closest('.post-item').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        // Удаление коммента
        const deleteBtn = target.closest('.delete-reply-btn');
        if (deleteBtn) {
            e.preventDefault();
            if (!confirm('Видалити цей коментар?')) return;
            const replyItem = deleteBtn.closest('.reply-item');
            const csrfToken = getCookie('csrftoken');
            
            try {
                const response = await fetch(deleteBtn.href, { 
                    method: "POST",
                    headers: { 
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken 
                    }
                });
                if (response.ok) {
                    replyItem.style.opacity = '0';
                    replyItem.style.transform = 'translateX(30px)';
                    setTimeout(() => { replyItem.remove(); }, 400);
                }
            } catch (err) { console.error('Delete error:', err); }
        }
    });

    document.addEventListener('submit', function(e) {
        const form = e.target.closest('.ajax-reply-form');
        if (form) { e.preventDefault(); handleCommentSubmit(form); }
    });

    document.addEventListener('dblclick', function(e) {
        const wrapper = e.target.closest('.media-wrapper');
        if (wrapper) {
            window.getSelection().removeAllRanges();
            const heart = wrapper.querySelector('.like-heart-pop');
            if (heart) { heart.classList.remove('animate'); void heart.offsetWidth; heart.classList.add('animate'); }
            const card = wrapper.closest('.post-item');
            const form = card.querySelector('.ajax-like-form');
            const input = card.querySelector('.like-action-input');
            if (form && input) {
                input.value = 'like_only';
                sendLikeRequest(form).then(() => { input.value = 'toggle'; });
            }
        }
    });

    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('comment-textarea')) {
            e.target.style.height = 'auto';
            e.target.style.height = (e.target.scrollHeight) + 'px';
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.target.classList.contains('comment-textarea') && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleCommentSubmit(e.target.closest('form'));
        }
    });
});