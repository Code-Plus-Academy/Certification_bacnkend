export function Footer() {
  return (
    <footer className="bg-canvas py-[64px] border-t border-hairline">
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 mb-[48px]">
          <div className="col-span-1 md:col-span-2 pr-8">
            <div className="flex items-center gap-3 mb-4">
              <span className="font-sans font-medium text-[18px] tracking-tight text-ink">Studio</span>
            </div>
            <p className="text-[14px] text-body font-sans leading-[1.5] max-w-[280px]">
              The creator workspace for Code Plus Academy. Write, publish, and manage everything you teach.
            </p>
          </div>
          
          <div className="col-span-1">
            <h4 className="font-sans font-semibold text-[16px] text-ink mb-4">Product</h4>
            <ul className="space-y-[12px] font-sans text-[14px] text-body">
              <li>
                <a href="#features" className="hover:text-ink transition-colors focus:outline-none focus:ring-1 focus:ring-ink rounded-sm">Features</a>
              </li>
              <li>
                <a href="#notes-arena" className="hover:text-ink transition-colors focus:outline-none focus:ring-1 focus:ring-ink rounded-sm">Notes Arena</a>
              </li>
            </ul>
          </div>
          
          <div className="col-span-1">
            <h4 className="font-sans font-semibold text-[16px] text-ink mb-4">Company</h4>
            <ul className="space-y-[12px] font-sans text-[14px] text-body">
              <li>
                <a href="#about" className="hover:text-ink transition-colors focus:outline-none focus:ring-1 focus:ring-ink rounded-sm">About</a>
              </li>
              <li>
                <a href="#contact" className="hover:text-ink transition-colors focus:outline-none focus:ring-1 focus:ring-ink rounded-sm">Contact</a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-hairline-soft pt-[32px] flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[14px] text-body font-sans">
            © {new Date().getFullYear()} Code Plus Academy. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
