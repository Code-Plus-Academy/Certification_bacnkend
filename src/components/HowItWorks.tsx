import { useReveal } from '../hooks/useReveal';

const steps = [
  {
    number: '01',
    title: 'Draft',
    description: 'Start from a blank template, or let the AI assistant write the first version based on a topic or source URL.',
  },
  {
    number: '02',
    title: 'Edit',
    description: 'Refine your content in the structured editor. Use the AI chat to add code examples, tweak headings, or adjust tone.',
  },
  {
    number: '03',
    title: 'Publish',
    description: 'Publish your article, sync your YouTube videos & Instagram Reels, or distribute your study resources directly to your students.',
  },
];

export function HowItWorks() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="how-it-works" className="py-[80px] bg-canvas-soft border-t border-hairline relative">
      <div 
        ref={ref}
        className={`max-w-[1200px] mx-auto px-6 transition-all duration-1000 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="text-center mb-[64px]">
          <h2 className="text-[36px] font-sans font-normal text-ink mb-4 tracking-[-0.72px]">
            From idea to published.
          </h2>
        </div>

        <div className="grid md:grid-cols-3 gap-6 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-[28px] left-[16%] right-[16%] h-[1px] bg-hairline-strong"></div>

          {steps.map((step, idx) => (
            <div key={idx} className="relative z-10 flex flex-col items-center text-center">
              <div className="w-[56px] h-[56px] rounded-full bg-surface-card border border-hairline text-ink font-mono text-[16px] flex items-center justify-center mb-6 shadow-sm">
                {step.number}
              </div>
              <h3 className="text-[22px] font-sans font-normal text-ink mb-[12px] tracking-[-0.11px]">
                {step.title}
              </h3>
              <p className="text-[16px] text-body font-sans leading-[1.5] max-w-[280px]">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
