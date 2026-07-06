// Base API URL config
const API_URL = ""; 

// App state
let state = {
    token: localStorage.getItem("token") || null,
    user: JSON.parse(localStorage.getItem("user")) || null,
    currentCategory: null,
    searchQuery: "",
    page: 1,
    limit: 8,
    cart: { items: [], total: 0 },
    selectedAddressId: null,
    categories: []
};

window.state = state;
window.apiCall = apiCall;
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
window.handleLogout = handleLogout;
window.renderCartUI = renderCartUI;
window.openCheckout = openCheckout;
window.fetchOrders = fetchOrders;
window.fetchProviderDashboard = fetchProviderDashboard;
window.fetchAdminDashboard = fetchAdminDashboard;

// --- Toast Notifications Helper ---
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let icon = "fa-circle-check";
    if (type === "error") icon = "fa-circle-xmark";
    if (type === "warning") icon = "fa-triangle-exclamation";
    
    toast.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add("hide");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// --- API Request Wrapper ---
async function apiCall(endpoint, method = "GET", body = null, isMultipart = false) {
    const headers = {};
    if (state.token) {
        headers["Authorization"] = `Bearer ${state.token}`;
    }
    
    if (body && !isMultipart) {
        headers["Content-Type"] = "application/json";
    }

    const config = {
        method,
        headers
    };

    if (body) {
        config.body = isMultipart ? body : JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || "Something went wrong");
        }
        return data;
    } catch (err) {
        showToast(err.message, "error");
        throw err;
    }
}

