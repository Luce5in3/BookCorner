/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Nike 设计系统 - Primary
        'nike-black': '#111111',
        'nike-white': '#FFFFFF',
        
        // Surface & Background
        'snow': '#FAFAFA',
        'light-gray': '#F5F5F5',
        'hover-gray': '#E5E5E5',
        'dark-surface': '#28282A',
        'deep-charcoal': '#1F1F21',
        'dark-hover': '#39393B',
        
        // Neutrals & Text
        'text-primary': '#111111',
        'text-secondary': '#707072',
        'text-disabled': '#9E9EA0',
        'disabled-inverse': '#4B4B4D',
        'border-primary': '#707072',
        'border-secondary': '#CACACB',
        'border-active': '#111111',
        
        // Semantic & Accent
        'nike-red': '#D30005',
        'bright-red': '#EE0005',
        'nike-orange': '#D33918',
        'orange-flash': '#FF5000',
        'success-green': '#007D48',
        'success-inverse': '#1EAA52',
        'link-blue': '#1151FF',
        'info-inverse': '#1190FF',
        'warning-yellow': '#FEDF35',
        'focus-ring': 'rgba(39, 93, 197, 1)',
        
        // Grey Scale
        'grey-50': '#FAFAFA',
        'grey-100': '#F5F5F5',
        'grey-200': '#E5E5E5',
        'grey-300': '#CACACB',
        'grey-400': '#9E9EA0',
        'grey-500': '#707072',
        'grey-600': '#555555',
        'grey-700': '#39393B',
        'grey-800': '#28282A',
        'grey-900': '#1F1F21',
      },
      fontFamily: {
        'display': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
        'heading': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
        'body': ['Helvetica Neue', 'Helvetica', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'display': ['96px', { lineHeight: '0.90', fontWeight: '500' }],
        'display-sm': ['64px', { lineHeight: '0.95', fontWeight: '500' }],
        'display-xs': ['48px', { lineHeight: '1.0', fontWeight: '500' }],
        'h1': ['32px', { lineHeight: '1.20', fontWeight: '500' }],
        'h2': ['24px', { lineHeight: '1.20', fontWeight: '500' }],
        'h3': ['16px', { lineHeight: '1.50', fontWeight: '500' }],
        'body': ['16px', { lineHeight: '1.75', fontWeight: '400' }],
        'body-medium': ['16px', { lineHeight: '1.75', fontWeight: '500' }],
        'link': ['16px', { lineHeight: '1.75', fontWeight: '500' }],
        'link-sm': ['14px', { lineHeight: '1.86', fontWeight: '500' }],
        'button': ['16px', { lineHeight: '1.50', fontWeight: '500' }],
        'button-sm': ['14px', { lineHeight: '1.50', fontWeight: '500' }],
        'caption': ['14px', { lineHeight: '1.50', fontWeight: '500' }],
        'small': ['12px', { lineHeight: '1.50', fontWeight: '500' }],
        'tiny': ['12px', { lineHeight: '1.50', fontWeight: '400' }],
      },
      borderRadius: {
        'pill': '30px',
        'card': '20px',
        'input': '8px',
        'search': '24px',
        'small': '18px',
      },
      spacing: {
        '1': '4px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '7': '32px',
        '8': '48px',
        '9': '64px',
        '10': '80px',
      },
      boxShadow: {
        'none': 'none',
        'focus': '0 0 0 2px rgba(39, 93, 197, 1)',
        'divider': '0px -1px 0px 0px #E5E5E5 inset',
      },
      transitionTimingFunction: {
        'nike': '200ms ease',
      },
    },
  },
  plugins: [],
}
