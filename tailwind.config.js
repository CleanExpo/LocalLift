module.exports = {
  content: [
    "./templates/**/*.html", // For backend-rendered templates
    "./public/**/*.html",    // Add this to scan static HTML files in public/
    "./public/**/*.js",      // Add this to scan JS files in public/ for potential classes
    "./**/*.py",
    "./frontend/**/*.{js,ts,jsx,tsx}" // Keep this if you have a separate frontend source dir
  ],
  theme: { 
    extend: {
      colors: {
        primary: {
          50: '#e6f1ff',
          100: '#cce4ff',
          200: '#99c8ff',
          300: '#66adff',
          400: '#3391ff',
          500: '#0076ff',
          600: '#005ecc',
          700: '#004799',
          800: '#002f66',
          900: '#001833',
        },
        secondary: {
          50: '#f2fcf5',
          100: '#e6f9eb',
          200: '#ccf4d6',
          300: '#b3eec2',
          400: '#99e8ad',
          500: '#80e299',
          600: '#66b57a',
          700: '#4d885c',
          800: '#335b3d',
          900: '#1a2d1f',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Poppins', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 8px rgba(0, 0, 0, 0.05)',
        dropdown: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    }
  },
  plugins: [],
}
