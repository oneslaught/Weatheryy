const options = document.querySelectorAll(".theme-switch button");

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  options.forEach((option) => {
    option.classList.toggle("active", option.dataset.themeValue === theme);
  });
  document.cookie =
    document.cookie = `theme=${theme}; path=/; max-age=31536000; samesite=lax`;
}

options.forEach((option) => {
  option.addEventListener("click", () => applyTheme(option.dataset.themeValue));
});
