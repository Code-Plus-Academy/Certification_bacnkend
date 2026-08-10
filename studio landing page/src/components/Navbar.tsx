import { useState, useEffect } from 'react';
import { Menu, X, Sun, Moon, ExternalLink } from 'lucide-react';
import { useTheme } from '../hooks/useTheme';
import { Logo } from './Logo';

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 h-16 ${scrolled ? 'bg-canvas/90 backdrop-blur-md border-b border-hairline' : 'bg-transparent'}`}>
      <div className="max-w-[1200px] mx-auto px-6 h-full flex items-center justify-between">
        <a href="#" className="flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-primary rounded-md py-1">
          <Logo size={36} />
        </a>
        
        <div className="hidden md:flex items-center gap-6 text-[14px] font-medium text-ink">
          <a href="#features" className="hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-sm px-1">Features</a>
          <a href="#how-it-works" className="hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-sm px-1">How it works</a>
          <a href="#notes-arena" className="hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-sm px-1">Notes Arena</a>
          <a 
            href="https://www.codeplusacademy.in/explore" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[8px] border border-hairline bg-surface-card hover:bg-surface-strong text-ink hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary font-medium"
          >
            Explore
            <ExternalLink className="w-3.5 h-3.5 opacity-70" />
          </a>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-[8px] border border-hairline bg-surface-card text-ink hover:bg-surface-strong transition-colors focus:outline-none focus:ring-2 focus:ring-primary flex items-center justify-center h-10 w-10"
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-ink" /> : <Moon className="w-4 h-4 text-ink" />}
          </button>

          <button className="bg-primary text-on-primary px-[18px] py-[10px] rounded-[8px] font-medium text-[14px] leading-[1.0] hover:bg-primary-active transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-canvas h-10">
            Start free
          </button>
        </div>

        <div className="flex items-center gap-3 md:hidden">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-[8px] border border-hairline bg-surface-card text-ink hover:bg-surface-strong transition-colors focus:outline-none focus:ring-2 focus:ring-primary flex items-center justify-center h-10 w-10"
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? <Sun className="w-4 h-4 text-ink" /> : <Moon className="w-4 h-4 text-ink" />}
          </button>

          <button 
            className="text-ink focus:outline-none focus:ring-2 focus:ring-primary rounded-sm p-1"
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`fixed inset-0 bg-canvas z-50 transition-opacity duration-300 ${mobileMenuOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
        <div className="h-16 px-6 flex justify-between items-center border-b border-hairline">
          <a href="#" onClick={() => setMobileMenuOpen(false)}>
            <Logo size={32} />
          </a>
          <button 
            className="text-ink focus:outline-none focus:ring-2 focus:ring-primary rounded-sm"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="flex flex-col items-center gap-8 text-lg font-sans mt-12 text-ink">
          <a href="#features" className="hover:text-primary" onClick={() => setMobileMenuOpen(false)}>Features</a>
          <a href="#how-it-works" className="hover:text-primary" onClick={() => setMobileMenuOpen(false)}>How it works</a>
          <a href="#notes-arena" className="hover:text-primary font-medium" onClick={() => setMobileMenuOpen(false)}>Notes Arena</a>
          <a 
            href="https://www.codeplusacademy.in/explore" 
            target="_blank" 
            rel="noopener noreferrer" 
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-[8px] border border-hairline bg-surface-card hover:bg-surface-strong text-ink font-medium"
            onClick={() => setMobileMenuOpen(false)}
          >
            Explore <ExternalLink className="w-4 h-4 text-primary" />
          </a>
          
          <button
            onClick={() => {
              toggleTheme();
              setMobileMenuOpen(false);
            }}
            className="flex items-center gap-2 px-4 py-2 rounded-[8px] border border-hairline bg-surface-card text-ink text-sm font-medium"
          >
            {theme === 'dark' ? (
              <>
                <Sun className="w-4 h-4" /> Light Mode
              </>
            ) : (
              <>
                <Moon className="w-4 h-4" /> Dark Mode
              </>
            )}
          </button>

          <button className="bg-primary text-on-primary px-[18px] py-[10px] rounded-[8px] font-medium text-[14px] leading-[1.0] w-[80%] max-w-sm mt-2 h-10 hover:bg-primary-active">
            Start free
          </button>
        </div>
      </div>
    </nav>
  );
}
