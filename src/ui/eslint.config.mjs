import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';

export default tseslint.config({
  files: ['**/*.ts', '**/*.tsx'],
  extends: [
    eslint.configs.recommended,
    tseslint.configs.recommendedTypeChecked,
    tseslint.configs.stylisticTypeChecked,
    tseslint.configs.strictTypeChecked,
  ],
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
    },
  },
  rules: {
    "@typescript-eslint/no-extraneous-class": "off",
    "@typescript-eslint/use-unknown-in-catch-callback-variable": "off",
    "@typescript-eslint/restrict-template-expressions": [
      "error",
      {
        allowAny: false,
        allowBoolean: true,
        allowNever: false,
        allowNullish: false,
        allowNumber: true,
        allowRegExp: false,
      }
    ]
  },
});