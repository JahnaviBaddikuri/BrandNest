/* ===========================
   JWT AUTHENTICATION 
   =========================== */

const API_BASE = "http://localhost:5000/api";

// Utility Functions
function showMessage(elementId, message, type = 'error') {
  const messageEl = document.getElementById(elementId);
  if (messageEl) {
    messageEl.textContent = message;
    messageEl.classList.add('show', type);
    messageEl.classList.remove(type === 'error' ? 'success' : 'error');
    
    if (type === 'success') {
      setTimeout(() => {
        messageEl.classList.remove('show');
      }, 3000);
    }
  }
}

function clearErrors() {
  const errorElements = document.querySelectorAll('.error-message');
  errorElements.forEach(el => {
    el.textContent = '';
  });
  
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(el => {
    el.classList.remove('error');
  });
}

function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

function validatePassword(password) {
  return password.length >= 6;
}

async function uploadProfileImage(file) {
  if (!file) {
    return '';
  }

  console.log(' Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);

  const payload = new FormData();
  payload.append('file', file);

  console.log(' FormData created, sending to backend...');

  const response = await fetch(`${API_BASE}/creators/upload-profile`, {
    method: 'POST',
    body: payload,
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.message || 'Failed to upload image');
  }

  return result.data?.url || '';
}

async function uploadBrandLogo(file) {
  if (!file) {
    return '';
  }

  console.log(' Uploading brand logo:', file.name, 'Size:', file.size, 'Type:', file.type);

  const payload = new FormData();
  payload.append('file', file);

  console.log(' FormData created, sending to backend...');

  const response = await fetch(`${API_BASE}/brands/upload-logo`, {
    method: 'POST',
    body: payload,
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.message || 'Failed to upload logo');
  }

  return result.data?.url || '';
}

function setFieldError(fieldName, message) {
  const errorEl = document.getElementById(`${fieldName}Error`);
  const inputEl = document.querySelector(`[name="${fieldName}"]`);
  
  if (errorEl) {
    errorEl.textContent = message;
  }
  if (inputEl) {
    inputEl.classList.add('error');
  }
}

// Session Management with JWT tokens
function saveUserSession(userData, token) {
  localStorage.setItem('collabstr_user', JSON.stringify(userData));
  localStorage.setItem('collabstr_token', token);
  localStorage.setItem('collabstr_logged_in', 'true');
}

function getUserSession() {
  const user = localStorage.getItem('collabstr_user');
  return user ? JSON.parse(user) : null;
}

function getAuthToken() {
  return localStorage.getItem('collabstr_token');
}

function clearUserSession() {
  localStorage.removeItem('collabstr_user');
  localStorage.removeItem('collabstr_token');
  localStorage.removeItem('collabstr_logged_in');
}

function isUserLoggedIn() {
  return localStorage.getItem('collabstr_logged_in') === 'true' && !!getAuthToken();
}

// Make authenticated API request with JWT token
async function authenticatedFetch(url, options = {}) {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };

  const response = await fetch(url, { ...options, headers });
  
  if (response.status === 401) {
    // Token expired or invalid
    clearUserSession();
    window.location.href = 'login.html';
    throw new Error('Session expired. Please log in again.');
  }

  return response;
}

function redirectIfLoggedIn(redirectPage = 'dashboard.html') {
  if (isUserLoggedIn()) {
    window.location.href = redirectPage;
  }
}

function requireLogin(redirectPage = 'login.html') {
  if (!isUserLoggedIn()) {
    window.location.href = redirectPage;
  }
}

// ==========================================
// LOGIN PAGE LOGIC
// ==========================================

