(function () {
    const products = {
        async fetchCategories() {
            if (typeof window.apiCall !== "function") return [];
            try {
                const categories = await window.apiCall("/com/categories");
                window.state.categories = categories;
                return categories;
            } catch (error) {
                return [];
            }
        },

        async fetchProducts(page = 1, limit = 8, category = null, search = "") {
            if (typeof window.apiCall !== "function") return [];
            let url = `/products?page=${page}&limit=${limit}`;
            if (category) url += `&category=${category}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            const result = await window.apiCall(url);
            return result.data || [];
        },

        renderProducts(productsList) {
            const grid = document.getElementById("products-grid-container");
            if (!grid) return;
            if (!productsList.length) {
                grid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align:center; padding:40px; color: var(--text-muted);">
                        <h3>No products found for this selection</h3>
                    </div>
                `;
                return;
            }

            grid.innerHTML = productsList.map(prod => `
                <div class="product-card" onclick="window.viewProductDetails(${prod.id})">
                    <div class="product-img-wrapper">
                        <img src="${prod.image_url || '/uploads/products/placeholder.png'}" alt="${prod.name}" onerror="this.src='https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image'">
                    </div>
                    <div class="product-info">
                        <h4 class="product-title">${prod.name}</h4>
                        <p class="product-desc-excerpt">${prod.description || 'No description provided.'}</p>
                        <div class="product-footer">
                            <span class="product-price">₹${Number(prod.price || 0).toFixed(2)}</span>
                            <button class="btn-icon" onclick="event.stopPropagation(); window.addProductToCart(${prod.id}, 1);"><i class="fa-solid fa-cart-plus"></i></button>
                        </div>
                    </div>
                </div>
            `).join("");
        },

        async viewProductDetails(productId) {
            if (typeof window.apiCall !== "function") return;
            try {
                const prod = await window.apiCall(`/products/${productId}`);
                const category = window.state?.categories?.find(cat => cat.id === prod.category_id);
                document.getElementById("modal-product-name").innerText = prod.name;
                document.getElementById("modal-product-title-detail").innerText = prod.name;
                document.getElementById("modal-product-desc").innerText = prod.description || "No description provided.";
                document.getElementById("modal-product-price").innerText = `₹${Number(prod.price || 0).toFixed(2)}`;
                document.getElementById("modal-product-stock").innerText = `In Stock: ${prod.stock_quantity}`;
                document.getElementById("modal-product-category").innerText = category ? category.name : "Products";

                const img = document.getElementById("modal-product-img");
                img.src = prod.image_url || "https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image";
                img.onerror = () => {
                    img.src = "https://placehold.co/400x400/161c2d/f4f6fa?text=No+Image";
                };
                document.getElementById("qty-input").value = 1;

                const addBtn = document.getElementById("modal-add-to-cart-btn");
                addBtn.onclick = () => {
                    const qty = parseInt(document.getElementById("qty-input").value, 10) || 1;
                    window.addProductToCart(prod.id, qty);
                };

                if (typeof window.openModal === "function") {
                    window.openModal("product-detail-modal");
                }
            } catch (error) {
                console.error(error);
            }
        }
    };

    window.frontendProducts = products;
    window.viewProductDetails = products.viewProductDetails;
})();
