/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Apple Design System - Primary
        'apple-black': '#000000',
        'apple-white': '#FFFFFF',

        // Surface & Background
        'apple-gray': '#f5f5f7',
        'near-black': '#1d1d1f',

        // Dark Surfaces
        'dark-surface-1': '#272729',
        'dark-surface-2': '#262628',
        'dark-surface-3': '#28282a',
        'dark-surface-4': '#2a2a2d',
        'dark-surface-5': '#242426',

        // Interactive
        'apple-blue': '#0071e3',
        'link-blue': '#0066cc',
        'bright-blue': '#2997ff',

        // Text
        'text-primary': '#1d1d1f',
        'text-secondary': 'rgba(0, 0, 0, 0.8)',
        'text-tertiary': 'rgba(0, 0, 0, 0.48)',

        // Button States
        'btn-active': '#ededf2',
        'btn-default-light': '#fafafc',
        'overlay': 'rgba(210, 210, 215, 0.64)',

        // Semantic
        'success-green': '#007D48',
        'warning-yellow': '#FEDF35',
        'danger-red': '#FF3B30',
      },
      fontFamily: {
        'display': ['-apple-system', 'SF Pro Display', 'SF Pro Icons', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
        'body': ['-apple-system', 'SF Pro Text', 'SF Pro Icons', 'Helvetica Neue', 'Helvetica', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Arial', 'sans-serif'],
      },
      fontSize: {
        'display-hero': ['56px', { lineHeight: '1.07', fontWeight: '600', letterSpacing: '-0.28px' }],
        'section-heading': ['40px', { lineHeight: '1.10', fontWeight: '600' }],
        'tile-heading': ['28px', { lineHeight: '1.14', fontWeight: '400', letterSpacing: '0.196px' }],
        'card-title': ['21px', { lineHeight: '1.19', fontWeight: '700', letterSpacing: '0.231px' }],
        'sub-heading': ['21px', { lineHeight: '1.19', fontWeight: '400', letterSpacing: '0.231px' }],
        'nav-heading': ['34px', { lineHeight: '1.47', fontWeight: '600', letterSpacing: '-0.374px' }],
        'sub-nav': ['24px', { lineHeight: '1.50', fontWeight: '300' }],
        'body': ['17px', { lineHeight: '1.47', fontWeight: '400', letterSpacing: '-0.374px' }],
        'body-emphasis': ['17px', { lineHeight: '1.24', fontWeight: '600', letterSpacing: '-0.374px' }],
        'button-lg': ['18px', { lineHeight: '1.00', fontWeight: '300' }],
        'button': ['17px', { lineHeight: '2.41', fontWeight: '400' }],
        'link': ['14px', { lineHeight: '1.43', fontWeight: '400', letterSpacing: '-0.224px' }],
        'caption': ['14px', { lineHeight: '1.29', fontWeight: '400', letterSpacing: '-0.224px' }],
        'caption-bold': ['14px', { lineHeight: '1.29', fontWeight: '600', letterSpacing: '-0.224px' }],
        'micro': ['12px', { lineHeight: '1.33', fontWeight: '400', letterSpacing: '-0.12px' }],
        'micro-bold': ['12px', { lineHeight: '1.33', fontWeight: '600', letterSpacing: '-0.12px' }],
        'nano': ['10px', { lineHeight: '1.47', fontWeight: '400', letterSpacing: '-0.08px' }],
      },
      borderRadius: {
        'micro': '5px',
        'standard': '8px',
        'comfortable': '11px',
        'large': '12px',
        'pill': '980px',
        'circle': '50%',
      },
      spacing: {
        '1': '2px',
        '2': '4px',
        '3': '5px',
        '4': '6px',
        '5': '7px',
        '6': '8px',
        '7': '9px',
        '8': '10px',
        '9': '11px',
        '10': '14px',
        '11': '15px',
        '12': '17px',
        '13': '20px',
        '14': '24px',
      },
      boxShadow: {
        'card': 'rgba(0, 0, 0, 0.22) 3px 5px 30px 0px',
        'focus': '0 0 0 2px #0071e3',
        'nav': '0 1px 0 rgba(0, 0, 0, 0.1)',
      },
      transitionTimingFunction: {
        'apple': '200ms ease',
      },
      backdropBlur: {
        'nav': '20px',
      },
    },
  },
  plugins: [],
}
