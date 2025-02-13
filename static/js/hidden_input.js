document.addEventListener("DOMContentLoaded", function () {
    const searchIcon = document.getElementById("search-icon");
    const searchBar = document.getElementById("search-bar");
    let hideTimeout;

    searchIcon.addEventListener("click", function (event) {
        event.preventDefault();

        if (!searchBar.classList.contains("show")) {
            searchBar.classList.add("show");
            searchBar.focus();
        }

        clearTimeout(hideTimeout);
        hideTimeout = setTimeout(() => {
            if (!searchBar.value.trim()) {
                searchBar.classList.remove("show");
            }
        }, 6000);
    });

    searchBar.addEventListener("input", function () {
        clearTimeout(hideTimeout);
    });

    searchBar.addEventListener("blur", function () {
        hideTimeout = setTimeout(() => {
            if (!searchBar.value.trim()) {
                searchBar.classList.remove("show");
            }
        }, 6000);
    });
});