// Helper to decode JWT token to extract role/claims
function decodeToken(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

// --- Navigation Controller ---
function showView(viewId) {
    document.querySelectorAll(".view-section").forEach(section => {
        section.classList.add("hidden");
        section.classList.remove("active");
    });
    
    const activeSection = document.getElementById(viewId);
    if (activeSection) {
        activeSection.classList.remove("hidden");
        activeSection.classList.add("active");
    }

    // Update navbar active state
    document.querySelectorAll(".nav-link").forEach(link => link.classList.remove("active"));
    if (viewId === "home-view") document.getElementById("nav-home").classList.add("active");
    if (viewId === "orders-view") document.getElementById("nav-orders").classList.add("active");
    if (viewId === "provider-view") document.getElementById("nav-provider-dashboard").classList.add("active");
    if (viewId === "admin-view") document.getElementById("nav-admin-dashboard").classList.add("active");
}

// --- Modals Controller ---
function openModal(modalId) {
    document.getElementById(modalId).classList.add("active");
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("active");
}

// --- Authentication Handler ---
async function handleLogin(email, password) {
    try {
        const res = await apiCall("/auth/login", "POST", { email, password });
        state.token = res.access_token;
        localStorage.setItem("token", res.access_token);
        
        // Decode token to find details
        const payload = decodeToken(res.access_token);
        if (payload) {
            state.user = {
                id: payload.id,
                email: payload.email,
                role: payload.role,
                full_name: payload.email.split("@")[0] // fallback placeholder name
            };
            localStorage.setItem("user", JSON.stringify(state.user));
        }
        
        closeModal("login-modal");
        showToast("Logged in successfully!");
        initApp();
    } catch (err) {
        // Handled in apiCall
    }
}

async function handleRegister(name, email, phone, password, role) {
    try {
        const res = await apiCall("/auth/register", "POST", {
            full_name: name,
            email,
            phone,
            password,
            role
        });
        
        closeModal("register-modal");
        
        if (role === "provider") {
            showToast("Registration successful! Account awaits admin activation.", "warning");
        } else {
            showToast("Registration successful! Please login.");
            openModal("login-modal");
        }
    } catch (err) {
        // Handled in apiCall
    }
}

function handleLogout() {
    state.token = null;
    state.user = null;
    state.cart = { items: [], total: 0 };
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    
    showToast("Logged out successfully");
    
    // Reset view
    initApp();
}

// --- Cart Management Logic ---
async function fetchCart() {
    if (!state.token || state.user?.role !== "customer") return;
    try {
        const cartData = await apiCall("/cart");
        state.cart = cartData;
        renderCartUI();
    } catch (err) {
        console.error(err);
    }
}

function renderCartUI() {
    const badge = document.getElementById("cart-badge-count");
    const container = document.getElementById("cart-items-container");
    const totalDisplay = document.getElementById("cart-total-amount");
    
    const count = state.cart.items.reduce((sum, item) => sum + item.quantity, 0);
    badge.innerText = count;
    
    if (state.cart.items.length === 0) {
        container.innerHTML = `
            <div class="cart-empty-message">
                <i class="fa-solid fa-cart-shopping"></i>
                <p>Your cart is empty</p>
            </div>
        `;
        totalDisplay.innerText = "₹0.00";
        return;
    }

    container.innerHTML = state.cart.items.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4 class="cart-item-title">${item.name}</h4>
                <span class="cart-item-price">₹${item.price.toFixed(2)}</span>
                <div class="cart-item-controls">
                    <div class="quantity-selector">
                        <button class="qty-btn" onclick="updateCartItemQty(${item.id}, ${item.quantity - 1})"><i class="fa-solid fa-minus"></i></button>
                        <input type="number" value="${item.quantity}" readonly>
                        <button class="qty-btn" onclick="updateCartItemQty(${item.id}, ${item.quantity + 1})"><i class="fa-solid fa-plus"></i></button>
                    </div>
                    <button class="cart-item-delete" onclick="removeCartItem(${item.id})">Remove</button>
                </div>
            </div>
        </div>
    `).join("");
    
    totalDisplay.innerText = `₹${state.cart.total.toFixed(2)}`;
}

async function addProductToCart(productId, quantity) {
    if (!state.token) {
        showToast("Please login as a customer to add items to cart", "warning");
        openModal("login-modal");
        return;
    }
    if (state.user?.role !== "customer") {
        showToast("Sellers and Admins cannot use shopping carts", "warning");
        return;
    }
    try {
        await apiCall("/cart", "POST", { product_id: productId, quantity });
        showToast("Product added to cart!");
        closeModal("product-detail-modal");
        fetchCart();
    } catch (err) {
        // Handled
    }
}

async function updateCartItemQty(itemId, newQty) {
    if (newQty < 1) {
        removeCartItem(itemId);
        return;
    }
    try {
        await apiCall(`/cart/${itemId}`, "PUT", { quantity: newQty });
        fetchCart();
    } catch (err) {
        // Handled
    }
}

async function removeCartItem(itemId) {
    try {
        await apiCall(`/cart/${itemId}`, "DELETE");
        showToast("Item removed from cart");
        fetchCart();
    } catch (err) {
        // Handled
    }
}

// --- Product Retrieval & Listing ---
async function fetchCategories() {
    try {
        const cats = await apiCall("/com/categories");
        state.categories = cats;
        
        // Render in Home Categories section
        const list = document.getElementById("categories-list");
        list.innerHTML = `
            <div class="category-pill ${state.currentCategory === null ? 'active' : ''}" onclick="selectCategory(null)">
                All Categories
            </div>
        ` + cats.map(cat => `
            <div class="category-pill ${state.currentCategory === cat.id ? 'active' : ''}" onclick="selectCategory(${cat.id})">
                ${cat.name}
            </div>
        `).join("");
        
        // Render in Upload Product form select options
        const select = document.getElementById("prod-category");
        if (select) {
            select.innerHTML = cats.map(cat => `
                <option value="${cat.id}">${cat.name}</option>
            `).join("");
        }
    } catch (e) {
        // Handled
    }
}

function selectCategory(catId) {
    state.currentCategory = catId;
    state.page = 1;
    fetchCategories();
    fetchProducts();
}

async function fetchProducts() {
    let url = `/products?page=${state.page}&limit=${state.limit}`;
    if (state.currentCategory) url += `&category=${state.currentCategory}`;
    if (state.searchQuery) url += `&search=${encodeURIComponent(state.searchQuery)}`;
    
    try {
        const res = await apiCall(url);
        renderProducts(res.data);
        
        // Update pagination buttons
        document.getElementById("current-page-display").innerText = `Page ${state.page}`;
        document.getElementById("prev-page-btn").disabled = state.page === 1;
        document.getElementById("next-page-btn").disabled = res.data.length < state.limit;
    } catch (err) {
        console.error(err);
    }
}

function renderProducts(productsList) {
    const grid = document.getElementById("products-grid-container");
    if (productsList.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                <h3>No products found matching query</h3>
            </div>
        `;
        return;
    }

    grid.innerHTML = productsList.map(prod => `
        <div class="product-card" onclick="viewProductDetails(${prod.id})">
            <div class="product-img-wrapper">
                <img src="${prod.image_url || '/uploads/products/placeholder.png'}" alt="${prod.name}" onerror="this.src='https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image'">
            </div>
            <div class="product-info">
                <h4 class="product-title">${prod.name}</h4>
                <p class="product-desc-excerpt">${prod.description || 'No description provided.'}</p>
                <div class="product-footer">
                    <span class="product-price">₹${prod.price.toFixed(2)}</span>
                    <button class="btn-icon" onclick="event.stopPropagation(); addProductToCart(${prod.id}, 1);"><i class="fa-solid fa-cart-plus"></i></button>
                </div>
            </div>
        </div>
    `).join("");
}

