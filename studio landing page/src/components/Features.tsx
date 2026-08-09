import { useReveal } from '../hooks/useReveal';

const features = [
  {
    title: 'AI-assisted writing',
    description: 'Generate a full article from a topic or URL. Use the in-editor chat to ask for specific edits, like adding a code block or rewriting a heading.',
  },
  {
    title: 'Structured article editor',
    description: 'Start with 10 built-in templates, including Course, Tech Deep Dive, Project Showcase, Comparison, and Toolkit.',
  },
  {
    title: 'YouTube & Instagram Reels publishing',
    description: 'Paste a YouTube link (long-form or Short) or Instagram Reel link and Studio automatically pulls in the title, thumbnail, duration, and tags.',
  },
  {
    title: 'Study resource uploads',
    description: 'Upload notes, previous year question papers, cheat sheets, lab manuals, syllabi, reference books, and assignments directly to Notes Arena.',
    link: '#notes-arena',
    linkText: 'Explore Notes Arena'
  },
];

export function Features() {
  const { ref, isVisible } = useReveal();

  return (
    <section id="features" className="py-[80px] bg-canvas border-t border-hairline relative">
      <div 
        ref={ref}
        className={`max-w-[1200px] mx-auto px-6 relative z-10 transition-all duration-1000 ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
        }`}
      >
        <div className="mb-[64px]">
          <h2 className="text-[36px] font-sans font-normal text-ink mb-4 tracking-[-0.72px]">
            Everything you need to publish.
          </h2>
          <p className="text-[16px] text-body font-sans max-w-2xl leading-[1.5]">
            One unified library for all your content, with search, autosave, and full version history built right into the editor.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, idx) => (
            <div 
              key={idx}
              className="bg-surface-card border border-hairline rounded-[12px] p-[24px] flex flex-col"
            >
              <h3 className="text-[18px] font-semibold font-sans text-ink mb-[12px] leading-[1.4]">
                {feature.title}
              </h3>
              <p className="text-[16px] text-body font-sans leading-[1.5] mb-4 flex-1">
                {feature.description}
              </p>
              {feature.link && (
                <a href={feature.link} className="inline-flex items-center text-primary font-medium text-[14px] hover:text-primary-active transition-colors mt-auto">
                  {feature.linkText} <span className="ml-1">→</span>
                </a>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
