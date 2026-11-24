export function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

export function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = '/src/pages/login.html';
  }
}

export function logout() {
  localStorage.removeItem('access_token');
  window.location.href = '/src/pages/login.html';
}