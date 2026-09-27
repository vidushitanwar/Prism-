import { useEffect } from "react";

/**
 * Fires `handler` when the given key is pressed with the given modifiers.
 * Used for the Ctrl+K command palette and Esc-to-close behavior.
 */
export function useKeyboardShortcut(
  key: string,
  handler: () => void,
  options?: { ctrlOrCmd?: boolean }
) {
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const matchesKey = e.key.toLowerCase() === key.toLowerCase();
      const matchesModifier = options?.ctrlOrCmd ? e.ctrlKey || e.metaKey : true;
      if (matchesKey && matchesModifier) {
        e.preventDefault();
        handler();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [key, handler, options?.ctrlOrCmd]);
}
