const API_BASE = "http://localhost:5000/api";
const apiStatusEl = document.getElementById("apiStatus");

const featuredFallback = [
  { name: "Jaydee", platform: "Instagram", followers: "1.1m", rating: "4.9", price: "$1,000", location: "Phoenix, AZ" },
  { name: "Pearline", platform: "UGC", followers: "UGC", rating: "4.9", price: "$1,000", location: "Phoenix, AZ" },
  { name: "Brandon", platform: "UGC", followers: "UGC", rating: "5.0", price: "$50", location: "Chicago, IL" },
  { name: "Dani", platform: "UGC", followers: "UGC", rating: "5.0", price: "$50", location: "London, UK" },
];

const grids = {
  featured: document.getElementById("featuredGrid"),
};

const platformSelect = document.getElementById("platformSelect");
const categorySelect = document.getElementById("categorySelect");
const searchBtn = document.getElementById("searchBtn");



let creatorsCache = [];

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
  const verifiedBadge = item.verified ? `<div class="creator-card__verified">✓ Verified</div>` : '';
  
  card.innerHTML = `
    <div class="creator-card__img" ${imageStyle}></div>
    <div class="creator-card__body">
      <div class="creator-card__tag">${item.platform} • ${item.followers}</div>
      <div class="creator-card__name">${item.name}</div>
      ${verifiedBadge}
      <div class="creator-card__meta">${item.price} • ${item.location}</div>
      <div class="creator-card__meta">Rating ${item.rating}</div>
    </div>
  `;
  return card;
}

function fillGrid(grid, items) {
  grid.innerHTML = "";
  items.forEach((item) => grid.appendChild(buildCreatorCard(item)));
}

function toCardData(creator) {
  return {
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

function renderCreators(creators) {
  const cards = creators.map(toCardData);
  fillGrid(grids.featured, cards.slice(0, 8));
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
