(function () {
    const auth = {
        async login(email, password) {
            if (typeof window.apiCall === "function") {
                return window.apiCall("/auth/login", "POST", { email, password });
            }
            throw new Error("Authentication service is unavailable");
        },

        async register(name, email, phone, password, role) {
            if (typeof window.apiCall === "function") {
                return window.apiCall("/auth/register", "POST", {
                    full_name: name,
                    email,
                    phone,
                    password,
                    role
                });
            }
            throw new Error("Authentication service is unavailable");
        },

        logout() {
            if (typeof window.handleLogout === "function") {
                return window.handleLogout();
            }
            return null;
        },

        updateAuthUI() {
            const userMenu = document.getElementById("user-menu-area");
            if (!userMenu) return;

            const currentUser = window.state?.user;
            if (window.state?.token && currentUser) {
                userMenu.innerHTML = `
                    <div class="user-profile-menu" onclick="window.frontendAuth.logout()">
                        <i class="fa-solid fa-user-gear"></i>
                        <span>${currentUser.full_name || currentUser.email} (Sign Out)</span>
                    </div>
                `;
            } else {
                userMenu.innerHTML = `
                    <button class="btn btn-outline" onclick="window.openModal('login-modal')">Login</button>
                    <button class="btn btn-primary" onclick="window.openModal('register-modal')">Register</button>
                `;
            }
        }
    };

    window.frontendAuth = auth;
})();