async function viewProductDetails(productId) {
    try {
        const prod = await apiCall(`/products/${productId}`);
        
        document.getElementById("modal-product-name").innerText = prod.name;
        document.getElementById("modal-product-title-detail").innerText = prod.name;
        document.getElementById("modal-product-desc").innerText = prod.description || "No description provided.";
        document.getElementById("modal-product-price").innerText = `₹${prod.price.toFixed(2)}`;
        document.getElementById("modal-product-stock").innerText = `In Stock: ${prod.stock_quantity}`;
        
        const cat = state.categories.find(c => c.id === prod.category_id);
        document.getElementById("modal-product-category").innerText = cat ? cat.name : "Products";
        
        const img = document.getElementById("modal-product-img");
        img.src = prod.image_url || "https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image";
        img.onerror = () => { img.src = "https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image"; };
        
        // Reset qty form input
        document.getElementById("qty-input").value = 1;
        
        // Add add to cart listener
        const addBtn = document.getElementById("modal-add-to-cart-btn");
        addBtn.onclick = () => {
            const qty = parseInt(document.getElementById("qty-input").value);
            addProductToCart(prod.id, qty);
        };
        
        openModal("product-detail-modal");
    } catch (e) {
        // Handled
    }
}

// --- Addresses ---
async function fetchAddressesCheckout() {
    try {
        const addrs = await apiCall("/address");
        const list = document.getElementById("checkout-address-list");
        
        if (addrs.length === 0) {
            list.innerHTML = `<p style="color: var(--text-muted); font-size:14px;">No addresses saved. Please add one below.</p>`;
            state.selectedAddressId = null;
            return;
        }

        list.innerHTML = addrs.map((addr, idx) => {
            const isSelected = addr.is_default || idx === 0;
            if (isSelected) state.selectedAddressId = addr.id;
            
            return `
                <label class="address-card ${isSelected ? 'selected' : ''}" onclick="selectAddress(${addr.id})">
                    <input type="radio" name="checkout_address" value="${addr.id}" ${isSelected ? 'checked' : ''}>
                    <div class="address-details">
                        <strong>${addr.address_line1}</strong> ${addr.address_line2 ? ', ' + addr.address_line2 : ''} ${addr.is_default ? '<span class="address-default-badge">Default</span>' : ''}<br>
                        ${addr.city}, ${addr.state}, ${addr.country} - ${addr.postal_code}
                    </div>
                </label>
            `;
        }).join("");
    } catch (e) {
        // Handled
    }
}

function selectAddress(id) {
    state.selectedAddressId = id;
    document.querySelectorAll(".address-card").forEach(c => c.classList.remove("selected"));
    event.currentTarget.classList.add("selected");
}

async function handleAddAddress(formData) {
    try {
        await apiCall("/address", "POST", formData);
        showToast("Address added successfully!");
        closeModal("add-address-modal");
        fetchAddressesCheckout();
    } catch (e) {
        // Handled
    }
}

