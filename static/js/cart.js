const ShopApp = {
    // Configuration
    config: {
        selectors: {
            favoriteBtn: '.favorite-btn',
            cartBtn: '.add-to-cart-btn',
            toast: '#notification-toast',
            toastMessage: '.toast-message'
        },
        urls: {
            login: '/login/',
            cart: '/cart/',
            toggleFavorite: (id) => `/toggle-favorite/${id}/`,
            addToCart: (id) => `/cart/add/${id}/`
        },
        notificationDuration: 3000
    },

    // Initialisation
    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initFavoriteButtons();
            this.initCartButtons();
        });
    },

    // Gestionnaires d'événements
    initFavoriteButtons() {
        document.querySelectorAll(this.config.selectors.favoriteBtn)
            .forEach(button => button.addEventListener('click', this.handleFavoriteClick.bind(this)));
    },

    initCartButtons() {
        document.querySelectorAll(this.config.selectors.cartBtn)
            .forEach(button => button.addEventListener('click', this.handleCartClick.bind(this)));
    },

    // Utilitaires
    utils: {
        getCookie(name) {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
        },

        async fetchWithAuth(url, options = {}) {
            const defaultOptions = {
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            };

            return fetch(url, { ...defaultOptions, ...options });
        },

        showNotification(message, type = 'success') {
            const toast = document.querySelector(ShopApp.config.selectors.toast);
            if (!toast) return;

            const messageElement = toast.querySelector(ShopApp.config.selectors.toastMessage);
            toast.className = `toast-container ${type}`;
            messageElement.textContent = message;
            toast.style.display = 'block';

            setTimeout(() => {
                toast.style.display = 'none';
            }, ShopApp.config.notificationDuration);
        }
    },

    // Gestionnaires d'actions
    async handleFavoriteClick(event) {
        const button = event.currentTarget;
        const { productId } = button.dataset;
        const currentIsFavorite = button.dataset.isFavorite === 'true';

        button.style.pointerEvents = 'none';

        try {
            const response = await this.utils.fetchWithAuth(
                this.config.urls.toggleFavorite(productId),
                { method: 'POST' }
            );
            const data = await response.json();

            if (data.status === 'success') {
                this.updateFavoriteButtons(productId, !currentIsFavorite);
            }
        } catch (error) {
            console.error('Error:', error);
            this.utils.showNotification('Une erreur est survenue', 'error');
        } finally {
            button.style.pointerEvents = 'auto';
        }
    },

    async handleCartClick(event) {
        const button = event.currentTarget;
        const { productId } = button.dataset;

        button.disabled = true;

        try {
            const response = await this.utils.fetchWithAuth(
                this.config.urls.addToCart(productId),
                { method: 'POST' }
            );

            if (response.ok) {
                this.utils.showNotification('Produit ajouté au panier avec succès');
                setTimeout(() => {
                    window.location.href = this.config.urls.cart;
                }, 1000);
            } else {
                throw new Error('Erreur lors de l\'ajout au panier');
            }
        } catch (error) {
            console.error('Error:', error);
            this.utils.showNotification('Erreur lors de l\'ajout au panier', 'error');
        } finally {
            button.disabled = false;
        }
    },

    updateFavoriteButtons(productId, isFavorite) {
        document.querySelectorAll(`${this.config.selectors.favoriteBtn}[data-product-id="${productId}"]`)
            .forEach(button => {
                const icon = button.querySelector('i');
                const text = button.querySelector('p');

                icon.classList.remove('fa-heart', 'fa-heart-o');
                icon.classList.add(isFavorite ? 'fa-heart' : 'fa-heart-o');
                text.textContent = isFavorite ? 'Retirer des favoris' : 'favoris';
                button.dataset.isFavorite = isFavorite.toString();
            });
    }
};

// Fonctions utilitaires globales
const redirectToLogin = () => window.location.href = ShopApp.config.urls.login;

// Initialisation de l'application
ShopApp.init();