module.exports = {
  env: {
    browser: true,
    es2021: true
  },
  extends: [
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'standard-with-typescript',
    'plugin:jsx-a11y/recommended'
  ],
  ignorePatterns: [
    'vite*.ts'
  ],
  overrides: [
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    tsconfigRootDir: __dirname,
    project: './tsconfig.json'
  },
  plugins: [
    'react',
    'react-refresh'
  ],
  rules: {
    '@typescript-eslint/ban-types': [
      'error',
      {
        types: {
          Function: false
        },
        extendDefaults: true
      }
    ],
    '@typescript-eslint/ban-tslint-comment': 'off',
    'react-refresh/only-export-components': 'warn',
    'react/prop-types': 'off'
  },
  settings: {
    react: {
      version: 'detect'
    }
  }
}
