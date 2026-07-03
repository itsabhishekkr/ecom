(function () {
    const dashboard = {
        async fetchProviderDashboard() {
            if (!window.state?.token || window.state?.user?.role !== "provider") return;
            if (typeof window.apiCall !== "function") return;
            try {
                const stats = await window.apiCall("/provider/dashboard");
                document.getElementById("prov-stat-products").innerText = stats.total_products;
                document.getElementById("prov-stat-orders").innerText = stats.total_orders;
                document.getElementById("prov-stat-sales").innerText = `₹${Number(stats.total_sales || 0).toFixed(2)}`;
            } catch (error) {
                console.error(error);
            }
        },

        async fetchAdminDashboard() {
            if (!window.state?.token || window.state?.user?.role !== "admin") return;
            if (typeof window.apiCall !== "function") return;
            try {
                const stats = await window.apiCall("/admin/dashboard");
                document.getElementById("admin-stat-users").innerText = stats.total_users;
                document.getElementById("admin-stat-products").innerText = stats.total_products;
                document.getElementById("admin-stat-orders").innerText = stats.total_orders;
                document.getElementById("admin-stat-revenue").innerText = `₹${Number(stats.total_revenue || 0).toFixed(2)}`;
            } catch (error) {
                console.error(error);
            }
        }
    };

    window.frontendDashboard = dashboard;
})();
