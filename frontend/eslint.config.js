import vueA11y from 'eslint-plugin-vuejs-accessibility';
import tsParser from '@typescript-eslint/parser';

export default [
  ...vueA11y.configs['flat/recommended'].map(config => ({
    ...config,
    files: ['src/**/*.vue'],
    languageOptions: {
      ...config.languageOptions,
      parserOptions: {
        ...config.languageOptions?.parserOptions,
        parser: tsParser,
      },
    },
    rules: {
      ...config.rules,
      // Accept either for/id association or nesting — both are valid HTML patterns
      'vuejs-accessibility/label-has-for': ['error', { required: { some: ['nesting', 'id'] } }],
    },
  })),
];
