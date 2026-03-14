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

// 3. Функция переключения видимости комментов
function toggleComments(postId) {
    const section = document.getElementById('comments-section-' + postId);
    if (!section) return;
    section.style.display = (section.style.display === 'none' || section.style.display === '') ? 'block' : 'none';
}

// 4. ГЛАВНАЯ ИНИЦИАЛИЗАЦИЯ
document.addEventListener("DOMContentLoaded", function() {
    console.log("SocialHybrit JS: Full System Initialized");

    let page = 1;
    let emptyPage = false;
    let blockRequest = false;

    const sentinel = document.getElementById('loading-sentinel');
    const container = document.getElementById('post-container');
    const loader = document.getElementById('loader');

    // --- БЕСКОНЕЧНЫЙ СКРОЛЛ ---
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && !blockRequest && !emptyPage) {
            loadMorePosts();
        }
    }, { threshold: 0.1, rootMargin: "200px" });

    if (sentinel) observer.observe(sentinel);

    async function loadMorePosts() {
        blockRequest = true;
        page++;
        if (loader) loader.classList.remove('d-none');

        try {
            const response = await fetch(`?page=${page}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            });
            if (!response.ok) { emptyPage = true; return; }
            const data = await response.json();

            if (!data.html || data.html.trim() === "") {
                emptyPage = true;
            } else {
                container.insertAdjacentHTML('beforeend', data.html);
                if (!data.has_next) emptyPage = true;
                else setTimeout(() => { blockRequest = false; }, 200);
            }
        } catch (e) {
            console.error("Pagination error:", e);
            blockRequest = false;
        } finally {
            if (loader) loader.classList.add('d-none');
        }
    }

    // --- ФУНКЦИЯ ОТПРАВКИ КОММЕНТАРИЯ (AJAX) ---
    async function handleCommentSubmit(form) {
        const url = form.action;
        const formData = new FormData(form);
        const postItem = form.closest('.post-item');
        const replyList = postItem.querySelector('.replies-list');
        const textarea = form.querySelector('textarea');
        const submitBtn = form.querySelector('button[type="submit"]');

        if (!textarea.value.trim()) return;
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
                
                // Убираем заглушку "Нет комментов"
                const emptyMsg = replyList.querySelector('p.text-muted');
                if (emptyMsg) emptyMsg.remove();

                // Создаем HTML нового коммента с анимацией
                const newReplyHtml = `
                    <div class="reply-item d-flex justify-content-between align-items-start mb-2" style="opacity: 0; transform: translateX(-10px); transition: all 0.3s ease;">
                        <div style="min-width: 0;">
                            <span class="fw-bold me-1 small">${data.username}</span>
                            <span class="text-muted ms-1" style="font-size: 0.85rem;">now</span>
                            <span class="small reply-text d-block">${data.text}</span>
                        </div>
                        <a href="/replies/${data.pk}/delete/" class="delete-reply-btn text-muted ms-2 no-select">
                            <i class="bi bi-trash"></i>
                        </a>
                    </div>`;
                
                replyList.insertAdjacentHTML('beforeend', newReplyHtml);
                
                // Запуск анимации появления
                const newElem = replyList.lastElementChild;
                setTimeout(() => {
                    newElem.style.opacity = '1';
                    newElem.style.transform = 'translateX(0)';
                }, 10);

                form.reset();
                textarea.style.height = 'auto';
            }
        } catch (error) {
            console.error('Comment error:', error);
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    }

    // --- ДЕЛЕГИРОВАНИЕ ВСЕХ СОБЫТИЙ КЛИКА ---
    document.addEventListener('click', async function(e) {
        // 1. Кнопка "Читать далее"
        if (e.target.classList.contains('read-more-btn')) {
            const p = e.target.closest('.post-caption');
            p.querySelector('.about-short').classList.add('d-none');
            p.querySelector('.about-full').classList.remove('d-none');
        }
        
        // 2. Кнопка "Скрыть"
        if (e.target.classList.contains('read-less-btn')) {
            const p = e.target.closest('.post-caption');
            p.querySelector('.about-full').classList.add('d-none');
            p.querySelector('.about-short').classList.remove('d-none');
            p.closest('.post-item').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        // 3. Кнопка УДАЛЕНИЯ комментария (AJAX)
        const deleteBtn = e.target.closest('.delete-reply-btn');
        if (deleteBtn) {
            e.preventDefault();
            e.stopImmediatePropagation(); // Защита от двойного окна

            if (!confirm('Видалити цей коментар?')) return;

            const url = deleteBtn.href;
            const replyItem = deleteBtn.closest('.reply-item');

            try {
                const response = await fetch(url, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                if (response.ok) {
                    replyItem.style.transition = 'all 0.4s ease';
                    replyItem.style.opacity = '0';
                    replyItem.style.transform = 'translateX(30px)';
                    setTimeout(() => { replyItem.remove(); }, 400);
                }
            } catch (err) { console.error('Delete error:', err); }
        }
    });

    // --- ОБРАБОТКА ФОРМ (ДОБАВЛЕНИЕ КОММЕНТА) ---
    document.addEventListener('submit', function(e) {
        // Ищем форму по классу ajax-reply-form
        const form = e.target.closest('.ajax-reply-form') || (e.target.action && e.target.action.includes('create'));
        if (form && typeof form !== 'string') {
            e.preventDefault();
            e.stopImmediatePropagation();
            handleCommentSubmit(e.target);
        }
    });

    // Двойной клик (Лайк)
    document.addEventListener('dblclick', function(e) {
        const wrapper = e.target.closest('.media-wrapper');
        if (wrapper) {
            window.getSelection().removeAllRanges();
            const heart = wrapper.querySelector('.like-heart-pop');
            if (heart) {
                heart.classList.remove('animate');
                void heart.offsetWidth;
                heart.classList.add('animate');
            }
            const card = wrapper.closest('.post-item');
            const form = card.querySelector('.ajax-like-form');
            const input = card.querySelector('.like-action-input');
            if (form && input) {
                input.value = 'like_only';
                sendLikeRequest(form).then(() => { input.value = 'toggle'; });
            }
        }
    });

    // Авто-высота textarea
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('comment-textarea')) {
            e.target.style.height = 'auto';
            e.target.style.height = (e.target.scrollHeight) + 'px';
        }
    });

    // Отправка по Enter (без Shift)
    document.addEventListener('keydown', function(e) {
        if (e.target.classList.contains('comment-textarea') && e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            const form = e.target.closest('form');
            if (e.target.value.trim() !== "") {
                handleCommentSubmit(form);
            }
        }
    });
});