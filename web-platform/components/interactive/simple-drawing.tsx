"use client";

import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Trash2, Undo, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Point {
  x: number;
  y: number;
}

interface Stroke {
  points: Point[];
}

interface SimpleDrawingProps {
  targetChar?: string;
  onStrokeComplete?: (strokes: Stroke[]) => void;
  onClear?: () => void;
}

export function SimpleDrawing({ targetChar, onStrokeComplete, onClear }: SimpleDrawingProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [strokes, setStrokes] = useState<Stroke[]>([]);
  const [currentStroke, setCurrentStroke] = useState<Point[]>([]);

  // Draw on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw all completed strokes
    strokes.forEach((stroke) => {
      if (stroke.points.length < 2) return;
      
      ctx.beginPath();
      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      
      for (let i = 1; i < stroke.points.length; i++) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
      }
      
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 4;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.stroke();
    });

    // Draw current stroke
    if (currentStroke.length > 1) {
      ctx.beginPath();
      ctx.moveTo(currentStroke[0].x, currentStroke[0].y);
      
      for (let i = 1; i < currentStroke.length; i++) {
        ctx.lineTo(currentStroke[i].x, currentStroke[i].y);
      }
      
      ctx.strokeStyle = "#22c55e";
      ctx.lineWidth = 4;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.stroke();
    }
  }, [strokes, currentStroke]);

  // Get coordinates relative to canvas
  const getCoordinates = (e: React.MouseEvent | React.TouchEvent): Point | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    if ('touches' in e) {
      // Touch event
      const touch = e.touches[0];
      return {
        x: (touch.clientX - rect.left) * scaleX,
        y: (touch.clientY - rect.top) * scaleY,
      };
    } else {
      // Mouse event
      return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY,
      };
    }
  };

  // Mouse/Touch handlers
  const handleStart = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    const point = getCoordinates(e);
    if (point) {
      setIsDrawing(true);
      setCurrentStroke([point]);
    }
  };

  const handleMove = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing) return;
    
    const point = getCoordinates(e);
    if (point) {
      setCurrentStroke(prev => [...prev, point]);
    }
  };

  const handleEnd = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!isDrawing) return;

    if (currentStroke.length > 0) {
      const newStrokes = [...strokes, { points: currentStroke }];
      setStrokes(newStrokes);
      onStrokeComplete?.(newStrokes);
    }
    
    setIsDrawing(false);
    setCurrentStroke([]);
  };

  // Undo last stroke
  const undoStroke = () => {
    if (strokes.length > 0) {
      setStrokes(prev => prev.slice(0, -1));
    }
  };

  // Clear all
  const clearAll = () => {
    setStrokes([]);
    setCurrentStroke([]);
    onClear?.();
  };

  return (
    <div className="space-y-4">
      {/* Canvas Area */}
      <div className="relative aspect-[4/3] bg-white rounded-2xl overflow-hidden border-2 border-slate-200">
        {/* Grid background (米字格) */}
        <svg 
          className="absolute inset-0 w-full h-full pointer-events-none"
          viewBox="0 0 640 480"
          preserveAspectRatio="none"
        >
          {/* Outer border */}
          <rect x="20" y="20" width="600" height="440" fill="none" stroke="#E5E7EB" strokeWidth="2" />
          {/* Cross lines */}
          <line x1="320" y1="20" x2="320" y2="460" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
          <line x1="20" y1="240" x2="620" y2="240" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
          {/* Diagonal lines */}
          <line x1="20" y1="20" x2="620" y2="460" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
          <line x1="620" y1="20" x2="20" y2="460" stroke="#E5E7EB" strokeWidth="1" strokeDasharray="5,5" />
        </svg>

        {/* Target Character Overlay */}
        {targetChar && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <span className="text-[200px] text-slate-200 font-bold select-none">
              {targetChar}
            </span>
          </div>
        )}

        {/* Drawing Canvas */}
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="absolute inset-0 w-full h-full cursor-crosshair touch-none"
          onMouseDown={handleStart}
          onMouseMove={handleMove}
          onMouseUp={handleEnd}
          onMouseLeave={handleEnd}
          onTouchStart={handleStart}
          onTouchMove={handleMove}
          onTouchEnd={handleEnd}
        />

        {/* Drawing Status */}
        {isDrawing && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute top-4 right-4 px-3 py-1.5 rounded-full bg-green-500 text-white text-sm font-medium pointer-events-none"
          >
            <Pencil className="w-4 h-4 inline mr-1" />
            Đang vẽ...
          </motion.div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap justify-center gap-3">
        <Button
          onClick={undoStroke}
          variant="outline"
          disabled={strokes.length === 0}
          className="gap-2"
        >
          <Undo className="w-5 h-5" />
          Undo
        </Button>

        <Button
          onClick={clearAll}
          variant="outline"
          disabled={strokes.length === 0 && currentStroke.length === 0}
          className="gap-2"
        >
          <Trash2 className="w-5 h-5" />
          Xóa
        </Button>
      </div>

      {/* Instructions */}
      <div className="text-center space-y-2">
        <p className="text-sm text-slate-600 font-medium">
          💡 Hướng dẫn:
        </p>
        <p className="text-sm text-slate-500">
          🖱️ Desktop: Click và kéo chuột để vẽ
        </p>
        <p className="text-sm text-slate-500">
          📱 Mobile: Chạm và vuốt ngón tay để vẽ
        </p>
      </div>

      {/* Stroke count */}
      {strokes.length > 0 && (
        <div className="text-center">
          <span className="text-sm text-slate-500">
            Số nét đã vẽ: <strong className="text-primary">{strokes.length}</strong>
          </span>
        </div>
      )}
    </div>
  );
}
