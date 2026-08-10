import { useState, useEffect } from 'react';
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion';

type Tab = 'article' | 'video';
type GenerationMode = 'topic' | 'url';
type VideoPreset = 'youtube_long' | 'youtube_short' | 'instagram_reel';

interface VideoMetadata {
  url: string;
  title: string;
  duration: string;
  platform: string;
  platformType: 'youtube' | 'instagram';
  tags: string[];
}

const VIDEO_PRESETS: Record<VideoPreset, VideoMetadata> = {
  youtube_long: {
    url: 'https://youtube.com/watch?v=react19_deep_dive',
    title: 'Understanding React 19 Server Components',
    duration: '12:34',
    platform: 'YouTube (Long-form)',
    platformType: 'youtube',
    tags: ['react19', 'frontend', 'webdev', 'codeplus'],
  },
  youtube_short: {
    url: 'https://youtube.com/shorts/r19-quick-tip-30s',
    title: '3 Second Trick for React State ⚡',
    duration: '0:45',
    platform: 'YouTube Short',
    platformType: 'youtube',
    tags: ['shorts', 'react', 'quicktips', 'coding'],
  },
  instagram_reel: {
    url: 'https://instagram.com/reel/C3x9kL2p1M8',
    title: 'Building AI Apps with Code Plus Academy #reels',
    duration: '0:58',
    platform: 'Instagram Reel',
    platformType: 'instagram',
    tags: ['reels', 'aistudio', 'coding', 'codeplus'],
  },
};

export function EditorPanel() {
  const prefersReducedMotion = usePrefersReducedMotion();
  const [activeTab, setActiveTab] = useState<Tab>('article');
  const [genMode, setGenMode] = useState<GenerationMode>('topic');
  const [inputValue, setInputValue] = useState('');
  const [genStatus, setGenStatus] = useState('');
  const [blocksFilled, setBlocksFilled] = useState(0);

  const [videoPreset, setVideoPreset] = useState<VideoPreset>('youtube_long');
  const [videoInput, setVideoInput] = useState('');
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [timelineStage, setTimelineStage] = useState(0);

  const currentVideoMeta = VIDEO_PRESETS[videoPreset];

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
        setVideoInput(currentVideoMeta.url);
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
      const targetUrl = currentVideoMeta.url;
      let i = 0;
      const typeNextChar = () => {
        if (i < targetUrl.length) {
          setVideoInput(targetUrl.slice(0, i + 1));
          i++;
          timeouts.push(window.setTimeout(typeNextChar, 25));
        } else {
          timeouts.push(window.setTimeout(() => {
            setVideoLoaded(true);
          }, 600));
        }
      };
      timeouts.push(window.setTimeout(typeNextChar, 400));
    }

    return clearTimeouts;
  }, [activeTab, genMode, videoPreset, prefersReducedMotion]);

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
            <div className="flex flex-col gap-5 max-w-2xl">
              <div className="flex items-center gap-2 border-b border-hairline pb-3">
                <span className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted mr-1">Link Type:</span>
                <button 
                  onClick={() => setVideoPreset('youtube_long')}
                  className={`text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill transition-colors ${videoPreset === 'youtube_long' ? 'bg-surface-strong text-ink' : 'text-muted hover:text-ink'}`}
                >
                  YouTube (Long-form)
                </button>
                <button 
                  onClick={() => setVideoPreset('youtube_short')}
                  className={`text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill transition-colors ${videoPreset === 'youtube_short' ? 'bg-surface-strong text-ink' : 'text-muted hover:text-ink'}`}
                >
                  YouTube Shorts
                </button>
                <button 
                  onClick={() => setVideoPreset('instagram_reel')}
                  className={`text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill transition-colors ${videoPreset === 'instagram_reel' ? 'bg-surface-strong text-ink' : 'text-muted hover:text-ink'}`}
                >
                  Instagram Reel
                </button>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted">Paste Video or Reel URL</label>
                <div className="flex items-center bg-canvas-soft border border-hairline rounded-[8px] px-4 py-3 h-[44px] overflow-hidden">
                  <span className="text-muted mr-3 shrink-0">🔗</span>
                  <span className="text-ink truncate">{videoInput}</span>
                  {!videoLoaded && <span className="w-2 h-4 bg-primary ml-1 shrink-0 animate-pulse"></span>}
                </div>
              </div>

              {videoLoaded && (
                <div className="animate-fade-in border border-hairline rounded-[12px] overflow-hidden bg-surface-card flex flex-col sm:flex-row shadow-sm">
                  <div className="w-full sm:w-48 h-32 bg-canvas flex items-center justify-center shrink-0 border-b sm:border-b-0 sm:border-r border-hairline relative">
                    <div className="w-12 h-12 rounded-full bg-surface-card shadow-sm flex items-center justify-center border border-hairline">
                      <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-ink border-b-[6px] border-b-transparent ml-1"></div>
                    </div>
                    <div className="absolute bottom-2 right-2 bg-ink text-canvas text-[11px] font-mono px-1.5 py-0.5 rounded-[4px]">
                      {currentVideoMeta.duration}
                    </div>
                    <div className="absolute top-2 left-2">
                      {currentVideoMeta.platformType === 'instagram' ? (
                        <span className="bg-gradient-to-r from-purple-600 to-pink-500 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shadow-sm">
                          Reel
                        </span>
                      ) : (
                        <span className="bg-red-600 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full shadow-sm">
                          YouTube
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="p-4 flex flex-col justify-between flex-1">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[11px] font-semibold text-primary uppercase tracking-wider">{currentVideoMeta.platform}</span>
                        <span className="text-muted">•</span>
                        <span className="text-[11px] text-muted font-mono">{currentVideoMeta.duration}</span>
                      </div>
                      <h3 className="font-sans text-[15px] font-medium text-ink mb-1 line-clamp-2">{currentVideoMeta.title}</h3>
                      <p className="font-sans text-[13px] text-muted">Code Plus Academy</p>
                    </div>
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {currentVideoMeta.tags.map((tag, idx) => (
                        <span key={idx} className="text-[10px] font-semibold tracking-[0.88px] uppercase bg-surface-strong text-ink px-[8px] py-0.5 rounded-pill">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              {videoLoaded && (
                <div className="animate-fade-in flex items-center justify-between gap-3 pt-1 border-t border-hairline">
                  <div className="flex items-center gap-2">
                    <div className="text-[11px] font-semibold tracking-[0.88px] uppercase text-muted">Status:</div>
                    <div className="text-[11px] font-semibold tracking-[0.88px] uppercase px-[10px] py-1 rounded-pill text-semantic-success bg-semantic-success/10">
                      Auto-Fetched Metadata • Ready to Publish
                    </div>
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
