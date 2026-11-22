import { useState, useEffect } from 'react';

export type AppTheme = 'light' | 'dark';

/**
 * useHostTheme
 * Microfrontend hook that syncs with host Django/Bootstrap 5.3 theme.
 * - Reads initial theme from document.documentElement.getAttribute('data-bs-theme')
 * - Listens to 'themeChanged' custom events emitted by theme-toggle.js
 * - Maintains a defensive MutationObserver on <html> data-bs-theme attribute
 */
export const useHostTheme = (): AppTheme => {
  const getTheme = (): AppTheme => {
    if (typeof document === 'undefined') return 'light';
    const current = document.documentElement.getAttribute('data-bs-theme');
    if (current === 'dark' || current === 'light') {
      return current;
    }
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || saved === 'light') {
      return saved;
    }
    if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  };

  const [theme, setTheme] = useState<AppTheme>(getTheme);

  useEffect(() => {
    const handleThemeChanged = (event: Event) => {
      const customEvent = event as CustomEvent<{ theme: AppTheme }>;
      if (customEvent.detail && (customEvent.detail.theme === 'dark' || customEvent.detail.theme === 'light')) {
        setTheme(customEvent.detail.theme);
      } else {
        setTheme(getTheme());
      }
    };

    window.addEventListener('themeChanged', handleThemeChanged);

    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (
          mutation.type === 'attributes' &&
          mutation.attributeName === 'data-bs-theme'
        ) {
          const newTheme = document.documentElement.getAttribute('data-bs-theme');
          if (newTheme === 'dark' || newTheme === 'light') {
            setTheme(newTheme);
          }
        }
      }
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-bs-theme'],
    });

    return () => {
      window.removeEventListener('themeChanged', handleThemeChanged);
      observer.disconnect();
    };
  }, []);

  return theme;
};

export default useHostTheme;
