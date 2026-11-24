import { requireAuth, logout } from '../utils/auth.js';
console.log('groups.js загружен');
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('logout-btn');
  if (btn) {
    btn.addEventListener('click', logout);
  }
});