function setupLoginPage() {
  const loginForm = document.getElementById('loginForm');
  const logoutBtn = document.getElementById('logoutBtn');
  const forgotPasswordLink = document.getElementById('forgotPasswordLink');

  if (loginForm) {
    redirectIfLoggedIn();
    
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearErrors();

      const email = document.getElementById('loginEmail').value.trim();
      const password = document.getElementById('loginPassword').value;
      const role = document.getElementById('userRole').value;

      // Validation
      let isValid = true;

      if (!validateEmail(email)) {
        setFieldError('email', 'Please enter a valid email address');
        isValid = false;
      }

      if (!validatePassword(password)) {
        setFieldError('password', 'Password must be at least 6 characters');
        isValid = false;
      }

      if (!role) {
        setFieldError('role', 'Please select your role');
        isValid = false;
      }

      if (!isValid) {
        return;
      }

      try {
        // Call JWT login endpoint
        const response = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password, role })
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || 'Login failed');
        }

        // Save JWT token and user data
        saveUserSession(result.data.user, result.data.token);
        showMessage('authMessage', 'Login successful! Redirecting...', 'success');

        setTimeout(() => {
          window.location.href = 'dashboard.html';
        }, 1200);
      } catch (error) {
        showMessage('authMessage', error.message || 'Login failed. Please try again.', 'error');
      }
    });
  }

  // Logout Logic
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      clearUserSession();
      window.location.href = 'index.html';
    });
  }

  // Forgot Password functionality (TODO: Implement backend support)
  if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', async (e) => {
      e.preventDefault();
      showMessage('authMessage', 'Password reset feature coming soon. Please contact support.', 'error');
    });
  }
}

// ==========================================
// CREATOR SIGNUP PAGE LOGIC
// ==========================================

function setupCreatorPage() {
  const creatorForm = document.getElementById('creatorForm');

  if (creatorForm) {
    redirectIfLoggedIn();

    creatorForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearErrors();

      const formData = new FormData(creatorForm);
      const profileImageInput = document.getElementById('profileImage');
      const profileImageFile = profileImageInput && profileImageInput.files
        ? profileImageInput.files[0]
        : null;
      
      console.log(' Profile image input:', profileImageInput);
      console.log(' Profile image file:', profileImageFile);
      
      const data = {
        email: formData.get('email'),
        password: formData.get('password'),
        username: formData.get('username'),
        platform: formData.get('platform'),
        category: formData.get('category'),
        rate: parseFloat(formData.get('rate')) || 0,
        location: formData.get('location'),
        bio: formData.get('bio'),
        followers_count: parseInt(formData.get('followers_count')) || 0,
        engagement_rate: parseFloat(formData.get('engagement_rate')) || 0,
        profile_image_url: '',
        is_verified: formData.get('is_verified') === 'on'
      };

      // Validation
      let isValid = true;

      if (!validateEmail(data.email)) {
        setFieldError('email', 'Please enter a valid email address');
        isValid = false;
      }

      if (!validatePassword(data.password)) {
        setFieldError('password', 'Password must be at least 6 characters');
        isValid = false;
      }

      if (!data.username.trim()) {
        setFieldError('username', 'Username is required');
        isValid = false;
      }

      if (!data.platform) {
        setFieldError('platform', 'Please select a platform');
        isValid = false;
      }

      if (!data.category) {
        setFieldError('category', 'Please select a category');
        isValid = false;
      }

      if (data.rate <= 0) {
        setFieldError('rate', 'Please enter a valid rate');
        isValid = false;
      }

      if (!isValid) {
        return;
      }

      try {
        // Step 1: Upload profile image if provided
        console.log(' About to upload image:', profileImageFile);
        data.profile_image_url = await uploadProfileImage(profileImageFile);
        console.log(' Image upload result:', data.profile_image_url);

        // Step 2: Register with JWT backend
        const response = await fetch(`${API_BASE}/auth/register/creator`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || 'Failed to create account');
        }

        // Step 3: Store temporary data and redirect to verification page
        sessionStorage.setItem('pending_verification', JSON.stringify({
          email: result.data.email,
          role: result.data.role
        }));

        showMessage('authMessage', 'Account created! Redirecting to verification...', 'success');

        setTimeout(() => {
          window.location.href = 'verify-email.html';
        }, 1200);
      } catch (error) {
        showMessage('authMessage', error.message || 'Failed to create account. Please try again.', 'error');
      }
    });
  }
}

// ==========================================
// BRAND SIGNUP PAGE LOGIC
// ==========================================

