import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, FileText, Menu, X, Play, Loader2, CheckCircle2, FileAudio, RefreshCw, ExternalLink, ChevronDown, ChevronUp, Info, ChevronRight } from 'lucide-react';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const fileInputRef = useRef(null);
  const [activeTab, setActiveTab] = useState('process'); 
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  // Workflow States
  const [step, setStep] = useState(1); 
  const [selectedLecture, setSelectedLecture] = useState(null);
  const [selectedModel, setSelectedModel] = useState('llama3.1:8b');
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [lectures, setLectures] = useState([]);
  const [libraryData, setLibraryData] = useState([]);
  const [generatedNotes, setGeneratedNotes] = useState('');
  
  const [options, setOptions] = useState({ pdf: true, mcq: false });

  useEffect(() => {
    fetchLectures();
    fetchLibrary();
  }, []);

  const fetchLectures = async () => {
    try {
      const res = await fetch(`${API_BASE}/lectures`);
      const data = await res.json();
      setLectures(data.lectures || []);
    } catch (e) { console.error(e); }
  };

  const fetchLibrary = async () => {
    try {
      const res = await fetch(`${API_BASE}/library`);
      const data = await res.json();
      setLibraryData(data.library || []);
    } catch (e) { console.error(e); }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setStatus(`Uploading ${file.name}...`);
    const formData = new FormData();
    formData.append('file', file);
    try {
      await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData });
      setSelectedLecture(file.name);
      fetchLectures();
      startTranscription(file.name);
    } catch (e) { setStatus('Upload failed'); }
  };

  const startTranscription = (filename) => {
    setStep(2);
    setProgress(0);
    setStatus('Establishing stream connection...');
    
    const eventSource = new EventSource(`${API_BASE}/transcribe_stream?filename=${encodeURIComponent(filename)}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
      if (data.msg) setStatus(data.msg);

      if (data.status === 'exists') {
        setStatus('[SMART] Archive found. Proceed to generation.');
        eventSource.close();
      } else if (data.status === 'completed') {
        setStatus('Transcription finalized.');
        eventSource.close();
      }
    };

    eventSource.onerror = (e) => {
      setStatus('Stream lost. Please check connection.');
      eventSource.close();
    };
  };

  const startSummarization = async () => {
    setStep(4);
    setProgress(50);
    setStatus(`Synthesizing knowledge with ${selectedModel}... This will create 3 types of notes.`);
    const lectureName = selectedLecture.replace(/\.[^/.]+$/, "");
    const formData = new FormData();
    formData.append('lecture_name', lectureName);
    formData.append('ai_model', selectedModel);
    formData.append('generate_pdf', options.pdf);
    formData.append('generate_mcq', options.mcq);
    try {
      const res = await fetch(`${API_BASE}/summarize`, { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'completed') {
        setGeneratedNotes(data.content);
        setProgress(100);
        setStep(5);
        fetchLibrary();
      } else if (res.status === 503) {
        setStatus('AI Engine (Ollama) is not responding. Please start it.');
        setStep(3);
      }
    } catch (e) { 
      setStatus('Synthesis failed. Is Ollama running?'); 
      setStep(3);
    }
  };

  return (
    <div className="cinematic-container">
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <>
            <motion.div className="sidebar-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setIsSidebarOpen(false)} />
            <motion.aside className="cinematic-sidebar glass-card" initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}>
              <div className="sidebar-header"><div className="logo-sm">LECTURE TO NOTES</div><X className="close-icon" onClick={() => setIsSidebarOpen(false)} /></div>
              <div className="sidebar-nav">
                <div className={`nav-item ${activeTab === 'process' ? 'active' : ''}`} onClick={() => { setActiveTab('process'); setIsSidebarOpen(false); }}>🚀 Workspace</div>
                <div className={`nav-item ${activeTab === 'library' ? 'active' : ''}`} onClick={() => { setActiveTab('library'); setIsSidebarOpen(false); }}>📚 Archive</div>
              </div>
              <div className="sidebar-content">
                <h3 className="sidebar-label">Lectures</h3>
                <div className="lecture-list">
                  {lectures.map(l => (
                    <div key={l.filename} className="lecture-item glass-card" onClick={() => { setSelectedLecture(l.filename); startTranscription(l.filename); setIsSidebarOpen(false); }}>
                      <div className="lecture-name">{l.filename}</div>
                      {l.status === 'transcribed' ? <CheckCircle2 size={14} color="#10b981" /> : <Play size={14} />}
                    </div>
                  ))}
                </div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <header className="cinematic-header">
        <div className="header-left">
          <Menu className="menu-icon" onClick={() => setIsSidebarOpen(true)} />
          <div className="logo">Lecture to Notes</div>
        </div>
        <div className="header-actions">
           {activeTab === 'library' && <RefreshCw size={18} className="refresh-icon" onClick={fetchLibrary} />}
           <button className="btn-stellar-sm" onClick={() => fileInputRef.current.click()}>Upload</button>
        </div>
        <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFileUpload} />
      </header>

      <div className="video-background"><div className="overlay"></div></div>

      <section className="section">
        {activeTab === 'process' ? (
          <motion.div className="hero-content" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <h1 className="hero-title">{step === 5 ? 'INTELLIGENCE READY' : 'WORKSPACE'}</h1>
            <div className="glass-card main-dashboard">
              <div className="workflow-steps">
                {[1, 2, 3, 4, 5].map(s => <div key={s} className={`step-dot ${step >= s ? 'active' : ''} ${step === s ? 'current' : ''}`}></div>)}
              </div>
              
              <p className="status-text">{status || 'Select a lecture to begin processing.'}</p>

              {(step === 2 || step === 4) && (
                <div style={{ width: '100%' }}>
                  <div className="progress-container"><motion.div className="progress-bar" animate={{ width: `${progress}%` }} /><Loader2 className="spin progress-loader" /></div>
                  <div className="progress-percent">{progress}%</div>
                  {step === 2 && progress === 100 && (
                    <motion.button initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="btn-stellar" style={{ width: '100%', marginTop: '30px' }} onClick={() => setStep(3)}>Proceed to Generation <ChevronRight size={18} /></motion.button>
                  )}
                </div>
              )}

              {step === 3 && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                  <div className="model-selector-group">
                    <label className="group-label">Select AI Model</label>
                    <div className="model-selector">
                      {['BART', 'Phi-3', 'LLaMA-3'].map(m => (
                        <button 
                          key={m} 
                          className={`btn-stellar-outline ${selectedModel.includes(m.toLowerCase().split('-')[0]) ? 'active' : ''}`} 
                          onClick={() => {
                            if (m === 'LLaMA-3') setSelectedModel('llama3.1:8b');
                            else if (m === 'Phi-3') setSelectedModel('phi3:latest');
                            else setSelectedModel('bart');
                          }}
                        >
                          {m}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="info-box glass-card">
                    <Info size={16} color="var(--primary)" />
                    <p>
                      {selectedModel.includes('bart') 
                        ? 'BART creates a single core summary of your lecture.' 
                        : `${selectedModel.toUpperCase()} generates 3 document types: Short, Detailed, and Extreme notes.`}
                    </p>
                  </div>

                  <div className="options-row">
                    <label className="checkbox-container"><input type="checkbox" checked={options.pdf} onChange={e => setOptions({...options, pdf: e.target.checked})} /> Generate PDF</label>
                    <label className="checkbox-container"><input type="checkbox" checked={options.mcq} onChange={e => setOptions({...options, mcq: e.target.checked})} /> Generate MCQs</label>
                  </div>
                  <button className="btn-stellar" style={{ width: '100%' }} onClick={startSummarization}>Generate Knowledge Base</button>
                </motion.div>
              )}

              {step === 5 && (
                <div className="notes-preview glass-card">
                  <div className="notes-header"><h3>Detailed Notes for {selectedLecture}</h3><CheckCircle2 color="#10b981" /></div>
                  <div className="notes-body">{generatedNotes}</div>
                  <button className="btn-stellar" style={{ margin: '20px' }} onClick={() => { setStep(1); setGeneratedNotes(''); fetchLibrary(); }}>Archive & Finish</button>
                </div>
              )}

              {step === 1 && (
                <div className="empty-state" onClick={() => setIsSidebarOpen(true)}><FileAudio size={48} color="var(--text-muted)" /><p>Select a lecture to start.</p></div>
              )}
            </div>
          </motion.div>
        ) : (
          <motion.div className="hero-content" initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ width: '100%' }}>
            <h1 className="hero-title">INTELLIGENCE ARCHIVE</h1>
            <div className="library-grid">{libraryData.map(item => <LibraryCard key={item.lecture} item={item} />)}{libraryData.length === 0 && <p className="empty-msg">Archive is empty.</p>}</div>
          </motion.div>
        )}
      </section>
      <footer className="cinematic-footer"><p>&copy; 2026 Lecture to Notes. Processing Intelligence.</p></footer>
    </div>
  );
}

function LibraryCard({ item }) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="library-card glass-card">
      <div className="lib-card-header" onClick={() => setIsOpen(!isOpen)} style={{ cursor: 'pointer' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
          <h3 className={`lib-lecture-name ${isOpen ? 'expanded' : ''}`}>{item.lecture}</h3>
          {item.has_transcript && <a href={`${API_BASE}/view_notes/${item.lecture}/transcript.txt`} target="_blank" rel="noreferrer" className="badge transcript-link" onClick={(e) => e.stopPropagation()}>View Transcript <ExternalLink size={10} style={{ marginLeft: '4px' }} /></a>}
        </div>
        {isOpen ? <ChevronUp /> : <ChevronDown />}
      </div>
      <AnimatePresence>{isOpen && (
        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="lib-expanded-content">
          {item.models.map(m => (
            <div key={m.model} className="model-item">
              <div className="model-name">{m.model}</div>
              <div className="file-badges">
                {m.files.map(f => (
                  <a key={f} href={`${API_BASE}/view_notes/${item.lecture}/${m.model}/${f}`} target="_blank" rel="noreferrer" className="file-badge-link" onClick={(e) => e.stopPropagation()}>
                    <span className="file-badge">
                      {f.endsWith('.pdf') ? '📄 PDF' : f.includes('mcq') ? '❓ MCQ' : '📝 Notes'}
                      <span className="file-sub-name">{f} <ExternalLink size={10} /></span>
                    </span>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </motion.div>
      )}</AnimatePresence>
    </div>
  );
}

export default App;
