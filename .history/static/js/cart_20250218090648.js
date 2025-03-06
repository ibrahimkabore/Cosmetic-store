// Namespace pour notre application
const ShopApp = {
 
    // Gestionnaire d'initialisation
    init: function() {
        this.initEventListeners();
    },

    // Initialisation des écouteurs d'événements
    initEventListeners: function() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initFavoriteButtons();
            this.initCartButtons();
        });
    },

    // Gestionnaire des favoris
    initFavoriteButtons: function() {
        document.querySelectorAll('.favorite-btn').forEach(button => {
            button.addEventListener('click', this.handleFavoriteClick.bind(this));
        });
    },

    // Gestionnaire du panier
    initCartButtons: function() {
        document.querySelectorAll('.add-to-cart-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                const productId = event.currentTarget.dataset.productId;
                this.addToCart(productId);
            });
        });
    },

    // Méthodes utilitaires
    utils: {
        getCookie: function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        showNotification: function(message, type = 'success') {
            const toast = document.getElementById('notification-toast');
            if (!toast) return;

            const messageElement = toast.querySelector('.toast-message');
            toast.className = `toast-container ${type}`;
            messageElement.textContent = message;
            toast.style.display = 'block';

            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
    },

    // Gestion des favoris
    handleFavoriteClick: function(event) {
        const button = event.currentTarget;
        const productId = button.dataset.productId;
        const currentIsFavorite = button.dataset.isFavorite === 'true';

        button.style.pointerEvents = 'none';

        fetch(`/toggle-favorite/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.utils.getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.updateFavoriteButtons(productId, !currentIsFavorite);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.utils.showNotification('Une erreur est survenue', 'error');
        })
        .finally(() => {
            button.style.pointerEvents = 'auto';
        });
    },

    // Mise à jour des boutons favoris
    updateFavoriteButtons: function(productId, isFavorite) {
        document.querySelectorAll(`.favorite-btn[data-product-id="${productId}"]`)
            .forEach(button => {
                const icon = button.querySelector('i');
                const text = button.querySelector('p');

                icon.classList.remove('fa-heart', 'fa-heart-o');
                icon.classList.add(isFavorite ? 'fa-heart' : 'fa-heart-o');
                text.textContent = isFavorite ? 'Retirer des favoris' : 'favoris';
                button.dataset.isFavorite = isFavorite.toString();
            });
    },

    // Gestion du panier
    addToCart: function(productId) {
        const button = document.querySelector(`.add-to-cart-btn[data-product-id="${productId}"]`);
        if (!button) return;

        button.disabled = true;

        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.utils.getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                this.utils.showNotification('Produit ajouté au panier avec succès');
                window.location.href = '/cart/';
            } else {
                throw new Error('Erreur lors de l\'ajout au panier');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.utils.showNotification('Erreur lors de l\'ajout au panier', 'error');
        })
        .finally(() => {
            button.disabled = false;
        });
    }
};

// Initialisation de l'application
ShopApp.init();