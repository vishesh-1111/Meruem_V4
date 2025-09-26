import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  // This loads the standard `next/core-web-vitals` and `next/typescript` configs.
  ...compat.extends("next/core-web-vitals", "next/typescript"),

  // This configuration object overrides the `no-unused-vars` rule.
  // It is placed after the `compat.extends` call to ensure the override takes effect.
  {
    rules: {
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/no-explicit-any": "off",
        "import/order": "off", // Disables the import/order rule
    "import/no-unresolved": "off",
  
    },
  },

  // This object contains file ignores and is placed last to be processed after the rules are configured.
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      "out/**",
      "build/**",
      "next-env.d.ts",
    ],
  },
];

export default eslintConfig;