function setupBrandPage() {
  const brandForm = document.getElementById('brandForm');

  if (brandForm) {
    redirectIfLoggedIn();

    brandForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearErrors();

      const formData = new FormData(brandForm);
      const brandLogoInput = document.getElementById('brandLogo');
      const brandLogoFile = brandLogoInput && brandLogoInput.files
        ? brandLogoInput.files[0]
        : null;
      
      console.log('🏢 Brand logo input:', brandLogoInput);
      console.log('🏢 Brand logo file:', brandLogoFile);
      
      const data = {
        email: formData.get('email'),
        password: formData.get('password'),
        company_name: formData.get('company_name'),
        industry: formData.get('industry'),
        location: formData.get('location'),
        website: formData.get('website'),
        logo_url: '',
        verified: formData.get('verified') === 'on'
      };

      // Validation
      let isValid = true;

      if (!validateEmail(data.email)) {
        setFieldError('email', 'Please enter a valid email address');
        isValid = false;
      }

      if (!validatePassword(data.password)) {
        setFieldError('password', 'Password must be at least 6 characters');
        isValid = false;
      }

      if (!data.company_name.trim()) {
        setFieldError('companyName', 'Company name is required');
        isValid = false;
      }

      if (!data.industry) {
        setFieldError('industry', 'Please select an industry');
        isValid = false;
      }

      if (!isValid) {
        return;
      }

      try {
        // Step 1: Upload brand logo if provided
        console.log('🏢 About to upload brand logo:', brandLogoFile);
        data.logo_url = await uploadBrandLogo(brandLogoFile);
        console.log('🏢 Logo upload result:', data.logo_url);

        // Step 2: Register with JWT backend
        const response = await fetch(`${API_BASE}/auth/register/brand`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || 'Failed to create account');
        }

        // Step 3: Store temporary data and redirect to verification page
        sessionStorage.setItem('pending_verification', JSON.stringify({
          email: result.data.email,
          role: result.data.role
        }));

        showMessage('authMessage', 'Account created! Redirecting to verification...', 'success');

        setTimeout(() => {
          window.location.href = 'verify-email.html';
        }, 1200);
      } catch (error) {
        showMessage('authMessage', error.message || 'Failed to create account. Please try again.', 'error');
      }
    });
  }
}

// ==========================================
// EMAIL VERIFICATION PAGE LOGIC
// ==========================================

function setupVerifyEmailPage() {
  const verifyForm = document.getElementById('verifyForm');
  const resendBtn = document.getElementById('resendBtn');
  const userEmailEl = document.getElementById('userEmail');
  const otpInput = document.getElementById('otpCode');

  // Get pending verification data
  const pendingData = sessionStorage.getItem('pending_verification');
  
  if (!pendingData) {
    // No pending verification, redirect to login
    window.location.href = 'login.html';
    return;
  }

  const { email, role } = JSON.parse(pendingData);
  
  // Display email
  if (userEmailEl) {
    userEmailEl.textContent = email;
  }

  // Auto-format OTP input (only digits)
  if (otpInput) {
    otpInput.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/\D/g, '').slice(0, 4);
    });
  }

  // Handle verify form submission
  if (verifyForm) {
    verifyForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearErrors();

      const otp = otpInput.value.trim();

      if (otp.length !== 4) {
        setFieldError('otp', 'Please enter a 4-digit code');
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/auth/verify-email`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, otp, role })
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || 'Verification failed');
        }

        // Clear pending verification data
        sessionStorage.removeItem('pending_verification');

        showMessage('authMessage', 'Email verified successfully! Redirecting to login...', 'success');

        setTimeout(() => {
          window.location.href = 'login.html';
        }, 1500);

      } catch (error) {
        showMessage('authMessage', error.message || 'Verification failed. Please try again.', 'error');
      }
    });
  }

  // Handle resend OTP
  if (resendBtn) {
    resendBtn.addEventListener('click', async () => {
      resendBtn.disabled = true;
      resendBtn.textContent = 'Sending...';

      try {
        const response = await fetch(`${API_BASE}/auth/resend-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, role })
        });

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.message || 'Failed to resend code');
        }

        showMessage('authMessage', 'New code sent to your email!', 'success');
        
        setTimeout(() => {
          resendBtn.disabled = false;
          resendBtn.textContent = 'Resend Code';
        }, 3000);

      } catch (error) {
        showMessage('authMessage', error.message || 'Failed to resend code.', 'error');
        resendBtn.disabled = false;
        resendBtn.textContent = 'Resend Code';
      }
    });
  }
}

// ==========================================
// DASHBOARD PAGE LOGIC
// ==========================================

