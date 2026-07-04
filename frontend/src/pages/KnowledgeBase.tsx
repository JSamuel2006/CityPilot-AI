import { useState, useRef } from 'react';
import { UploadCloud, File as FileIcon, Trash2, BookOpen, FileText, Table } from 'lucide-react';

interface UploadedFile {
  name: string;
  size: number;
  type: string;
}

const getFileIcon = (name: string) => {
  if (name.endsWith('.pdf')) return <FileText size={18} className="text-danger" />;
  if (name.endsWith('.csv')) return <Table size={18} className="text-success" />;
  return <FileIcon size={18} className="text-info" />;
};

const KnowledgeBase = () => {
  const [files, setFiles] = useState<UploadedFile[]>([
    { name: 'City_Emergency_Protocol_2026.pdf', size: 2400000, type: 'pdf' },
    { name: 'Ward_Population_Census.csv', size: 850000, type: 'csv' },
    { name: 'Drainage_Infrastructure_Report.pdf', size: 5200000, type: 'pdf' },
    { name: 'Budget_Allocation_Q2.docx', size: 320000, type: 'docx' },
  ]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map(f => ({ name: f.name, size: f.size, type: f.name.split('.').pop() || '' }));
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6 fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-text-primary tracking-tight flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary/20 flex items-center justify-center">
            <BookOpen size={20} className="text-primary" />
          </div>
          Knowledge Base
        </h1>
        <p className="text-sm text-text-muted mt-2 ml-12">Upload city policies, protocols, and data to enhance AI decision context</p>
      </div>

      {/* Upload Zone */}
      <div
        className="glass rounded-xl p-10 border-2 border-dashed border-border hover:border-primary/30 transition-all cursor-pointer flex flex-col items-center justify-center max-w-3xl"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="w-14 h-14 rounded-xl bg-white/[0.03] border border-border flex items-center justify-center mb-4">
          <UploadCloud size={24} className="text-text-muted" />
        </div>
        <h3 className="text-sm font-semibold text-text-primary mb-1">Drop files here or click to browse</h3>
        <p className="text-xs text-text-muted">PDF, DOCX, CSV — max 50MB per file</p>
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.csv"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="max-w-3xl">
          <h3 className="text-sm font-semibold text-text-primary mb-3">Uploaded Documents ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, i) => (
              <div key={i} className="glass rounded-lg p-3.5 flex items-center gap-3 group hover:glass-hover transition-all">
                <div className="w-9 h-9 rounded-lg bg-white/[0.03] border border-border flex items-center justify-center shrink-0">
                  {getFileIcon(file.name)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-text-primary font-medium truncate">{file.name}</p>
                  <p className="text-[10px] text-text-muted mt-0.5">{(file.size / 1024 / 1024).toFixed(2)} MB • Uploaded</p>
                </div>
                <button
                  onClick={(e) => { e.stopPropagation(); removeFile(i); }}
                  className="p-2 rounded-lg text-text-muted hover:text-danger hover:bg-danger/10 transition-colors opacity-0 group-hover:opacity-100"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBase;
