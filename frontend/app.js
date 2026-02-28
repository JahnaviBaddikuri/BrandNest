// API_BASE is provided by auth.js; fallback only when loaded standalone
if (typeof API_BASE === 'undefined') {
  window.API_BASE = "http://localhost:5000/api";
}
const apiStatusEl = document.getElementById("apiStatus");

const featuredFallback = [
  { name: "Jaydee", platform: "Instagram", followers: "1.1m", rating: "4.9", price: "$1,000", location: "Phoenix, AZ" },
  { name: "Pearline", platform: "UGC", followers: "UGC", rating: "4.9", price: "$1,000", location: "Phoenix, AZ" },
  { name: "Brandon", platform: "UGC", followers: "UGC", rating: "5.0", price: "$50", location: "Chicago, IL" },
  { name: "Dani", platform: "UGC", followers: "UGC", rating: "5.0", price: "$50", location: "London, UK" },
];

const grids = {
  featured: document.getElementById("featuredGrid"),
  brands: document.getElementById("brandsGrid"),
};

const platformSelect = document.getElementById("platformSelect");
const categorySelect = document.getElementById("categorySelect");
const searchBtn = document.getElementById("searchBtn");

let creatorsCache = [];
let brandsCache = [];

function setStatus(message, isError = false) {
  if (!apiStatusEl) {
    return;
  }
  apiStatusEl.textContent = `API status: ${message}`;
  apiStatusEl.style.color = isError ? "#b42318" : "#6c6c6c";
}

