(function () {
  function syncScrollState() {
    if (!document.body) {
      return;
    }

    document.body.classList.toggle("cavise-scrolled", window.scrollY > 12);
  }

  function formatCompactNumber(value) {
    if (!Number.isFinite(value)) {
      return "--";
    }

    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1).replace(/\.0$/, "")}M`;
    }

    if (value >= 1000) {
      return `${(value / 1000).toFixed(1).replace(/\.0$/, "")}k`;
    }

    return String(value);
  }

  async function hydrateGitHubStats() {
    const githubBadge = document.querySelector("[data-github-api]");
    if (!githubBadge) {
      return;
    }

    const apiUrl = githubBadge.getAttribute("data-github-api");
    if (!apiUrl) {
      return;
    }

    try {
      const response = await fetch(apiUrl, {
        headers: {
          Accept: "application/vnd.github+json",
        },
      });

      if (!response.ok) {
        return;
      }

      const data = await response.json();
      const releaseTarget = githubBadge.querySelector("[data-github-release]");
      const starsTarget = githubBadge.querySelector("[data-github-stars]");
      const forksTarget = githubBadge.querySelector("[data-github-forks]");

      let releaseLabel = null;

      try {
        const releaseResponse = await fetch(`${apiUrl}/releases/latest`, {
          headers: {
            Accept: "application/vnd.github+json",
          },
        });

        if (releaseResponse.ok) {
          const releaseData = await releaseResponse.json();
          releaseLabel = releaseData.tag_name || releaseData.name;
        } else {
          const tagsResponse = await fetch(`${apiUrl}/tags?per_page=1`, {
            headers: {
              Accept: "application/vnd.github+json",
            },
          });

          if (tagsResponse.ok) {
            const tagsData = await tagsResponse.json();
            if (Array.isArray(tagsData) && tagsData.length > 0) {
              releaseLabel = tagsData[0].name;
            }
          }
        }
      } catch (_error) {
        // Keep placeholder if the release lookup is unavailable.
      }

      if (releaseTarget && releaseLabel) {
        releaseTarget.textContent = releaseLabel;
      }

      if (starsTarget) {
        starsTarget.textContent = formatCompactNumber(data.stargazers_count);
      }

      if (forksTarget) {
        forksTarget.textContent = formatCompactNumber(data.forks_count);
      }
    } catch (_error) {
      // Keep placeholders if the GitHub API is unavailable.
    }
  }

  function initSidebarToggle() {
    const toggle = document.querySelector("[data-cavise-sidebar-toggle]");
    if (!toggle || !document.body) {
      return;
    }

    const desktopQuery = window.matchMedia("(min-width: 769px)");
    const compactDesktopQuery = window.matchMedia("(max-width: 1280px)");
    let sidebarOverride = null;

    function syncSidebarState() {
      if (!desktopQuery.matches) {
        document.body.classList.remove("cavise-sidebar-collapsed");
        toggle.setAttribute("aria-expanded", "false");
        return;
      }

      let collapsed = compactDesktopQuery.matches;
      if (sidebarOverride === "open") {
        collapsed = false;
      } else if (sidebarOverride === "closed") {
        collapsed = true;
      }

      document.body.classList.toggle("cavise-sidebar-collapsed", collapsed);
      toggle.setAttribute("aria-expanded", String(!collapsed));
    }

    toggle.addEventListener("click", function () {
      if (!desktopQuery.matches) {
        return;
      }

      sidebarOverride = document.body.classList.contains("cavise-sidebar-collapsed")
        ? "open"
        : "closed";
      syncSidebarState();
    });

    function resetSidebarState() {
      sidebarOverride = null;
      syncSidebarState();
    }

    desktopQuery.addEventListener("change", resetSidebarState);
    compactDesktopQuery.addEventListener("change", resetSidebarState);

    syncSidebarState();
  }

  function formatCodeLanguage(language) {
    const normalized = (language || "").toLowerCase();
    const map = {
      bash: "Bash",
      shell: "Shell",
      sh: "Shell",
      zsh: "Shell",
      python: "Python",
      py: "Python",
      yaml: "YAML",
      yml: "YAML",
      json: "JSON",
      toml: "TOML",
      ini: "INI",
      xml: "XML",
      html: "HTML",
      css: "CSS",
      javascript: "JavaScript",
      js: "JavaScript",
      typescript: "TypeScript",
      ts: "TypeScript",
      cpp: "C++",
      cxx: "C++",
      c: "C",
      cmake: "CMake",
      text: "Text",
      console: "Console",
    };

    if (map[normalized]) {
      return map[normalized];
    }

    if (!normalized) {
      return "Code";
    }

    return normalized.charAt(0).toUpperCase() + normalized.slice(1);
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    textarea.remove();
  }

  function initCodeBlocks() {
    const blocks = document.querySelectorAll('.rst-content div[class^="highlight-"]');
    if (!blocks.length) {
      return;
    }

    blocks.forEach((block) => {
      const className = Array.from(block.classList).find((name) =>
        name.startsWith("highlight-"),
      );
      const language = className ? className.replace("highlight-", "") : "code";
      const formattedLanguage = formatCodeLanguage(language);

      if (block.querySelector(".cavise-code-header")) {
        return;
      }

      const pre = block.querySelector("pre");
      if (!pre) {
        return;
      }

      const header = document.createElement("div");
      header.className = "cavise-code-header";

      const languageLabel = document.createElement("span");
      languageLabel.className = "cavise-code-language";
      languageLabel.textContent = formattedLanguage;

      const button = document.createElement("button");
      button.type = "button";
      button.className = "cavise-code-copy";
      button.textContent = "Copy";

      button.addEventListener("click", async () => {
        try {
          await copyText(pre.innerText);
          button.textContent = "Copied";
          button.classList.add("is-copied");
          window.setTimeout(() => {
            button.textContent = "Copy";
            button.classList.remove("is-copied");
          }, 1600);
        } catch (_error) {
          button.textContent = "Failed";
          window.setTimeout(() => {
            button.textContent = "Copy";
          }, 1600);
        }
      });

      header.appendChild(languageLabel);
      header.appendChild(button);
      block.insertBefore(header, block.firstChild);
    });
  }

  function initTheme() {
    syncScrollState();
    window.addEventListener("scroll", syncScrollState, { passive: true });
    initSidebarToggle();
    initCodeBlocks();
    hydrateGitHubStats();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme, { once: true });
  } else {
    initTheme();
  }
})();
