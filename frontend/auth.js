/* ===========================
   AUTHENTICATION 
   =========================== */

const API_BASE = "http://localhost:5000/api";

const firebaseConfig = {
  apiKey: "AIzaSyD641YTDz6q47v2519phcOfMqVnJI30ocM",
  authDomain: "collabstr-5181a.firebaseapp.com",
  projectId: "collabstr-5181a",
  storageBucket: "collabstr-5181a.firebasestorage.app",
  messagingSenderId: "999428574878",
  appId: "1:999428574878:web:53a59956508c809181358f",
  measurementId: "G-ZWM90XD8CJ",
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();
auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(() => {
  console.warn("Firebase persistence not set.");
});

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

  console.log('📤 Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);

  const payload = new FormData();
  payload.append('file', file);

  console.log('📦 FormData created, sending to backend...');

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

// Session Management (simplified - backend is source of truth)
function saveUserSession(userData) {
  localStorage.setItem('collabstr_user', JSON.stringify(userData));
  localStorage.setItem('collabstr_logged_in', 'true');
}

function getUserSession() {
  const user = localStorage.getItem('collabstr_user');
  return user ? JSON.parse(user) : null;
}

function clearUserSession() {
  localStorage.removeItem('collabstr_user');
  localStorage.removeItem('collabstr_logged_in');
}

function isUserLoggedIn() {
  return localStorage.getItem('collabstr_logged_in') === 'true';
}

// Fetch user profile from backend (THIS IS KEY!)
async function fetchUserProfile(firebaseUser) {
  try {
    const token = await firebaseUser.getIdToken();
    const response = await fetch(`${API_BASE}/auth/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const result = await response.json();
      return result.data; // Contains profile + role from backend
    }
    return null;
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    return null;
  }
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
        // Step 1: Sign in with Firebase
        const result = await auth.signInWithEmailAndPassword(email, password);
        const user = result.user;

        // Step 2: Fetch profile from backend (source of truth!)
        const profile = await fetchUserProfile(user);

        if (!profile) {
          await auth.signOut();
          showMessage('authMessage', 'Profile not found. Please complete signup first.', 'error');
          return;
        }

        // Step 3: Check if selected role matches backend role
        if (profile.role !== role) {
          await auth.signOut();
          showMessage('authMessage', `Role mismatch. You registered as a ${profile.role}.`, 'error');
          return;
        }

        // Step 4: Save session with backend data
        saveUserSession(profile);
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

  // Forgot Password functionality
  if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener('click', async (e) => {
      e.preventDefault();
      
      const email = document.getElementById('loginEmail').value.trim();
      
      if (!email) {
        showMessage('authMessage', 'Please enter your email address first', 'error');
        return;
      }
      
      if (!validateEmail(email)) {
        showMessage('authMessage', 'Please enter a valid email address', 'error');
        return;
      }
      
      try {
        await auth.sendPasswordResetEmail(email);
        showMessage('authMessage', 'Password reset email sent! Check your inbox.', 'success');
      } catch (error) {
        if (error.code === 'auth/user-not-found') {
          showMessage('authMessage', 'No account found with this email', 'error');
        } else {
          showMessage('authMessage', error.message || 'Failed to send reset email', 'error');
        }
      }
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
      
      console.log('📋 Profile image input:', profileImageInput);
      console.log('📁 Profile image file:', profileImageFile);
      
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

      let firebaseUser = null;

      try {
        // Step 1: Create Firebase account
        const result = await auth.createUserWithEmailAndPassword(data.email, data.password);
        firebaseUser = result.user;
        await firebaseUser.updateProfile({ displayName: data.username });

        // Step 2: Upload profile image if provided
        console.log('🖼️ About to upload image:', profileImageFile);
        data.profile_image_url = await uploadProfileImage(profileImageFile);
        console.log('✅ Image upload result:', data.profile_image_url);

        // Step 3: Send profile to backend with Firebase UID
        data.firebase_uid = firebaseUser.uid; // Add Firebase UID!

        const response = await fetch(`${API_BASE}/creators`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        const responseData = await response.json();

        if (!response.ok) {
          // If backend fails, delete Firebase account to keep things in sync
          await firebaseUser.delete();
          throw new Error(responseData.message || 'Failed to create profile');
        }

        // Step 4: Save profile from backend (includes role)
        const profile = responseData.data;
        profile.role = 'creator';
        saveUserSession(profile);

        showMessage('authMessage', 'Account created successfully! Redirecting...', 'success');

        setTimeout(() => {
          window.location.href = 'dashboard.html';
        }, 1200);
      } catch (error) {
        if (firebaseUser) {
          try {
            await firebaseUser.delete();
          } catch (cleanupError) {
            console.warn('Failed to cleanup Firebase user:', cleanupError);
          }
        }
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
      const data = {
        email: formData.get('email'),
        password: formData.get('password'),
        company_name: formData.get('company_name'),
        industry: formData.get('industry'),
        location: formData.get('location'),
        website: formData.get('website'),
        logo_url: formData.get('logo_url'),
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
        // Step 1: Create Firebase account
        const result = await auth.createUserWithEmailAndPassword(data.email, data.password);
        const user = result.user;
        await user.updateProfile({ displayName: data.company_name });

        // Step 2: Send profile to backend with Firebase UID
        data.firebase_uid = user.uid; // Add Firebase UID!

        const response = await fetch(`${API_BASE}/brands`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        const responseData = await response.json();

        if (!response.ok) {
          // If backend fails, delete Firebase account to keep things in sync
          await user.delete();
          throw new Error(responseData.message || 'Failed to create profile');
        }

        // Step 3: Save profile from backend (includes role)
        const profile = responseData.data;
        profile.role = 'brand';
        saveUserSession(profile);

        showMessage('authMessage', 'Brand account created successfully! Redirecting...', 'success');

        setTimeout(() => {
          window.location.href = 'dashboard.html';
        }, 1200);
      } catch (error) {
        showMessage('authMessage', error.message || 'Failed to create account. Please try again.', 'error');
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

  // Check if user is logged in
  auth.onAuthStateChanged(async (firebaseUser) => {
    if (!firebaseUser) {
      clearUserSession();
      window.location.href = 'login.html';
      return;
    }

    // Fetch profile from backend (source of truth!)
    const profile = await fetchUserProfile(firebaseUser);
    
    if (!profile) {
      // User authenticated but no profile in backend
      alert('Profile not found. Please contact support.');
      auth.signOut();
      window.location.href = 'login.html';
      return;
    }

    saveUserSession(profile);
    loadUserProfile(profile);
  });

  // Logout functionality
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (confirm('Are you sure you want to logout?')) {
        auth.signOut().finally(() => {
          clearUserSession();
          window.location.href = 'index.html';
        });
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

        const response = await fetch(endpoint, { method: 'DELETE' });
        const responseData = await response.json();

        if (!response.ok) {
          throw new Error(responseData.message || 'Failed to delete account');
        }

        if (auth.currentUser) {
          try {
            await auth.currentUser.delete();
          } catch (error) {
            console.warn('Firebase account deletion failed:', error);
          }
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
    verificationStatus.textContent = isVerified ? 'Approved ✓' : 'Pending Admin Approval';
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
  } else if (currentPage === 'dashboard.html') {
    setupDashboardPage();
  }
});