// --- Checkout & Checkout Orders ---
function openCheckout() {
    if (state.cart.items.length === 0) {
        showToast("Your cart is empty", "warning");
        return;
    }
    
    // Render order summary list
    const summary = document.getElementById("checkout-summary-items");
    summary.innerHTML = state.cart.items.map(item => `
        <div class="summary-item">
            <span>${item.name} (x${item.quantity})</span>
            <strong>₹${(item.price * item.quantity).toFixed(2)}</strong>
        </div>
    `).join("");
    
    document.getElementById("checkout-grand-total").innerText = `₹${state.cart.total.toFixed(2)}`;
    
    fetchAddressesCheckout();
    showView("checkout-view");
}

async function handlePlaceOrder() {
    if (!state.selectedAddressId) {
        showToast("Please select a shipping address", "warning");
        return;
    }
    
    const payment_method = document.querySelector('input[name="payment_method"]:checked').value;
    
    try {
        const res = await apiCall("/orders", "POST", {
            address_id: state.selectedAddressId,
            payment_method
        });
        
        showToast("Order placed successfully!");
        const orderId = res.order_id;
        
        // Empty cart locally
        state.cart = { items: [], total: 0 };
        renderCartUI();
        
        if (payment_method === "online") {
            // Trigger payment modal gateway
            triggerPaymentGate(orderId);
        } else {
            showView("orders-view");
            fetchOrders();
        }
    } catch (e) {
        // Handled
    }
}

