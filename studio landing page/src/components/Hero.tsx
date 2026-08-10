import { useReveal } from '../hooks/useReveal';
import { EditorPanel } from './EditorPanel';
import { VantaBackground } from './VantaBackground';

export function Hero() {
  const { ref, isVisible } = useReveal();

  return (
    <section className="pt-32 pb-20 md:pt-40 md:pb-[80px] px-6 relative overflow-hidden bg-canvas">
      <VantaBackground />
      <div 
        ref={ref}
        className={`max-w-[1200px] mx-auto flex flex-col items-center text-center transition-all duration-1000 relative z-10 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <h1 className="text-[40px] md:text-[56px] lg:text-[72px] font-sans font-normal leading-[1.1] mb-6 text-ink tracking-[-2.16px] max-w-4xl">
          Write, publish, and manage everything you teach — with AI.
        </h1>
        
        <p className="text-[16px] text-body mb-8 max-w-2xl leading-[1.5] font-sans">
          A unified workspace for creators published on <strong className="text-ink font-semibold">Code Plus Academy</strong>. Draft articles instantly with AI, sync YouTube videos &amp; Instagram Reels effortlessly, and upload structured study notes for your students.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mb-16">
          <button className="w-full sm:w-auto bg-ink text-canvas px-[20px] py-[12px] h-[44px] rounded-[8px] font-medium text-[14px] leading-[1.0] hover:bg-ink/90 transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-ink focus:ring-offset-2 focus:ring-offset-canvas">
            Get started (for Code Plus Academy)
          </button>
          <button className="w-full sm:w-auto bg-transparent text-ink px-[20px] py-[12px] h-[44px] rounded-[8px] font-medium text-[14px] leading-[1.0] hover:bg-hairline-soft transition-colors flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-ink focus:ring-offset-2 focus:ring-offset-canvas">
            Try Studio
          </button>
        </div>

        <div className="w-full">
          <EditorPanel />
        </div>
      </div>
    </section>
  );
}
