import { useEffect, useRef } from 'react';
import { useTheme } from '../hooks/useTheme';

declare global {
  interface Window {
    VANTA: any;
    p5: any;
  }
}

export function VantaBackground() {
  const vantaRef = useRef<HTMLDivElement>(null);
  const vantaEffect = useRef<any>(null);
  const { theme } = useTheme();

  useEffect(() => {
    let timer: number;

    const initVanta = () => {
      if (vantaEffect.current) {
        vantaEffect.current.destroy();
        vantaEffect.current = null;
      }

      if (window.VANTA && window.VANTA.TRUNK && vantaRef.current) {
        const isDark = theme === 'dark';
        vantaEffect.current = window.VANTA.TRUNK({
          el: vantaRef.current,
          p5: window.p5,
          mouseControls: true,
          touchControls: true,
          gyroControls: false,
          minHeight: 200.00,
          minWidth: 200.00,
          scale: 1.00,
          scaleMobile: 1.00,
          chaos: 10.00,
          color: isDark ? 0xf54e00 : 0xe04800,
          backgroundColor: isDark ? 0x131210 : 0xf7f7f4,
          spacing: 2.50,
        });
      } else {
        timer = window.setTimeout(initVanta, 100);
      }
    };

    initVanta();

    return () => {
      if (timer) clearTimeout(timer);
      if (vantaEffect.current) {
        vantaEffect.current.destroy();
      }
    };
  }, [theme]);

  return (
    <div 
      ref={vantaRef} 
      className="absolute inset-0 z-0 pointer-events-none opacity-40 dark:opacity-30 transition-opacity duration-500"
      aria-hidden="true"
    />
  );
}
