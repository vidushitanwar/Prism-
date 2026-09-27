/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Original PRISM palette — deep space-graph tones with a prism
        // accent spectrum, deliberately not a generic SaaS blue.
        prism: {
          950: "#06070d",
          900: "#0b0d17",
          800: "#12162a",
          700: "#1c2140",
          600: "#2a3160",
          500: "#4750a3",
          400: "#7c85d4",
          300: "#aab1ea",
          100: "#e7e9fb",
        },
        spectrum: {
          violet: "#8b5cf6",
          cyan: "#22d3ee",
          amber: "#f59e0b",
          rose: "#fb7185",
          emerald: "#34d399",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["'Inter'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      backgroundImage: {
        "prism-radial":
          "radial-gradient(circle at 20% 20%, rgba(139,92,246,0.18), transparent 40%), radial-gradient(circle at 80% 0%, rgba(34,211,238,0.14), transparent 45%), radial-gradient(circle at 50% 100%, rgba(245,158,11,0.10), transparent 40%)",
      },
    },
  },
  plugins: [],
};
