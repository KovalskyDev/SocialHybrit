function toggleComments(postId) {
    const section = document.getElementById('comments-section-' + postId);
    if (!section) return;
    section.style.display = (section.style.display === 'none' || section.style.display === '') ? 'block' : 'none';
}

document.addEventListener("DOMContentLoaded", function() {
    // 1. Обработка якоря (если перешли по ссылке на конкретный пост)
    const hash = window.location.hash;
    if (hash && hash.startsWith('#post-')) {
        const postId = hash.replace('#post-', '');
        toggleComments(postId);
        const element = document.getElementById('post-' + postId);
        if (element) element.scrollIntoView();
    }

    // 2. Единый слушатель кликов для кнопок "ще/приховати"
    document.addEventListener('click', function(e) {
        // Нажали "ще"
        if (e.target.classList.contains('read-more-btn')) {
            const container = e.target.closest('.post-caption');
            container.querySelector('.about-short').classList.add('d-none');
            container.querySelector('.about-full').classList.remove('d-none');
        }
        
        // Нажали "приховати"
        if (e.target.classList.contains('read-less-btn')) {
            const container = e.target.closest('.post-caption');
            container.querySelector('.about-full').classList.add('d-none');
            container.querySelector('.about-short').classList.remove('d-none');
            
            // Скроллим обратно к началу поста, чтобы не потеряться
            container.closest('.post-item').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    });

    // 3. Лайк двойным кликом
    document.querySelectorAll('.media-wrapper').forEach(wrapper => {
        wrapper.addEventListener('dblclick', function(e) {
            // Убираем выделение текста при быстром клике
            window.getSelection().removeAllRanges();
            
            const heart = this.querySelector('.like-heart-pop');
            heart.classList.remove('animate');
            void heart.offsetWidth; // Магия для перезапуска анимации
            heart.classList.add('animate');
            
            const card = this.closest('.card');
            const likeForm = card.querySelector('.like-form');
            const actionInput = card.querySelector('.like-action-input');
            
            if (actionInput) actionInput.value = 'like_only';
            
            // Отправляем форму через 400мс (чтобы сердце успело мелькнуть)
            setTimeout(() => { if(likeForm) likeForm.submit(); }, 400);
        });
    });
});

document.addEventListener('input', function (e) {
    if (e.target.classList.contains('comment-textarea')) {
        const textarea = e.target;
        
        // Сбрасываем высоту, чтобы она могла уменьшиться при удалении текста
        textarea.style.height = 'auto';
        
        // Устанавливаем новую высоту равную высоте контента внутри (scrollHeight)
        const newHeight = textarea.scrollHeight;
        textarea.style.height = newHeight + 'px';
        
        // Если текста слишком много, включаем скролл
        if (newHeight > 150) {
            textarea.style.overflowY = 'auto';
        } else {
            textarea.style.overflowY = 'hidden';
        }
    }
});

// Обработка отправки по Enter (необязательно, но удобно)
document.addEventListener('keydown', function(e) {
    if (e.target.classList.contains('comment-textarea') && e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Запрещаем перенос строки
        const form = e.target.closest('form');
        if (e.target.value.trim() !== "") {
            form.submit(); // Отправляем форму
        }
    }
});