import { useTheme } from '../hooks/useTheme';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
  textClassName?: string;
  mode?: 'light' | 'dark' | 'auto';
}

export function Logo({
  className = '',
  size = 36,
  showText = true,
  textClassName = '',
  mode = 'auto',
}: LogoProps) {
  const { theme } = useTheme();
  
  const activeMode = mode === 'auto' ? theme : mode;
  const isDark = activeMode === 'dark';

  return (
    <div className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 transition-transform hover:scale-105 duration-200"
      >
        <defs>
          {/* Main Vibrant Cyan to Purple Gradient */}
          <linearGradient
            id="codePlusGradient"
            x1="15%"
            y1="10%"
            x2="85%"
            y2="90%"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="45%" stopColor="#6366F1" />
            <stop offset="85%" stopColor="#A855F7" />
            <stop offset="100%" stopColor="#C084FC" />
          </linearGradient>

          {/* Slight Glow / Drop Shadow for emblem */}
          <filter id="logoGlow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#6366F1" floodOpacity="0.15" />
          </filter>
        </defs>

        {/* Outer Circular Container */}
        <circle
          cx="60"
          cy="60"
          r="56"
          fill={isDark ? '#1A191D' : '#FFFFFF'}
          stroke={isDark ? '#2D2B32' : '#EAE8E3'}
          strokeWidth="1.5"
        />

        <g filter="url(#logoGlow)">
          {/* Outer C-Shape Loop */}
          <path
            d="M 68 28.5 C 38 28.5 20 42 20 62 C 20 81 37 92 68 92 C 73 92 78 91 82 89.5 C 84.5 88.5 85.5 85.5 84 83.2 C 82.5 81 79.5 80.2 77 81.3 C 74.2 82.5 71 83 68 83 C 42 83 29 74.5 29 62 C 29 48.5 42 37.5 68 37.5 C 70.8 37.5 73.5 37.9 76 38.6 C 78.5 39.3 81.2 38 82.2 35.5 C 83.2 33 82 30.2 79.5 29.4 C 75.8 28.8 72 28.5 68 28.5 Z"
            fill="url(#codePlusGradient)"
          />

          {/* Inner Sharp Swoosh accent on C top inner rim */}
          <path
            d="M 23 58 C 28 54 36 50 48 48 C 38 52 30 58 25 64 C 23.5 62 23 60 23 58 Z"
            fill="url(#codePlusGradient)"
            opacity="0.9"
          />

          {/* Play Triangle Symbol inside C */}
          <path
            d="M 48 48.5 C 48 46.5 50.2 45.2 52 46.2 L 72 57.7 C 73.7 58.7 73.7 61.3 72 62.3 L 52 73.8 C 50.2 74.8 48 73.5 48 71.5 V 48.5 Z"
            fill="url(#codePlusGradient)"
          />

          {/* Top-Right Plus (+) Symbol */}
          <path
            d="M 80 20 V 32 M 74 26 H 86"
            stroke="url(#codePlusGradient)"
            strokeWidth="4.5"
            strokeLinecap="round"
          />
        </g>
      </svg>

      {showText && (
        <div className="flex flex-col justify-center text-left leading-none">
          <span className={`font-sans font-bold tracking-tight animate-studio-gradient ${textClassName || 'text-[18px]'}`}>
            Studio
          </span>
          <span className="text-muted font-normal text-[11px] leading-tight tracking-tight whitespace-nowrap mt-0.5">
            by Code Plus Academy
          </span>
        </div>
      )}
    </div>
  );
}
