// ===== SEARCH (len na index stránke) =====
const searchInput = document.querySelector(".search-input");

if (searchInput) {
    searchInput.addEventListener("input", () => {
        const value = searchInput.value.toLowerCase().trim();
        const cards = document.querySelectorAll(".person-card");

        cards.forEach(card => {
            const name = card.querySelector(".person-name").textContent.toLowerCase();
            card.style.display = name.includes(value) ? "" : "none";
        });
    });
}
