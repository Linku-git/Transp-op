# Frontend Rules (React/TypeScript)

## File Structure
- Pages: `frontend/src/pages/<module>/` — route-level components
- Components: `frontend/src/components/<category>/` — shared UI components
- API: `frontend/src/api/<module>.ts` — API client functions
- Stores: `frontend/src/stores/<name>Store.ts` — Zustand state stores
- Hooks: `frontend/src/hooks/use<Name>.ts` — custom React hooks
- Types: `frontend/src/types/<module>.ts` — TypeScript interfaces

## Conventions
- TypeScript strict mode (no `any` types, no `@ts-ignore`)
- Functional components only (no class components)
- Use named exports, not default exports
- Component files: PascalCase (`SiteList.tsx`)
- Hook files: camelCase with `use` prefix (`useSites.ts`)
- Every component must handle: loading, error, and empty states
- Use TailwindCSS for styling, no CSS modules or styled-components
- API calls via Axios with typed responses
- i18n via react-i18next (fr primary, en secondary)
- Zustand stores: one per domain, named `use<Domain>Store`

## Testing
- Colocated tests: `__tests__/<Component>.test.tsx` next to component
- Use Vitest + React Testing Library
- Every component gets at minimum a render test
- Test file naming: `<Component>.test.tsx`
