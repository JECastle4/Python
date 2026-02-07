// TypeScript shim for importing .vue files
// Place this in your src directory (e.g., src/shims-vue.d.ts)
declare module '*.vue' {
  import { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
