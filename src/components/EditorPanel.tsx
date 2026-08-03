import { useState, useEffect } from 'react';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

type Tab = 'article' | 'video';
type GenerationMode = 'topic' | 'url';

export function EditorPanel() {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [activeTab, setActiveTab] = useState<Tab>('article');
  const [genMode, setGenMode] = useState<GenerationMode>('topic');
  const [inputValue, setInputValue] = useState('');
  const [genStatus, setGenStatus] = useState('');
  const [blocksFilled, setBlocksFilled] = useState(0);
  const [videoInput, setVideoInput] = useState('');
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [timelineStage, setTimelineStage] = useState(0);

  useEffect(() => {
    let timeouts: number[] = [];
    const clearTimeouts = () => timeouts.forEach(window.clearTimeout);
    
    if (prefersReducedMotion) {
      if (activeTab === 'article') {
        setInputValue(genMode === 'topic' ? 'React 19 Server Components' : 'https://react.dev/blog/2024');
        setGenStatus('Draft complete');
        setBlocksFilled(3);
        setTimelineStage(4);
      } else {
        setVideoInput('https://youtube.com/watch?v=react19');
        setVideoLoaded(true);
      }
      return;
    }

    setInputValue('');
    setGenStatus('');
    setBlocksFilled(0);
    setVideoInput('');
    setVideoLoaded(false);
    setTimelineStage(0);

    if (activeTab === 'article') {
      const targetInput = genMode === 'topic' ? 'React 19 Server Components' : 'https://react.dev/blog/2024';
      
      let i = 0;
      const typeNextChar = () => {
        if (i < targetInput.length) {
          setInputValue(targetInput.slice(0, i + 1));
          i++;
          timeouts.push(window.setTimeout(typeNextChar, 40));
        } else {
          timeouts.push(window.setTimeout(() => {
            setGenStatus(genMode === 'topic' ? 'AI is drafting your article...' : 'Reading source and drafting...');
            setTimelineStage(1);
            
            let block = 1;
            const fillNextBlock = () => {
              if (block <= 3) {
                setBlocksFilled(block);
                setGenStatus(`Filling block ${block} of 3...`);
                setTimelineStage(Math.min(block + 1, 4));
                block++;
                timeouts.push(window.setTimeout(fillNextBlock, 800));
              } else {
                setGenStatus('Draft complete');
                setTimelineStage(4);
              }
            };
            timeouts.push(window.setTimeout(fillNextBlock, 1000));
          }, 400));
        }
      };
      timeouts.push(window.setTimeout(typeNextChar, 500));
      
    } else if (activeTab === 'video') {
      const targetUrl = 'https://youtube.com/watch?v=react19';
      let i = 0;
      const typeNextChar = () => {
        if (i < targetUrl.length) {
          setVideoInput(targetUrl.slice(0, i + 1));
          i++;
          timeouts.push(window.setTimeout(typeNextChar, 30));
        } else {
          timeouts.push(window.setTimeout(() => {
            setVideoLoaded(true);
          }, 800));
        }
      };
      timeouts.push(window.setTimeout(typeNextChar, 500));
    }

    return clearTimeouts;
  }, [activeTab, genMode, prefersReducedMotion]);

  return (
    <div className="w-full max-w-5xl mx-auto rounded-[12px] overflow-hidden border border-hairline bg-surface-card flex flex-col md:flex-row h-auto md:h-[500px] text-left shadow-sm">
      
      {/* Sidebar */}
      <div className="w-full md:w-64 bg-canvas-soft border-r border-hairline flex flex-col shrink-0">
        <div className="flex items-center gap-2 px-4 py-3 border-b border-hairline">
          <div className="w-3 h-3 rounded-full bg-hairline-strong"></div>
          <div className="w-3 h-3 rounded-full bg-hairline-strong"></div>
          <div className="w-3 h-3 rounded-full bg-hairline-strong"></div>
        </div>
        <div className="p-4 flex flex-col gap-2">
          <div className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted mb-2">Workspace</div>
          <button
            onClick={() => setActiveTab('article')}
            className={`text-left px-3 py-1.5 rounded-[6px] text-[13px] font-mono transition-colors ${
              activeTab === 'article' 
                ? 'bg-surface-card border border-hairline text-ink' 
                : 'text-body hover:bg-surface-strong/50 hover:text-ink'
            }`}
          >
            article.md
          </button>
          <button
            onClick={() => setActiveTab('video')}
            className={`text-left px-3 py-1.5 rounded-[6px] text-[13px] font-mono transition-colors ${
              activeTab === 'video' 
                ? 'bg-surface-card border border-hairline text-ink' 
                : 'text-body hover:bg-surface-strong/50 hover:text-ink'
            }`}
          >
            video_sync
          </button>
        </div>
      </div>

      {/* Main Editor */}
      <div className="flex-1 bg-surface-card flex flex-col relative overflow-hidden">
        {/* Top bar */}
        <div className="h-12 border-b border-hairline flex items-center px-4 bg-canvas-soft">
          <span className="text-[13px] font-mono text-muted">
            {activeTab === 'article' ? 'article.md' : 'video_sync'}
          </span>
        </div>

        <div className="flex-1 p-6 font-mono text-[13px] text-body overflow-y-auto">
          {activeTab === 'article' && (
            <div className="flex flex-col h-full max-w-2xl">
              <div className="flex items-center gap-2 mb-6 border-b border-hairline pb-4">
                <button 
                  onClick={() => setGenMode('topic')}
                  className={`text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill transition-colors ${genMode === 'topic' ? 'bg-surface-strong text-ink' : 'text-muted hover:text-ink'}`}
                >
                  From Topic
                </button>
                <button 
                  onClick={() => setGenMode('url')}
                  className={`text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill transition-colors ${genMode === 'url' ? 'bg-surface-strong text-ink' : 'text-muted hover:text-ink'}`}
                >
                  From URL
                </button>
              </div>
              
              <div className="flex flex-col gap-2 mb-6">
                <div className="flex items-center">
                  <span className="text-primary mr-2">❯</span>
                  <span className="text-ink">{inputValue}</span>
                  {genStatus === '' && <span className="w-2 h-4 bg-primary ml-1 animate-pulse"></span>}
                </div>
              </div>

              {genStatus && (
                <div className="flex flex-wrap items-center gap-2 mb-6 p-4 rounded-[8px] bg-canvas-soft border border-hairline">
                  <div className="text-muted text-[13px] mr-2">Agent Timeline:</div>
                  <div className={`px-[10px] py-1 rounded-pill text-[11px] font-semibold tracking-[0.88px] uppercase transition-all duration-300 ${timelineStage >= 1 ? 'bg-timeline-thinking text-ink' : 'bg-surface-strong text-muted-soft'}`}>Thinking</div>
                  <div className="w-4 h-[1px] bg-hairline-strong"></div>
                  <div className={`px-[10px] py-1 rounded-pill text-[11px] font-semibold tracking-[0.88px] uppercase transition-all duration-300 ${timelineStage >= 2 ? 'bg-timeline-grep text-ink' : 'bg-surface-strong text-muted-soft'}`}>Grepping</div>
                  <div className="w-4 h-[1px] bg-hairline-strong"></div>
                  <div className={`px-[10px] py-1 rounded-pill text-[11px] font-semibold tracking-[0.88px] uppercase transition-all duration-300 ${timelineStage >= 3 ? 'bg-timeline-edit text-ink' : 'bg-surface-strong text-muted-soft'}`}>Editing</div>
                  <div className="w-4 h-[1px] bg-hairline-strong"></div>
                  <div className={`px-[10px] py-1 rounded-pill text-[11px] font-semibold tracking-[0.88px] uppercase transition-all duration-300 ${timelineStage >= 4 ? 'bg-timeline-done text-on-primary' : 'bg-surface-strong text-muted-soft'}`}>Done</div>
                </div>
              )}

              <div className="flex flex-col gap-4 font-sans text-[16px] text-body leading-[1.5]">
                {blocksFilled > 0 && (
                  <div className="animate-fade-in">
                    <h1 className="text-[26px] tracking-[-0.325px] font-normal text-ink mb-2">
                      {genMode === 'topic' ? 'React 19 Server Components' : 'Understanding the New React Architecture'}
                    </h1>
                  </div>
                )}
                {blocksFilled > 1 && (
                  <div className="animate-fade-in">
                    <p>
                      Server Components represent a major shift in how we build React applications. By executing components on the server, we can send less JavaScript to the client and improve initial load times significantly.
                    </p>
                  </div>
                )}
                {blocksFilled > 2 && (
                  <div className="animate-fade-in p-[20px] rounded-[12px] bg-canvas border border-hairline font-mono text-[13px] mt-4">
                    <span className="text-primary font-semibold">Note:</span> Emphasize to students that Client Components are not deprecated; they simply work alongside Server Components for interactivity.
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'video' && (
            <div className="flex flex-col gap-6 max-w-2xl">
              <div className="flex flex-col gap-2">
                <label className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted">Video Source URL</label>
                <div className="flex items-center bg-canvas-soft border border-hairline rounded-[8px] px-4 py-3 h-[44px]">
                  <span className="text-muted mr-3">🔗</span>
                  <span className="text-ink">{videoInput}</span>
                  {!videoLoaded && <span className="w-2 h-4 bg-primary ml-1 animate-pulse"></span>}
                </div>
              </div>

              {videoLoaded && (
                <div className="animate-fade-in border border-hairline rounded-[12px] overflow-hidden bg-surface-card flex flex-col sm:flex-row shadow-sm">
                  <div className="w-full sm:w-48 h-32 bg-canvas flex items-center justify-center shrink-0 border-r border-hairline relative">
                    <div className="w-12 h-12 rounded-full bg-surface-card shadow-sm flex items-center justify-center border border-hairline">
                      <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-ink border-b-[6px] border-b-transparent ml-1"></div>
                    </div>
                    <div className="absolute bottom-2 right-2 bg-ink text-canvas text-[11px] font-mono px-1.5 py-0.5 rounded-[4px]">
                      12:34
                    </div>
                  </div>
                  <div className="p-4 flex flex-col justify-between flex-1">
                    <div>
                      <h3 className="font-sans text-[16px] font-medium text-ink mb-1">Understanding React 19 Server Components</h3>
                      <p className="font-sans text-[14px] text-muted">Code Plus Academy</p>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <span className="text-[11px] font-semibold tracking-[0.88px] uppercase bg-surface-strong text-ink px-[10px] py-1 rounded-pill">react</span>
                      <span className="text-[11px] font-semibold tracking-[0.88px] uppercase bg-surface-strong text-ink px-[10px] py-1 rounded-pill">frontend</span>
                    </div>
                  </div>
                </div>
              )}
              
              {videoLoaded && (
                <div className="animate-fade-in mt-4 flex items-center gap-3">
                  <div className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted">Status:</div>
                  <div className="text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill text-semantic-success bg-semantic-success/10">
                    Ready to Publish
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
