/**
 * Получить значение cookie по имени
 */
export function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop().split(';').shift();
  }
  return null;
}

/**
 * Установить cookie
 */
export function setCookie(name, value, days = 30) {
  const expires = new Date();
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
  document.cookie = `${name}=${value}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
}

/**
 * Удалить cookie
 */
export function deleteCookie(name) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

/**
 * Выход из аккаунта (удаление всех auth cookies)
 */
export function logout() {
  deleteCookie('user_id');
  deleteCookie('yandex_token');
  localStorage.removeItem('yandex_token');
}

