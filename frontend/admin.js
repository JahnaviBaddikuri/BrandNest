const API_BASE = "http://localhost:5000/api";
const ADMIN_KEY = localStorage.getItem('admin_key') || prompt('Enter admin API key:') || '';
if (ADMIN_KEY) localStorage.setItem('admin_key', ADMIN_KEY);

function adminFetch(url, options = {}) {
  options.headers = { ...options.headers, 'X-Admin-Key': ADMIN_KEY };
  return fetch(url, options);
}

// DOM Elements
const creatorsList = document.getElementById("creatorsList");
const brandsList = document.getElementById("brandsList");
const creatorCount = document.getElementById("creatorCount");
const brandCount = document.getElementById("brandCount");
const refreshBtn = document.getElementById("refreshBtn");

// Mock data for initial frontend testing
const mockPendingCreators = [
  {
    id: 1,
    username: "sarah_fitness",
    email: "sarah@example.com",
    platform: "Instagram",
    followers_count: 125000,
    category: "Fitness",
    location: "Los Angeles, CA",
    rate: 1500,
    engagement_rate: 4.2,
    created_at: "2026-02-10T10:30:00Z",
    is_verified: false
  },
  {
    id: 2,
    username: "tech_mike",
    email: "mike@example.com",
    platform: "YouTube",
    followers_count: 450000,
    category: "Tech",
    location: "Austin, TX",
    rate: 3000,
    engagement_rate: 5.8,
    created_at: "2026-02-11T14:20:00Z",
    is_verified: false
  },
  {
    id: 3,
    username: "beauty_emma",
    email: "emma@example.com",
    platform: "TikTok",
    followers_count: 890000,
    category: "Beauty",
    location: "New York, NY",
    rate: 2500,
    engagement_rate: 6.5,
    created_at: "2026-02-12T09:15:00Z",
    is_verified: false
  }
];

const mockPendingBrands = [
  {
    id: 1,
    company_name: "TechGear Pro",
    email: "contact@techgear.com",
    industry: "Technology",
    location: "San Francisco, CA",
    website: "https://techgear.com",
    created_at: "2026-02-09T11:00:00Z",
    verified: false
  },
  {
    id: 2,
    company_name: "Glow Beauty Co",
    email: "hello@glowbeauty.com",
    industry: "Beauty & Cosmetics",
    location: "Miami, FL",
    website: "https://glowbeauty.com",
    created_at: "2026-02-11T16:45:00Z",
    verified: false
  }
];

// Utility Functions
function formatFollowers(value) {
  if (value === null || value === undefined) return "n/a";
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return `${value}`;
}

function formatPrice(value) {
  if (value === null || value === undefined) return "$0";
  return `$${Number(value).toLocaleString()}`;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getInitials(name) {
  return name
    .split(/[\s_]+/)
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// Build Creator Card
function buildCreatorCard(creator) {
  const card = document.createElement("div");
  card.className = "pending-card";
  card.dataset.id = creator.id;
  card.dataset.type = "creator";

  card.innerHTML = `
    <div class="pending-card__content">
      <div class="pending-card__details">
        <div class="pending-card__header">
          <div class="pending-card__info">
            <div class="pending-card__name">@${creator.username}</div>
            <div class="pending-card__email">${creator.email}</div>
            <span class="pending-card__type">Creator</span>
            <span class="pending-card__date">Joined ${formatDate(creator.created_at)}</span>
          </div>
        </div>
        
        <div class="pending-card__meta">
          <div class="meta-item">
            <span class="meta-item__label">Platform</span>
            <span class="meta-item__value">${creator.platform}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Followers</span>
            <span class="meta-item__value meta-item__value--highlight">${formatFollowers(creator.followers_count)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Category</span>
            <span class="meta-item__value">${creator.category}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Location</span>
            <span class="meta-item__value">${creator.location}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Rate</span>
            <span class="meta-item__value">${formatPrice(creator.rate)}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Engagement</span>
            <span class="meta-item__value">${creator.engagement_rate}%</span>
          </div>
        </div>
      </div>
      
      <div class="pending-card__actions">
        <button class="btn-approve" onclick="approveUser('creator', ${creator.id})">
          Approve
        </button>
      </div>
    </div>
  `;

  return card;
}

// Build Brand Card
function buildBrandCard(brand) {
  const card = document.createElement("div");
  card.className = "pending-card";
  card.dataset.id = brand.id;
  card.dataset.type = "brand";

  card.innerHTML = `
    <div class="pending-card__content">
      <div class="pending-card__details">
        <div class="pending-card__header">
          <div class="pending-card__info">
            <div class="pending-card__name">${brand.company_name}</div>
            <div class="pending-card__email">${brand.email}</div>
            <span class="pending-card__type">Brand</span>
            <span class="pending-card__date">Joined ${formatDate(brand.created_at)}</span>
          </div>
        </div>
        
        <div class="pending-card__meta">
          <div class="meta-item">
            <span class="meta-item__label">Industry</span>
            <span class="meta-item__value">${brand.industry}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Location</span>
            <span class="meta-item__value">${brand.location}</span>
          </div>
          <div class="meta-item">
            <span class="meta-item__label">Website</span>
            <span class="meta-item__value">
              <a href="${brand.website}" target="_blank" style="color: #175cd3; text-decoration: none;">
                ${brand.website.replace('https://', '')}
              </a>
            </span>
          </div>
        </div>
      </div>
      
      <div class="pending-card__actions">
        <button class="btn-approve" onclick="approveUser('brand', ${brand.id})">
          Approve
        </button>
      </div>
    </div>
  `;

  return card;
}

// Load Pending Users
async function loadPendingUsers() {
  // Clear existing content
  creatorsList.innerHTML = '<div class="loading-spinner"></div>';
  brandsList.innerHTML = '<div class="loading-spinner"></div>';

  try {
    // Fetch pending users from backend
    const response = await adminFetch(`${API_BASE}/admin/pending-users`);
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || 'Failed to load pending users');
    }
    
    // Render the data
    renderCreators(result.data.creators || []);
    renderBrands(result.data.brands || []);
    
  } catch (error) {
    console.error('Error loading pending users:', error);
    
    // Show error message and fallback to mock data for testing
    creatorsList.innerHTML = '<div style="text-align:center;padding:20px;color:#b42318;">Failed to load data. Using mock data.</div>';
    brandsList.innerHTML = '<div style="text-align:center;padding:20px;color:#b42318;">Failed to load data. Using mock data.</div>';
    
    setTimeout(() => {
      renderCreators(mockPendingCreators);
      renderBrands(mockPendingBrands);
    }, 1000);
  }
}

