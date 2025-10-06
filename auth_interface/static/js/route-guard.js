/**
 * Route Guard
 * Protects routes and ensures proper authentication
 * 
 * @module RouteGuard
 * @version 1.0.0
 */

'use strict';

/**
 * Route Guard Class
 * Manages route protection and authentication checks
 */
class RouteGuard {
  constructor(authService) {
    this.authService = authService;
    this.protectedRoutes = [
      '/templates/dashboard.html',
      '/dashboard.html',
      '/templates/profile.html',
      '/profile.html'
    ];
    this.publicRoutes = [
      '/templates/login.html',
      '/login.html',
      '/templates/register.html',
      '/register.html',
      '/templates/index.html',
      '/index.html',
      '/'
    ];
  }

  /**
   * Initialize route guard
   */
  init() {
    console.log('[RouteGuard] Initializing');
    
    // Check current route on page load
    this.checkCurrentRoute();
    
    // Intercept navigation
    this.interceptNavigation();
    
    // Handle browser back/forward
    window.addEventListener('popstate', () => {
      this.checkCurrentRoute();
    });
  }

  /**
   * Check if current route requires authentication
   */
  checkCurrentRoute() {
    const currentPath = window.location.pathname;
    console.log('[RouteGuard] Checking route:', currentPath);
    
    if (this.isProtectedRoute(currentPath)) {
      if (!this.authService.isAuthenticated()) {
        console.log('[RouteGuard] Unauthorized access to protected route');
        this.redirectToLogin();
        return false;
      }
      console.log('[RouteGuard] Access granted to protected route');
    } else if (this.isPublicRoute(currentPath)) {
      // If user is authenticated and tries to access login/register, redirect to dashboard
      if ((currentPath.includes('login') || currentPath.includes('register')) && 
          this.authService.isAuthenticated()) {
        console.log('[RouteGuard] Authenticated user accessing public route, redirecting to dashboard');
        this.redirectToDashboard();
        return false;
      }
    }
    
    return true;
  }

  /**
   * Check if route is protected
   * @param {string} path - Route path
   * @returns {boolean} Whether route is protected
   */
  isProtectedRoute(path) {
    return this.protectedRoutes.some(route => path.includes(route));
  }

  /**
   * Check if route is public
   * @param {string} path - Route path
   * @returns {boolean} Whether route is public
   */
  isPublicRoute(path) {
    return this.publicRoutes.some(route => path === route || path.endsWith(route));
  }

  /**
   * Intercept link clicks for navigation
   */
  interceptNavigation() {
    document.addEventListener('click', (event) => {
      const target = event.target.closest('a');
      
      if (!target) return;
      
      const href = target.getAttribute('href');
      
      if (!href || href.startsWith('#') || href.startsWith('http')) return;
      
      // Check if link is to a protected route
      if (this.isProtectedRoute(href)) {
        if (!this.authService.isAuthenticated()) {
          event.preventDefault();
          console.log('[RouteGuard] Blocked navigation to protected route');
          this.redirectToLogin();
        }
      }
    });
  }

  /**
   * Redirect to login page
   */
  redirectToLogin() {
    const currentPath = window.location.pathname;
    const returnUrl = encodeURIComponent(currentPath);
    
    console.log('[RouteGuard] Redirecting to login');
    
    // Store return URL for after login
    sessionStorage.setItem('returnUrl', currentPath);
    
    // Show message
    this.showMessage('Please log in to access this page', 'warning');
    
    // Redirect
    setTimeout(() => {
      window.location.href = `/templates/login.html?returnUrl=${returnUrl}`;
    }, 1000);
  }

  /**
   * Redirect to dashboard
   */
  redirectToDashboard() {
    console.log('[RouteGuard] Redirecting to dashboard');
    window.location.href = '/templates/dashboard.html';
  }

  /**
   * Redirect to return URL after login
   */
  redirectToReturnUrl() {
    const returnUrl = sessionStorage.getItem('returnUrl');
    sessionStorage.removeItem('returnUrl');
    
    if (returnUrl && returnUrl !== '/templates/login.html') {
      console.log('[RouteGuard] Redirecting to return URL:', returnUrl);
      window.location.href = returnUrl;
    } else {
      this.redirectToDashboard();
    }
  }

  /**
   * Show message to user
   * @param {string} message - Message text
   * @param {string} type - Message type (success, warning, danger)
   */
  showMessage(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10000;
      max-width: 90%;
      width: 400px;
      animation: slideDown 0.3s ease;
    `;
    alert.innerHTML = `
      <span>${message}</span>
    `;
    
    document.body.appendChild(alert);
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideDown {
        from {
          opacity: 0;
          transform: translateX(-50%) translateY(-20px);
        }
        to {
          opacity: 1;
          transform: translateX(-50%) translateY(0);
        }
      }
    `;
    document.head.appendChild(style);
    
    // Remove after 3 seconds
    setTimeout(() => {
      alert.style.animation = 'slideUp 0.3s ease';
      setTimeout(() => alert.remove(), 300);
    }, 3000);
  }

  /**
   * Guard a function call with authentication check
   * @param {Function} fn - Function to guard
   * @returns {Function} Guarded function
   */
  guard(fn) {
    return (...args) => {
      if (!this.authService.isAuthenticated()) {
        console.log('[RouteGuard] Function call blocked - not authenticated');
        this.redirectToLogin();
        return;
      }
      return fn(...args);
    };
  }

  /**
   * Check if user has required role/permission
   * @param {string|string[]} requiredRoles - Required role(s)
   * @returns {boolean} Whether user has required role
   */
  hasRole(requiredRoles) {
    const user = this.authService.getCurrentUser();
    
    if (!user || !user.roles) return false;
    
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];
    
    return roles.some(role => user.roles.includes(role));
  }

  /**
   * Guard route with role requirement
   * @param {string|string[]} requiredRoles - Required role(s)
   * @returns {boolean} Whether access is granted
   */
  requireRole(requiredRoles) {
    if (!this.authService.isAuthenticated()) {
      this.redirectToLogin();
      return false;
    }
    
    if (!this.hasRole(requiredRoles)) {
      console.log('[RouteGuard] Access denied - insufficient permissions');
      this.showMessage('You do not have permission to access this page', 'danger');
      setTimeout(() => {
        this.redirectToDashboard();
      }, 2000);
      return false;
    }
    
    return true;
  }
}

/**
 * Create route guard instance
 * Will be initialized when authService is available
 */
let routeGuard = null;

/**
 * Initialize route guard when DOM is ready
 */
function initRouteGuard() {
  if (typeof authService !== 'undefined') {
    routeGuard = new RouteGuard(authService);
    routeGuard.init();
    console.log('[RouteGuard] Initialized with authService');
  } else {
    console.warn('[RouteGuard] authService not found, retrying...');
    setTimeout(initRouteGuard, 100);
  }
}

// Initialize when page loads
if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRouteGuard);
  } else {
    initRouteGuard();
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { RouteGuard, routeGuard };
}