function setupDashboardPage() {
  const logoutBtn = document.getElementById('logoutBtn');
  const navLinks = document.querySelectorAll('.dashboard-nav__link');
  const profileSection = document.getElementById('profile-section');
  const settingsSection = document.getElementById('settings-section');
  const editProfileBtn = document.getElementById('editProfileBtn');
  const deleteAccountBtn = document.getElementById('deleteAccountBtn');

  // Check if user is logged in with JWT
  if (!isUserLoggedIn()) {
    clearUserSession();
    window.location.href = 'login.html';
    return;
  }

  // Verify JWT token is valid by fetching profile
  async function verifyAndLoadProfile() {
    try {
      const response = await authenticatedFetch(`${API_BASE}/auth/profile`);
      const result = await response.json();

      if (!response.ok || !result.data) {
        throw new Error('Failed to load profile');
      }

      // Update local storage with latest profile data
      const token = getAuthToken();
      saveUserSession(result.data, token);
      loadUserProfile(result.data);
    } catch (error) {
      console.error('Profile verification failed:', error);
      alert('Session expired or invalid. Please log in again.');
      clearUserSession();
      window.location.href = 'login.html';
    }
  }

  verifyAndLoadProfile();

  // Logout functionality
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to logout?')) {
        clearUserSession();
        window.location.href = 'index.html';
      }
    });
  }

  // Navigation between sections
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const section = link.getAttribute('data-section');
      
      // Remove active class from all links
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');

      // Hide all sections
      document.querySelectorAll('.dashboard-section').forEach(s => {
        s.classList.remove('active');
      });

      // Show selected section
      const sectionEl = document.getElementById(`${section}-section`);
      if (sectionEl) {
        sectionEl.classList.add('active');
      }
    });
  });

  // Edit Profile Button
  if (editProfileBtn) {
    editProfileBtn.addEventListener('click', () => {
      alert('Edit profile feature coming soon!');
    });
  }

  // Delete Account Button
  if (deleteAccountBtn) {
    deleteAccountBtn.addEventListener('click', async () => {
      if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
      }

      const user = getUserSession();
      if (!user || !user.id || !user.role) {
        alert('Unable to find your profile. Please log in again.');
        return;
      }

      try {
        const endpoint = user.role === 'brand'
          ? `${API_BASE}/brands/${user.id}`
          : `${API_BASE}/creators/${user.id}`;

        const response = await authenticatedFetch(endpoint, { method: 'DELETE' });
        const responseData = await response.json();

        if (!response.ok) {
          throw new Error(responseData.message || 'Failed to delete account');
        }

        clearUserSession();
        alert('Account deleted successfully.');
        window.location.href = 'index.html';
      } catch (error) {
        alert(error.message || 'Failed to delete account. Please try again.');
      }
    });
  }
}

function loadUserProfile(user) {
  if (!user) {
    window.location.href = 'login.html';
    return;
  }

  // Get display name based on role (backend has different field names)
  const displayName = user.username || user.company_name || 'User';
  
  // Update profile display
  document.getElementById('profileName').textContent = displayName;
  document.getElementById('profileEmail').textContent = user.email;
  document.getElementById('accountType').textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
  document.getElementById('accountEmail').textContent = user.email;

  // Set role badge
  const roleBadge = document.getElementById('profileRole');
  if (roleBadge) {
    roleBadge.textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
  }

  // Update verification status based on backend data
  const verificationStatus = document.getElementById('verificationStatus');
  if (verificationStatus) {
    const isVerified = user.is_verified || user.verified;
    verificationStatus.textContent = isVerified ? 'Approved' : 'Pending Admin Approval';
    verificationStatus.className = 'detail-value ' + (isVerified ? 'verified' : 'pending');
  }

  // Add role-specific details
  const additionalDetails = document.getElementById('additionalDetails');
  if (additionalDetails) {
    if (user.role === 'creator') {
      additionalDetails.innerHTML = `
        <span class="detail-label">Platform:</span>
        <span class="detail-value">${user.platform || 'N/A'}</span>
      `;
    } else if (user.role === 'brand') {
      additionalDetails.innerHTML = `
        <span class="detail-label">Industry:</span>
        <span class="detail-value">${user.industry || 'N/A'}</span>
      `;
    }
  }

  // Set avatar with initials
  const avatar = document.getElementById('profileAvatar');
  if (avatar) {
    const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    avatar.textContent = initials;
  }
}

// ==========================================
// INITIALIZE ON PAGE LOAD
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
  // Detect which page we're on and setup accordingly
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  if (currentPage === 'login.html') {
    setupLoginPage();
  } else if (currentPage === 'join-creator.html') {
    setupCreatorPage();
  } else if (currentPage === 'join-brand.html') {
    setupBrandPage();
  } else if (currentPage === 'verify-email.html') {
    setupVerifyEmailPage();
  } else if (currentPage === 'dashboard.html') {
    setupDashboardPage();
  }
});