function renderCreators(creators) {
  creatorsList.innerHTML = "";
  
  if (creators.length === 0) {
    creatorCount.textContent = "0";
    return;
  }

  creatorCount.textContent = creators.length;
  creators.forEach(creator => {
    creatorsList.appendChild(buildCreatorCard(creator));
  });
}

function renderBrands(brands) {
  brandsList.innerHTML = "";
  
  if (brands.length === 0) {
    brandCount.textContent = "0";
    return;
  }

  brandCount.textContent = brands.length;
  brands.forEach(brand => {
    brandsList.appendChild(buildBrandCard(brand));
  });
}

// Approve User Function
async function approveUser(userType, userId) {
  const card = document.querySelector(`.pending-card[data-id="${userId}"][data-type="${userType}"]`);
  const approveBtn = card.querySelector('.btn-approve');
  
  // Disable button
  approveBtn.disabled = true;
  approveBtn.textContent = "Approving...";

  try {
    // Call backend API to approve user
    const response = await adminFetch(`${API_BASE}/admin/approve/${userType}/${userId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || 'Failed to approve user');
    }
    
    // Show success message
    showSuccessMessage(`${userType === 'creator' ? 'Creator' : 'Brand'} approved successfully!`);
    
    // Remove card with animation
    card.style.transition = "all 0.3s ease";
    card.style.opacity = "0";
    card.style.transform = "translateX(20px)";
    
    setTimeout(() => {
      card.remove();
      updateCounts();
    }, 300);
    
  } catch (error) {
    console.error('Error approving user:', error);
    approveBtn.disabled = false;
    approveBtn.textContent = "Approve";
    alert(`Failed to approve user: ${error.message}`);
  }
}

function updateCounts() {
  const creatorsRemaining = creatorsList.querySelectorAll('.pending-card').length;
  const brandsRemaining = brandsList.querySelectorAll('.pending-card').length;
  
  creatorCount.textContent = creatorsRemaining;
  brandCount.textContent = brandsRemaining;
}

function showSuccessMessage(message) {
  const existingMsg = document.querySelector('.success-message');
  if (existingMsg) existingMsg.remove();
  
  const successDiv = document.createElement('div');
  successDiv.className = 'success-message';
  successDiv.textContent = message;
  
  const adminContainer = document.querySelector('.admin-container');
  adminContainer.insertBefore(successDiv, adminContainer.firstChild);
  
  setTimeout(() => {
    successDiv.style.opacity = '0';
    setTimeout(() => successDiv.remove(), 300);
  }, 3000);
}

// Event Listeners
refreshBtn.addEventListener('click', loadPendingUsers);

// Initial Load
loadPendingUsers();

// Make approveUser globally accessible
window.approveUser = approveUser;