function formatFollowers(value) {
  if (value === null || value === undefined) return "n/a";
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}m`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
  return `${value}`;
}

function formatPrice(value) {
  if (value === null || value === undefined) return "$0";
  return `$${Number(value).toLocaleString()}`;
}

function normalizePlatform(value) {
  return String(value || "").toLowerCase();
}

function getRating(creator) {
  if (creator.engagement_rate !== undefined && creator.engagement_rate !== null) {
    return creator.engagement_rate.toFixed(1);
  }
  return "4.9";
}

function buildCreatorCard(item) {
  const card = document.createElement("div");
  card.className = "creator-card";
  const imageStyle = item.image ? `style="background-image:url('${item.image}')"` : "";
  const verifiedBadge = item.verified ? `<div class="creator-card__verified">Verified</div>` : '';
  
  // Check if user is logged in as brand (getSession might not be defined on landing page)
  let session = null;
  let isBrand = false;
  try {
    if (typeof getSession === 'function') {
      session = getSession();
      isBrand = session && session.role === 'brand';
    }
  } catch (e) {
    // getSession not available, user not logged in
  }
  
  const contactButton = isBrand ? `<button class="creator-card__contact-btn" data-creator-id="${item.id}">Contact</button>` : '';
  
  card.innerHTML = `
    <div class="creator-card__img" ${imageStyle}></div>
    <div class="creator-card__body">
      <div class="creator-card__tag">${item.platform} • ${item.followers}</div>
      <div class="creator-card__name">${item.name}</div>
      ${verifiedBadge}
      <div class="creator-card__meta">${item.price} • ${item.location}</div>
      <div class="creator-card__meta">Rating ${item.rating}</div>
      ${contactButton}
    </div>
  `;
  
  // Add event listener to contact button if it exists
  if (isBrand && typeof handleContactRequest === 'function') {
    const contactBtn = card.querySelector('.creator-card__contact-btn');
    if (contactBtn) {
      contactBtn.addEventListener('click', () => handleContactRequest(item.id, item.name));
    }
  }
  
  return card;
}

function buildBrandCard(brand) {
  const card = document.createElement("div");
  card.className = "brand-card";
  const logoStyle = brand.logo ? `style="background-image:url('${brand.logo}')"` : "";
  const verifiedBadge = brand.verified ? `<div class="brand-card__verified">Verified</div>` : '';
  
  card.innerHTML = `
    <div class="brand-card__logo" ${logoStyle}>
      ${!brand.logo ? `<span class="brand-card__initials">${brand.initials}</span>` : ''}
    </div>
    <div class="brand-card__body">
      <div class="brand-card__industry">${brand.industry}</div>
      <div class="brand-card__name">${brand.name}</div>
      ${verifiedBadge}
      <div class="brand-card__location">${brand.location}</div>
      <div class="brand-card__website">
        <a href="${brand.website}" target="_blank" rel="noopener noreferrer">
          ${brand.websiteDisplay}
        </a>
      </div>
    </div>
  `;
  return card;
}

function fillGrid(grid, items) {
  grid.innerHTML = "";
  items.forEach((item) => grid.appendChild(buildCreatorCard(item)));
}

function fillBrandsGrid(grid, items) {
  grid.innerHTML = "";
  items.forEach((item) => grid.appendChild(buildBrandCard(item)));
}

function toCardData(creator) {
  return {
    id: creator.id,
    name: creator.username || "Creator",
    platform: creator.platform || "UGC",
    followers: formatFollowers(creator.followers_count),
    rating: getRating(creator),
    price: formatPrice(creator.rate),
    location: creator.location || "Remote",
    image: creator.profile_image_url || "",
    verified: creator.is_verified || false,
  };
}

function toBrandCardData(brand) {
  const getInitials = (name) => {
    return name
      .split(/[\s]+/)
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const formatWebsite = (url) => {
    if (!url) return '';
    return url.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, '');
  };

  return {
    name: brand.company_name || "Brand",
    industry: brand.industry || "Business",
    location: brand.location || "Remote",
    website: brand.website || "#",
    websiteDisplay: formatWebsite(brand.website),
    logo: brand.logo_url || "",
    initials: getInitials(brand.company_name || "Brand"),
    verified: brand.verified || false,
  };
}

async function fetchCreators(params = {}) {
  const query = new URLSearchParams();
  if (params.platform) query.append("platform", params.platform);
  if (params.category) query.append("category", params.category);
  const url = `${API_BASE}/creators${query.toString() ? `?${query}` : ""}`;
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || "Failed to load creators");
  }
  return data.data || [];
}

async function fetchBrands(params = {}) {
  const query = new URLSearchParams();
  if (params.industry) query.append("industry", params.industry);
  const url = `${API_BASE}/brands${query.toString() ? `?${query}` : ""}`;
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.message || "Failed to load brands");
  }
  return data.data || [];
}

async function loadCreators() {
  try {
    creatorsCache = await fetchCreators();
    setStatus("connected");
    renderCreators(creatorsCache);
  } catch (error) {
    setStatus("offline (showing placeholders)", true);
    renderFallback();
  }
}

async function loadBrands() {
  try {
    brandsCache = await fetchBrands();
    renderBrands(brandsCache);
  } catch (error) {
    console.error("Failed to load brands:", error);
    // Silently fail for brands, don't show error
  }
}

function renderCreators(creators) {
  const cards = creators.map(toCardData);
  fillGrid(grids.featured, cards.slice(0, 8));
}

function renderBrands(brands) {
  const cards = brands.map(toBrandCardData);
  fillBrandsGrid(grids.brands, cards.slice(0, 8));
}

function renderFallback() {
  fillGrid(grids.featured, featuredFallback);
}

searchBtn.addEventListener("click", async () => {
  const platformValue = platformSelect.value;
  const categoryValue = categorySelect.value;
  const platform = platformValue.startsWith("Choose") ? "" : platformValue.toLowerCase();
  const category = categoryValue.startsWith("Choose") ? "" : categoryValue.toLowerCase();

  try {
    const results = await fetchCreators({ platform, category });
    if (results.length) {
      fillGrid(grids.featured, results.map(toCardData));
      setStatus(`found ${results.length} creators`);
    } else {
      fillGrid(grids.featured, featuredFallback);
      setStatus("no matches, showing featured");
    }
  } catch (error) {
    setStatus(error.message, true);
  }
});

loadCreators();
loadBrands();

// Handle contact request
async function handleContactRequest(creatorId, creatorName) {
  // Prompt for optional message
  const message = prompt(`Send a contact request to ${creatorName}. Add a message (optional):`);
  
  // User cancelled
  if (message === null) {
    return;
  }
  
  try {
    const response = await authenticatedFetch(`${API_BASE}/contact-requests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        creator_id: creatorId,
        message: message.trim()
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      if (response.status === 409) {
        alert('You already sent a request to this creator. Check your Requests page to see the status.');
      } else {
        throw new Error(error.error || 'Failed to send contact request');
      }
      return;
    }
    
    const data = await response.json();
    alert(`Contact request sent to ${creatorName}! They will be notified.`);
    
  } catch (error) {
    console.error('Error sending contact request:', error);
    alert('Error: ' + error.message);
  }
}
