import eslint from "@eslint/js";
import tseslint from "typescript-eslint";
import reactPlugin from "eslint-plugin-react";

export default tseslint.config({
  files: ["**/*.ts", "**/*.tsx"],
  extends: [
    eslint.configs.recommended,
    tseslint.configs.recommendedTypeChecked,
    // tseslint.configs.stylisticTypeChecked,
    // tseslint.configs.strictTypeChecked,
    reactPlugin.configs.flat.recommended, // This is not a plugin object, but a shareable config object
    reactPlugin.configs.flat["jsx-runtime"], // Add this if you are using React 17+
  ],
  languageOptions: {
    parserOptions: {
      projectService: true,
      tsconfigRootDir: import.meta.dirname,
      ecmaFeatures: {
        jsx: true,
      },
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
      },
    ],
  },
});
