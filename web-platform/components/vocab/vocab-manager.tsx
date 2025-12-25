"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  Download,
  Cloud,
  CloudOff,
  Trash2,
  Star,
  StarOff,
  FileText,
  RefreshCw,
  Check,
  X,
  Search,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  getVocabList,
  setVocabList,
  addToVocabList,
  getFavorites,
  toggleFavorite,
  exportToAnkiCSV,
  parseCSV,
  exportAllData,
  importAllData,
  VocabItem,
} from "@/lib/storage";

interface VocabManagerProps {
  onSelectChar?: (char: string) => void;
  selectedChar?: string;
}

export function VocabManager({ onSelectChar, selectedChar }: VocabManagerProps) {
  const [vocabList, setVocabListState] = useState<VocabItem[]>([]);
  const [favorites, setFavoritesState] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"all" | "favorites" | "import">("all");
  const [importing, setImporting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load data on mount
  useEffect(() => {
    setVocabListState(getVocabList());
    setFavoritesState(getFavorites());
  }, []);

  // Filter vocab list
  const filteredList = vocabList.filter((item) => {
    const matchesSearch =
      !searchQuery ||
      item.char.includes(searchQuery) ||
      item.pinyin.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.meaning.toLowerCase().includes(searchQuery.toLowerCase());

    if (activeTab === "favorites") {
      return matchesSearch && favorites.includes(item.char);
    }
    return matchesSearch;
  });

  // Handle file import
  const handleFileImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImporting(true);
    try {
      const content = await file.text();
      
      if (file.name.endsWith(".json")) {
        // Import full backup
        const success = importAllData(content);
        if (success) {
          setVocabListState(getVocabList());
          setFavoritesState(getFavorites());
          showMessage("success", "Đã import dữ liệu thành công!");
        } else {
          showMessage("error", "File không hợp lệ");
        }
      } else {
        // Import CSV
        const items = parseCSV(content);
        if (items.length > 0) {
          addToVocabList(items);
          setVocabListState(getVocabList());
          showMessage("success", `Đã thêm ${items.length} chữ mới!`);
        } else {
          showMessage("error", "Không tìm thấy chữ Hán trong file");
        }
      }
    } catch (error) {
      showMessage("error", "Lỗi khi đọc file");
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  // Export functions
  const handleExportCSV = () => {
    const csv = exportToAnkiCSV();
    downloadFile(csv, "polybiz_vocab.csv", "text/csv");
    showMessage("success", "Đã xuất file CSV cho Anki!");
  };

  const handleExportJSON = () => {
    const json = exportAllData();
    downloadFile(json, "polybiz_backup.json", "application/json");
    showMessage("success", "Đã xuất file backup!");
  };

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Toggle favorite
  const handleToggleFavorite = (char: string) => {
    toggleFavorite(char);
    setFavoritesState(getFavorites());
  };

  // Remove character
  const handleRemoveChar = (char: string) => {
    const newList = vocabList.filter((item) => item.char !== char);
    setVocabList(newList);
    setVocabListState(newList);
  };

  // Show message
  const showMessage = (type: "success" | "error", text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-slate-800">📖 Quản lý từ vựng</h3>
        <span className="px-3 py-1 bg-primary/10 text-primary text-sm rounded-full">
          {vocabList.length} chữ
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {[
          { id: "all", label: "Tất cả" },
          { id: "favorites", label: "⭐ Yêu thích" },
          { id: "import", label: "📥 Import/Export" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-primary text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Message */}
      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
              message.type === "success"
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {message.type === "success" ? (
              <Check className="w-4 h-4" />
            ) : (
              <X className="w-4 h-4" />
            )}
            {message.text}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Import/Export Tab */}
      {activeTab === "import" && (
        <div className="space-y-4">
          {/* Import */}
          <div className="p-4 bg-slate-50 rounded-xl">
            <h4 className="font-medium text-slate-800 mb-3">📥 Import</h4>
            <div className="space-y-3">
              <div>
                <label className="block text-sm text-slate-600 mb-2">
                  Import từ CSV hoặc JSON backup:
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.txt,.json"
                  onChange={handleFileImport}
                  className="hidden"
                />
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="gap-2"
                  disabled={importing}
                >
                  {importing ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Upload className="w-4 h-4" />
                  )}
                  Chọn file
                </Button>
              </div>
              <p className="text-xs text-slate-500">
                Hỗ trợ: CSV (mỗi dòng 1 chữ), Anki export (.txt), JSON backup
              </p>
            </div>
          </div>

          {/* Export */}
          <div className="p-4 bg-slate-50 rounded-xl">
            <h4 className="font-medium text-slate-800 mb-3">📤 Export</h4>
            <div className="flex flex-wrap gap-3">
              <Button onClick={handleExportCSV} variant="outline" className="gap-2">
                <FileText className="w-4 h-4" />
                Export CSV (Anki)
              </Button>
              <Button onClick={handleExportJSON} variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Backup JSON
              </Button>
            </div>
          </div>

          {/* Google Drive (Coming Soon) */}
          <div className="p-4 bg-slate-50 rounded-xl opacity-60">
            <h4 className="font-medium text-slate-800 mb-3 flex items-center gap-2">
              <Cloud className="w-4 h-4" />
              Google Drive Sync
              <span className="px-2 py-0.5 bg-slate-200 text-slate-600 text-xs rounded">
                Coming Soon
              </span>
            </h4>
            <p className="text-sm text-slate-500">
              Đồng bộ danh sách từ vựng với Google Drive để sử dụng trên nhiều thiết bị.
            </p>
          </div>
        </div>
      )}

      {/* Vocab List Tab */}
      {(activeTab === "all" || activeTab === "favorites") && (
        <>
          {/* Search */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Tìm kiếm..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          {/* Character Grid */}
          <div className="max-h-[300px] overflow-y-auto">
            {filteredList.length > 0 ? (
              <div className="grid grid-cols-5 sm:grid-cols-8 gap-2">
                {filteredList.map((item) => (
                  <motion.button
                    key={item.char}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => onSelectChar?.(item.char)}
                    className={`relative p-2 rounded-lg text-center transition-all ${
                      selectedChar === item.char
                        ? "bg-primary text-white shadow-lg"
                        : "bg-slate-100 hover:bg-slate-200"
                    }`}
                  >
                    <span className="text-2xl block">{item.char}</span>
                    <span className="text-[10px] text-slate-500 block truncate">
                      {item.pinyin}
                    </span>

                    {/* Favorite indicator */}
                    {favorites.includes(item.char) && (
                      <span className="absolute -top-1 -right-1 text-yellow-500 text-xs">
                        ⭐
                      </span>
                    )}
                  </motion.button>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-500">
                {activeTab === "favorites"
                  ? "Chưa có chữ yêu thích"
                  : "Chưa có từ vựng. Import để bắt đầu!"}
              </div>
            )}
          </div>

          {/* Selected Character Actions */}
          {selectedChar && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 p-3 bg-slate-50 rounded-lg flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <span className="text-3xl">{selectedChar}</span>
                <div>
                  <p className="font-medium text-slate-800">
                    {vocabList.find((v) => v.char === selectedChar)?.pinyin}
                  </p>
                  <p className="text-sm text-slate-500">
                    {vocabList.find((v) => v.char === selectedChar)?.meaning}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleToggleFavorite(selectedChar)}
                >
                  {favorites.includes(selectedChar) ? (
                    <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                  ) : (
                    <StarOff className="w-4 h-4" />
                  )}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRemoveChar(selectedChar)}
                  className="text-red-500 hover:text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </motion.div>
          )}
        </>
      )}
    </div>
  );
}
