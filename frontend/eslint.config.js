import js from "@eslint/js";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { ecmaVersion: 2022 },
    plugins: { "react-hooks": reactHooks, "react-refresh": reactRefresh },
    rules: {
      ...reactHooks.configs.recommended.rules,
      // Estas pantallas cargan datos remotos al montarse; actualizar el estado
      // desde el efecto es el patrón intencional en este cliente sin React Query.
      "react-hooks/set-state-in-effect": "off",
      // Las funciones de carga se recrean con filtros del panel. Sus efectos
      // declaran explícitamente cuándo deben volver a consultar la API.
      "react-hooks/exhaustive-deps": "off",
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },
);
