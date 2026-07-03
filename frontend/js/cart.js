(function () {
    const cart = {
        async fetchCart() {
            if (!window.state?.token || window.state?.user?.role !== "customer") return;
            if (typeof window.apiCall !== "function") return;
            try {
                const cartData = await window.apiCall("/cart");
                window.state.cart = cartData;
                if (typeof window.renderCartUI === "function") {
                    window.renderCartUI();
                }
            } catch (error) {
                console.error(error);
            }
        },

        async addProductToCart(productId, quantity = 1) {
            if (!window.state?.token) {
                if (typeof window.showToast === "function") {
                    window.showToast("Please login as a customer to add items to cart", "warning");
                }
                if (typeof window.openModal === "function") {
                    window.openModal("login-modal");
                }
                return;
            }

            if (window.state?.user?.role !== "customer") {
                if (typeof window.showToast === "function") {
                    window.showToast("Sellers and admins cannot use the shopping cart", "warning");
                }
                return;
            }

            if (typeof window.apiCall === "function") {
                await window.apiCall("/cart", "POST", { product_id: productId, quantity });
                if (typeof window.showToast === "function") {
                    window.showToast("Product added to cart!");
                }
                if (typeof window.closeModal === "function") {
                    window.closeModal("product-detail-modal");
                }
                await this.fetchCart();
            }
        },

        async updateCartItemQty(itemId, newQty) {
            if (typeof window.apiCall !== "function") return;
            if (newQty < 1) {
                return this.removeCartItem(itemId);
            }
            await window.apiCall(`/cart/${itemId}`, "PUT", { quantity: newQty });
            await this.fetchCart();
        },

        async removeCartItem(itemId) {
            if (typeof window.apiCall !== "function") return;
            await window.apiCall(`/cart/${itemId}`, "DELETE");
            if (typeof window.showToast === "function") {
                window.showToast("Item removed from cart");
            }
            await this.fetchCart();
        },

        openCheckout() {
            if (window.state?.cart?.items?.length === 0) {
                if (typeof window.showToast === "function") {
                    window.showToast("Your cart is empty", "warning");
                }
                return;
            }
            if (typeof window.openCheckout === "function") {
                window.openCheckout();
            }
        }
    };

    window.frontendCart = cart;
    window.addProductToCart = cart.addProductToCart;
    window.updateCartItemQty = cart.updateCartItemQty;
    window.removeCartItem = cart.removeCartItem;
})();
