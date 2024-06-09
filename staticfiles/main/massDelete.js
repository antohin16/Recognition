function deleteSelectedReadings() {
    const checkboxes = document.querySelectorAll('input[name="delete-checkbox"]:checked');
    const ids = Array.from(checkboxes).map(checkbox => checkbox.value);

    fetch('/delete-readings/', {
        method: 'POST',
        body: JSON.stringify({ ids }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Выбранные записи успешно удалены.');
            window.location.reload();
        } else {
            alert('Ошибка при удалении записей.');
        }
    })
    .catch(error => console.error('Ошибка:', error));
}

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