// Razorpay Checkout Flow
async function triggerPaymentGate(orderId) {
    try {
        const payInit = await apiCall("/payments/create", "POST", { order_id: orderId });

        if (!window.Razorpay) {
            await new Promise((resolve, reject) => {
                const script = document.createElement("script");
                script.src = "https://checkout.razorpay.com/v1/checkout.js";
                script.onload = resolve;
                script.onerror = reject;
                document.body.appendChild(script);
            });
        }

        const options = {
            key: payInit.key_id,
            amount: Math.round(payInit.amount * 100),
            currency: payInit.currency || "INR",
            name: "Ecom Store",
            description: `Order #${payInit.order_id}`,
            order_id: payInit.razorpay_order_id,
            handler: async function (response) {
                showToast("Payment success! Verifying...");
                try {
                    await apiCall("/payments/verify", "POST", {
                        payment_id: payInit.payment_id,
                        razorpay_order_id: response.razorpay_order_id,
                        razorpay_payment_id: response.razorpay_payment_id,
                        razorpay_signature: response.razorpay_signature
                    });
                    showToast("Payment verified successfully!");
                    showView("orders-view");
                    fetchOrders();
                } catch (err) {
                    // Handled
                }
            },
            prefill: {
                name: state.user?.full_name || "",
                email: state.user?.email || "",
                contact: state.user?.phone || ""
            },
            theme: {
                color: "#f59e0b"
            },
            modal: {
                ondismiss: function () {
                    showToast("Payment cancelled. Order remains pending.", "warning");
                    showView("orders-view");
                    fetchOrders();
                }
            }
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
    } catch (e) {
        showToast("Unable to initialize payment. Please try again.", "warning");
    }
}

async function fetchOrders() {
    if (!state.token || state.user?.role !== "customer") return;
    try {
        const orders = await apiCall("/orders");
        const list = document.getElementById("orders-list");
        
        if (orders.length === 0) {
            list.innerHTML = `<p style="color: var(--text-muted); font-size:16px; text-align:center; padding: 40px;">You have no active orders yet.</p>`;
            return;
        }

        // Fetch product details for each order to show products
        const detailedOrdersHtml = await Promise.all(orders.map(async (o) => {
            try {
                const details = await apiCall(`/orders/${o.order_id}`);
                const itemsHtml = details.products.map(item => `
                    <div class="order-product-row">
                        <span>${item.name} (x${item.quantity})</span>
                        <span>₹${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                `).join("");
                
                const isPending = o.status === "pending";
                
                return `
                    <div class="order-card">
                        <div class="order-card-header">
                            <div>
                                <span class="order-id">Order ID: #${o.order_id}</span>
                            </div>
                            <span class="order-status-badge badge-${o.status}">${o.status}</span>
                        </div>
                        <div class="order-card-body">
                            ${itemsHtml}
                        </div>
                        <div class="order-card-footer">
                            <span class="order-total-price">Total: ₹${o.total.toFixed(2)}</span>
                            ${isPending ? `<button class="btn btn-primary" onclick="triggerPaymentGate(${o.order_id})"><i class="fa-solid fa-wallet"></i> Pay Now</button>` : ''}
                        </div>
                    </div>
                `;
            } catch (err) {
                return "";
            }
        }));
        
        list.innerHTML = detailedOrdersHtml.join("");
    } catch (e) {
        // Handled
    }
}

// --- Provider Dashboard Logic ---
async function fetchProviderDashboard() {
    if (!state.token || state.user?.role !== "provider") return;
    try {
        const stats = await apiCall("/provider/dashboard");
        document.getElementById("prov-stat-products").innerText = stats.total_products;
        document.getElementById("prov-stat-orders").innerText = stats.total_orders;
        document.getElementById("prov-stat-sales").innerText = `₹${stats.total_sales.toFixed(2)}`;
        
        fetchProviderProducts();
        fetchProviderOrders();
    } catch (e) {
        // Handled
    }
}

async function fetchProviderProducts() {
    try {
        // Note: product endpoint list is public, we will get all products and filter for this provider
        const res = await apiCall("/products?limit=100");
        const tbody = document.getElementById("prov-products-tbody");
        
        // Filter products locally where image shows provider products (if API doesn't support provider filter)
        // Since get_products endpoint doesn't strictly allow provider_id filter, we'll display products loaded
        // For accurate catalog tracking, we display products
        tbody.innerHTML = res.data.map(p => `
            <tr>
                <td><img class="table-img" src="${p.image_url || 'https://placehold.co/40px'}" onerror="this.src='https://placehold.co/40px'"></td>
                <td><strong>${p.name}</strong></td>
                <td>₹${p.price.toFixed(2)}</td>
                <td>${p.stock_quantity ?? 0}</td>
                <td>
                    <button class="btn btn-icon btn-danger" onclick="deleteProviderProduct(${p.id})"><i class="fa-solid fa-trash-can"></i></button>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        // Handled
    }
}

async function deleteProviderProduct(id) {
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
        await apiCall(`/products/${id}`, "DELETE");
        showToast("Product deleted successfully");
        fetchProviderDashboard();
    } catch (e) {
        // Handled
    }
}

async function handleAddProduct(formData) {
    try {
        await apiCall("/products", "POST", formData, true);
        showToast("Product added to catalog!");
        closeModal("add-product-modal");
        fetchProviderDashboard();
        fetchProducts();
    } catch (e) {
        // Handled
    }
}

async function fetchProviderOrders() {
    try {
        const orders = await apiCall("/provider/orders");
        const tbody = document.getElementById("prov-orders-tbody");
        
        if (orders.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No orders placed yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = orders.map(o => `
            <tr>
                <td><strong>#${o.order_id}</strong></td>
                <td>${o.customer}</td>
                <td><span class="order-status-badge badge-${o.status}">${o.status}</span></td>
                <td>
                    <select class="btn btn-outline" style="padding:4px 8px; font-size:13px;" onchange="updateProviderOrderStatus(${o.order_id}, this.value)">
                        <option value="processing" ${o.status === 'processing' ? 'selected' : ''}>Processing</option>
                        <option value="shipped" ${o.status === 'shipped' ? 'selected' : ''}>Shipped</option>
                        <option value="delivered" ${o.status === 'delivered' ? 'selected' : ''}>Delivered</option>
                    </select>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        // Handled
    }
}

async function updateProviderOrderStatus(orderId, status) {
    try {
        await apiCall(`/provider/orders/${orderId}`, "PUT", { status });
        showToast("Order status updated successfully!");
        fetchProviderDashboard();
    } catch (e) {
        // Handled
    }
}

// --- Admin Dashboard Logic ---
async function fetchAdminDashboard() {
    if (!state.token || state.user?.role !== "admin") return;
    try {
        const stats = await apiCall("/admin/dashboard");
        document.getElementById("admin-stat-users").innerText = stats.total_users;
        document.getElementById("admin-stat-products").innerText = stats.total_products;
        document.getElementById("admin-stat-orders").innerText = stats.total_orders;
        document.getElementById("admin-stat-revenue").innerText = `₹${stats.total_revenue.toFixed(2)}`;
        
        fetchAdminUsers();
        fetchAdminProviders();
    } catch (e) {
        // Handled
    }
}

async function fetchAdminUsers() {
    try {
        const users = await apiCall("/admin/users");
        const tbody = document.getElementById("admin-customers-tbody");
        
        tbody.innerHTML = users.map(u => `
            <tr>
                <td>#${u.id}</td>
                <td><strong>${u.full_name}</strong></td>
                <td>${u.email}</td>
                <td>${u.phone || 'N/A'}</td>
                <td><span class="role-badge">${u.role || 'customer'}</span></td>
                <td><span class="status-toggle ${u.is_active ? 'active' : 'blocked'}">${u.is_active ? 'Active' : 'Blocked'}</span></td>
                <td>
                    <button class="btn ${u.is_active ? 'btn-danger' : 'btn-success'}" style="padding:6px 12px; font-size:12px;" onclick="toggleUserStatus(${u.id}, ${!u.is_active}, '${u.role || 'customer'}')">
                        ${u.is_active ? 'Block' : 'Unblock'}
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        // Handled
    }
}

async function fetchAdminProviders() {
    try {
        const providers = await apiCall("/admin/providers");
        const tbody = document.getElementById("admin-providers-tbody");
        
        tbody.innerHTML = providers.map(p => `
            <tr>
                <td>#${p.id}</td>
                <td><strong>${p.full_name}</strong></td>
                <td>${p.email}</td>
                <td>${p.phone || 'N/A'}</td>
                <td><span class="status-toggle ${p.is_active ? 'active' : 'blocked'}">${p.is_active ? 'Active' : 'Blocked'}</span></td>
                <td>
                    <button class="btn ${p.is_active ? 'btn-danger' : 'btn-success'}" style="padding:6px 12px; font-size:12px;" onclick="toggleUserStatus(${p.id}, ${!p.is_active}, 'provider')">
                        ${p.is_active ? 'Block' : 'Unblock/Approve'}
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (e) {
        // Handled
    }
}

async function toggleUserStatus(userId, newStatus, role) {
    try {
        await apiCall(`/admin/users/${userId}`, "PUT", { is_active: newStatus });
        showToast(`User account status modified!`);
        fetchAdminDashboard();
    } catch (e) {
        // Handled
    }
}

async function handleCreateCategory() {
    const input = document.getElementById("admin-category-name");
    const name = input.value.trim();
    if (!name) {
        showToast("Please enter a category name", "warning");
        return;
    }

    try {
        await apiCall("/admin/categories", "POST", { name });
        input.value = "";
        showToast("Category created successfully!");
        fetchCategories();
        renderAdminCategories();
    } catch (e) {
        // Handled
    }
}

function renderAdminCategories() {
    const container = document.getElementById("admin-categories-list");
    if (!container) return;

    const categories = state.categories || [];
    container.innerHTML = categories.length === 0
        ? '<span style="color: var(--text-muted);">No categories yet.</span>'
        : categories.map(cat => `
            <span class="category-pill active" style="cursor: default;">${cat.name}</span>
        `).join("");
}

// --- App Bootstrapper ---
function initApp() {
    // 1. Navbar displays based on auth state
    const homeLink = document.getElementById("nav-home");
    const ordersLink = document.getElementById("nav-orders");
    const provLink = document.getElementById("nav-provider-dashboard");
    const adminLink = document.getElementById("nav-admin-dashboard");
    const userMenu = document.getElementById("user-menu-area");
    
    // Hide all role links initially
    ordersLink.classList.add("hidden");
    provLink.classList.add("hidden");
    adminLink.classList.add("hidden");
    
    if (state.token && state.user) {
        // Logged In
        userMenu.innerHTML = `
            <div class="user-profile-menu" onclick="handleLogout()">
                <i class="fa-solid fa-user-gear"></i>
                <span>${state.user.full_name} (Sign Out)</span>
            </div>
        `;
        
        if (state.user.role === "customer") {
            ordersLink.classList.remove("hidden");
            fetchCart();
        } else if (state.user.role === "provider") {
            provLink.classList.remove("hidden");
            showView("provider-view");
            fetchProviderDashboard();
        } else if (state.user.role === "admin") {
            adminLink.classList.remove("hidden");
            showView("admin-view");
            fetchAdminDashboard();
        }
    } else {
        // Logged Out
        userMenu.innerHTML = `
            <button class="btn btn-outline" onclick="openModal('login-modal')">Login</button>
            <button class="btn btn-primary" onclick="openModal('register-modal')">Register</button>
        `;
        showView("home-view");
        openModal("login-modal");
        closeModal("register-modal");
        // Clear cart counts
        document.getElementById("cart-badge-count").innerText = "0";
    }

    // 2. Fetch Categories and Products
    fetchCategories().then(() => renderAdminCategories());
    fetchProducts();
}

// --- DOM Event Listeners ---
document.addEventListener("DOMContentLoaded", () => {
    // Nav view switching
    document.getElementById("nav-logo").onclick = (e) => { e.preventDefault(); showView("home-view"); };
    document.getElementById("nav-home").onclick = (e) => { e.preventDefault(); showView("home-view"); };
    document.getElementById("nav-orders").onclick = (e) => { e.preventDefault(); showView("orders-view"); fetchOrders(); };
    document.getElementById("nav-provider-dashboard").onclick = (e) => { e.preventDefault(); showView("provider-view"); fetchProviderDashboard(); };
    document.getElementById("nav-admin-dashboard").onclick = (e) => { e.preventDefault(); showView("admin-view"); fetchAdminDashboard(); };

    // Search bar functionality
    document.getElementById("search-btn").onclick = () => {
        state.searchQuery = document.getElementById("search-input").value;
        state.page = 1;
        fetchProducts();
    };
    document.getElementById("search-input").onkeypress = (e) => {
        if (e.key === "Enter") {
            state.searchQuery = document.getElementById("search-input").value;
            state.page = 1;
            fetchProducts();
        }
    };

    // Pagination controls
    document.getElementById("prev-page-btn").onclick = () => {
        if (state.page > 1) {
            state.page--;
            fetchProducts();
        }
    };
    document.getElementById("next-page-btn").onclick = () => {
        state.page++;
        fetchProducts();
    };

    // Cart Sidebar toggle
    document.getElementById("cart-toggle-btn").onclick = () => {
        document.getElementById("cart-drawer-overlay").classList.add("active");
    };
    document.getElementById("cart-close-btn").onclick = () => {
        document.getElementById("cart-drawer-overlay").classList.remove("active");
    };
    document.getElementById("cart-drawer-overlay").onclick = (e) => {
        if (e.target === document.getElementById("cart-drawer-overlay")) {
            document.getElementById("cart-drawer-overlay").classList.remove("active");
        }
    };
    document.getElementById("cart-checkout-btn").onclick = () => {
        document.getElementById("cart-drawer-overlay").classList.remove("active");
        openCheckout();
    };

    // Close Modals
    document.querySelectorAll(".modal-overlay").forEach(overlay => {
        overlay.onclick = (e) => {
            if (e.target === overlay) overlay.classList.remove("active");
        };
        const closeBtn = overlay.querySelector(".modal-close-btn");
        if (closeBtn) {
            closeBtn.onclick = () => overlay.classList.remove("active");
        }
    });

    // Login Form Submit
    document.getElementById("login-form").onsubmit = (e) => {
        e.preventDefault();
        const email = document.getElementById("login-email").value;
        const pass = document.getElementById("login-password").value;
        handleLogin(email, pass);
    };

    // Register Form Submit
    document.getElementById("register-form").onsubmit = (e) => {
        e.preventDefault();
        const name = document.getElementById("reg-name").value;
        const email = document.getElementById("reg-email").value;
        const phone = document.getElementById("reg-phone").value;
        const pass = document.getElementById("reg-password").value;
        const role = document.getElementById("reg-role").value;
        handleRegister(name, email, phone, pass, role);
    };

    // Product Detail quantity selector
    document.getElementById("qty-minus").onclick = () => {
        const input = document.getElementById("qty-input");
        if (input.value > 1) input.value = parseInt(input.value) - 1;
    };
    document.getElementById("qty-plus").onclick = () => {
        const input = document.getElementById("qty-input");
        input.value = parseInt(input.value) + 1;
    };

    // Address Addition Form Submit
    document.getElementById("checkout-add-address-btn").onclick = () => openModal("add-address-modal");
    document.getElementById("add-address-form").onsubmit = (e) => {
        e.preventDefault();
        handleAddAddress({
            address_line1: document.getElementById("addr-line1").value,
            address_line2: document.getElementById("addr-line2").value,
            city: document.getElementById("addr-city").value,
            state: document.getElementById("addr-state").value,
            country: document.getElementById("addr-country").value,
            postal_code: document.getElementById("addr-postal").value,
            is_default: document.getElementById("addr-default").checked
        });
    };

    // Place Order Button
    document.getElementById("place-order-btn").onclick = () => handlePlaceOrder();

    // Provider Tab Controls
    document.getElementById("tab-prov-products").onclick = (e) => {
        document.querySelectorAll("#provider-view .tab-btn").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.add("active");
        document.getElementById("prov-products-content").classList.remove("hidden");
        document.getElementById("prov-orders-content").classList.add("hidden");
    };
    document.getElementById("tab-prov-orders").onclick = (e) => {
        document.querySelectorAll("#provider-view .tab-btn").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.add("active");
        document.getElementById("prov-products-content").classList.add("hidden");
        document.getElementById("prov-orders-content").classList.remove("hidden");
    };

    // Add Product Form Trigger & Submit
    document.getElementById("add-product-trigger-btn").onclick = () => openModal("add-product-modal");
    document.getElementById("add-product-form").onsubmit = (e) => {
        e.preventDefault();
        
        const form = document.getElementById("add-product-form");
        const formData = new FormData();
        formData.append("name", document.getElementById("prod-name").value);
        formData.append("description", document.getElementById("prod-desc").value);
        formData.append("price", parseFloat(document.getElementById("prod-price").value));
        formData.append("stock_quantity", parseInt(document.getElementById("prod-stock").value));
        formData.append("category_id", parseInt(document.getElementById("prod-category").value));
        formData.append("image", document.getElementById("prod-image").files[0]);
        
        handleAddProduct(formData);
    };

    // Admin Category Creation
    document.getElementById("create-category-btn").onclick = () => handleCreateCategory();
    document.getElementById("admin-category-name").onkeypress = (e) => {
        if (e.key === "Enter") handleCreateCategory();
    };

    // Admin Category Creation
    const createCategoryBtn = document.getElementById("create-category-btn");
    if (createCategoryBtn) {
        createCategoryBtn.onclick = () => handleCreateCategory();
    }
    const adminCategoryName = document.getElementById("admin-category-name");
    if (adminCategoryName) {
        adminCategoryName.onkeypress = (e) => {
            if (e.key === "Enter") handleCreateCategory();
        };
    }

    // Admin Tab Controls
    document.getElementById("tab-admin-customers").onclick = (e) => {
        document.querySelectorAll("#admin-view .tab-btn").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.add("active");
        document.getElementById("admin-customers-content").classList.remove("hidden");
        document.getElementById("admin-providers-content").classList.add("hidden");
    };
    document.getElementById("tab-admin-providers").onclick = (e) => {
        document.querySelectorAll("#admin-view .tab-btn").forEach(b => b.classList.remove("active"));
        e.currentTarget.classList.add("active");
        document.getElementById("admin-customers-content").classList.add("hidden");
        document.getElementById("admin-providers-content").classList.remove("hidden");
    };

    // Initialize application state
    initApp();
});
