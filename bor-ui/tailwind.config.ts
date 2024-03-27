import type { Config } from 'tailwindcss'

export default <Partial<Config>>{
  theme: {
    extend: {
      boxShadow: {
        'action-col-header': '-2px 0 4px -1px #adb5bd',
        'action-col-item': '-1px 0 4px 0 #adb5bd'
      },
      colors: {
        gray: {
          50: '#f8f9fa',
          100: '#f1f3f5',
          200: '#e9ecef',
          300: '#dee2e6',
          400: '#ced4da',
          500: '#adb5bd',
          600: '#868e96',
          700: '#495057',
          800: '#343a40',
          900: '#212529',
          950: '#232529'
        },
        blue: {
          50: '#e0e7ed',
          100: '#b3c2d1',
          200: '#8099b3',
          300: '#4d7094',
          350: '#38598a',
          400: '#26527d',
          500: '#1669bb',
          600: '#125192',
          700: '#002e5e',
          800: '#002753',
          900: '#002049',
          950: '#001438'
        },
        red: {
          50: '#FAE5E6',
          100: '#F2BEC0',
          200: '#E99396',
          300: '#E0686B',
          400: '#DA474C',
          500: '#D3272C',
          600: '#CE2327',
          700: '#C81D21',
          800: '#C2171B',
          900: '#B70E10',
          950: '#961E21'
        }
      }
    }
  }
}
