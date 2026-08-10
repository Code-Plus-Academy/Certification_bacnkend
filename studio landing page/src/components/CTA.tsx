import { useReveal } from '../hooks/useReveal';

export function CTA() {
  const { ref, isVisible } = useReveal();

  return (
    <section className="py-[96px] bg-canvas border-t border-hairline text-center">
      <div 
        ref={ref}
        className={`max-w-[1200px] mx-auto px-6 transition-all duration-1000 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <h2 className="text-[36px] font-sans font-normal text-ink mb-6 tracking-[-0.72px]">
          Ready to start publishing?
        </h2>
        <p className="text-[16px] text-body font-sans mb-[40px] max-w-2xl mx-auto leading-[1.5]">
          Join Code Plus Academy and get access to Studio. Write, manage, and share your resources in one place.
        </p>
        
        <button className="bg-primary text-on-primary px-[18px] py-[10px] h-[40px] rounded-[8px] font-medium text-[14px] leading-[1.0] hover:bg-primary-active transition-colors mx-auto inline-flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-canvas">
          Try Studio now
        </button>
      </div>
    </section>
  );
}
