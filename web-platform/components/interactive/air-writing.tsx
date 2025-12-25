"use client";

import { useEffect, useRef, useState } from "react";
import { Camera, CameraOff, Trash2, Undo, Hand, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Point {
  x: number;
  y: number;
}

interface Stroke {
  points: Point[];
}

interface AirWritingProps {
  targetChar?: string;
  onStrokeComplete?: (strokes: Stroke[]) => void;
  onClear?: () => void;
}

declare global {
  interface Window {
    Hands: any;
    Camera: any;
  }
}

export function AirWriting({ targetChar, onStrokeComplete, onClear }: AirWritingProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const persistentCanvasRef = useRef<HTMLCanvasElement | null>(null);
  
  const [cameraOn, setCameraOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [handStatus, setHandStatus] = useState("Đưa tay vào khung hình");
  const [statusColor, setStatusColor] = useState("yellow");
  
  // Drawing state - using refs to avoid re-render issues
  const drawingEnabledRef = useRef(false);
  const lastPointRef = useRef<Point | null>(null);
  const currentStrokeRef = useRef<Point[]>([]);
  const strokeHistoryRef = useRef<Stroke[]>([]);
  const handsRef = useRef<any>(null);
  const cameraInstanceRef = useRef<any>(null);
  const isDrawingRef = useRef(false);
  const lastDrawTimeRef = useRef(0);
  
  // Smoothing - simple weighted average like MVP
  const positionHistoryRef = useRef<Point[]>([]);
  
  // Constants - exactly like MVP
  const SMOOTH_FACTOR = 8;
  const MIN_MOVE_DISTANCE = 2;
  const MAX_JUMP_DISTANCE = 80;
  const DRAW_INTERVAL = 12;
  
  const loadScripts = async () => {
    const scripts = [
      "https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js",
      "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js",
    ];

    for (const src of scripts) {
      if (!document.querySelector(`script[src="${src}"]`)) {
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement("script");
          script.src = src;
          script.crossOrigin = "anonymous";
          script.onload = () => resolve();
          script.onerror = () => reject(new Error(`Failed to load ${src}`));
          document.head.appendChild(script);
        });
      }
    }
  };

  // Simple smoothing - exactly like MVP
  const smoothPosition = (rawX: number, rawY: number) => {
    positionHistoryRef.current.push({ x: rawX, y: rawY });
    if (positionHistoryRef.current.length > SMOOTH_FACTOR) {
      positionHistoryRef.current.shift();
    }
    
    const points = positionHistoryRef.current;
    let totalWeight = 0;
    let avgX = 0, avgY = 0;
    
    points.forEach((p, i) => {
      const weight = i + 1;
      avgX += p.x * weight;
      avgY += p.y * weight;
      totalWeight += weight;
    });
    
    return { x: avgX / totalWeight, y: avgY / totalWeight };
  };

  // Check if hand is open (all fingers extended) for erase
  const isHandOpen = (landmarks: any[]) => {
    const indexTip = landmarks[8], indexMcp = landmarks[5];
    const middleTip = landmarks[12], middleMcp = landmarks[9];
    const ringTip = landmarks[16], ringMcp = landmarks[13];
    const pinkyTip = landmarks[20], pinkyMcp = landmarks[17];
    
    const indexUp = indexTip.y < indexMcp.y;
    const middleUp = middleTip.y < middleMcp.y;
    const ringUp = ringTip.y < ringMcp.y;
    const pinkyUp = pinkyTip.y < pinkyMcp.y;
    
    return indexUp && middleUp && ringUp && pinkyUp;
  };

  const initCamera = async () => {
    setLoading(true);
    setError(null);

    try {
      await loadScripts();
      await new Promise(resolve => setTimeout(resolve, 500));

      if (!window.Hands || !window.Camera) {
        throw new Error("MediaPipe chưa sẵn sàng");
      }

      const hands = new window.Hands({
        locateFile: (file: string) => 
          `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });

      hands.onResults(onResults);
      handsRef.current = hands;

      const video = videoRef.current;
      if (!video) throw new Error("Video element not found");

      const camera = new window.Camera(video, {
        onFrame: async () => {
          if (handsRef.current && video) {
            await handsRef.current.send({ image: video });
          }
        },
        width: 640,
        height: 480,
      });

      await camera.start();
      cameraInstanceRef.current = camera;

      const persistentCanvas = document.createElement("canvas");
      persistentCanvas.width = 640;
      persistentCanvas.height = 480;
      persistentCanvasRef.current = persistentCanvas;

      setCameraOn(true);
      setLoading(false);

    } catch (err: any) {
      console.error("Camera init error:", err);
      setError(err.message || "Không thể khởi động camera");
      setLoading(false);
    }
  };

  const stopCamera = () => {
    if (cameraInstanceRef.current) {
      cameraInstanceRef.current.stop();
      cameraInstanceRef.current = null;
    }
    setCameraOn(false);
    setHandStatus("Đưa tay vào khung hình");
    positionHistoryRef.current = [];
  };

  const onResults = (results: any) => {
    const canvas = canvasRef.current;
    const persistentCanvas = persistentCanvasRef.current;
    if (!canvas || !persistentCanvas) return;

    const ctx = canvas.getContext("2d");
    const persistentCtx = persistentCanvas.getContext("2d");
    if (!ctx || !persistentCtx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    const gridSize = 340;
    const gridX = (canvas.width - gridSize) / 2;
    const gridY = (canvas.height - gridSize) / 2 + 15;

    ctx.fillStyle = "rgba(255, 255, 255, 0.08)";
    ctx.fillRect(gridX, gridY, gridSize, gridSize);

    ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
    ctx.lineWidth = 3;
    ctx.strokeRect(gridX, gridY, gridSize, gridSize);

    // Grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.15)";
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(gridX, gridY + gridSize / 2);
    ctx.lineTo(gridX + gridSize, gridY + gridSize / 2);
    ctx.moveTo(gridX + gridSize / 2, gridY);
    ctx.lineTo(gridX + gridSize / 2, gridY + gridSize);
    ctx.moveTo(gridX, gridY);
    ctx.lineTo(gridX + gridSize, gridY + gridSize);
    ctx.moveTo(gridX + gridSize, gridY);
    ctx.lineTo(gridX, gridY + gridSize);
    ctx.stroke();
    ctx.setLineDash([]);

    // Target character
    if (targetChar) {
      ctx.font = `${gridSize * 0.8}px "Noto Sans SC", "Microsoft YaHei", sans-serif`;
      ctx.fillStyle = "rgba(100, 150, 255, 0.15)";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(targetChar, gridX + gridSize / 2, gridY + gridSize / 2 + 10);
    }

    // Draw saved strokes
    ctx.drawImage(persistentCanvas, 0, 0);

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      const landmarks = results.multiHandLandmarks[0];
      const indexTip = landmarks[8];
      
      const rawX = (1 - indexTip.x) * canvas.width;
      const rawY = indexTip.y * canvas.height;
      const smoothed = smoothPosition(rawX, rawY);
      const x = smoothed.x;
      const y = smoothed.y;

      const inGrid = x >= gridX && x <= gridX + gridSize &&
                     y >= gridY && y <= gridY + gridSize;

      // Check for ERASE gesture (open hand) - only when NOT drawing
      if (!drawingEnabledRef.current && isHandOpen(landmarks)) {
        const palmCenter = landmarks[9];
        const palmX = (1 - palmCenter.x) * canvas.width;
        const palmY = palmCenter.y * canvas.height;
        
        // Draw erase indicator
        ctx.beginPath();
        ctx.arc(palmX, palmY, 50, 0, 2 * Math.PI);
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.fillStyle = "rgba(239, 68, 68, 0.2)";
        ctx.fill();
        
        // X icon
        ctx.beginPath();
        ctx.moveTo(palmX - 20, palmY - 20);
        ctx.lineTo(palmX + 20, palmY + 20);
        ctx.moveTo(palmX + 20, palmY - 20);
        ctx.lineTo(palmX - 20, palmY + 20);
        ctx.strokeStyle = "#ef4444";
        ctx.lineWidth = 4;
        ctx.stroke();

        setHandStatus("🖐️ Xòe tay = Xóa hết");
        setStatusColor("red");
        
        // Clear all
        clearAll();
        return;
      }

      // DRAW MODE - when Space is held
      if (drawingEnabledRef.current && inGrid) {
        const now = Date.now();

        if (!lastPointRef.current) {
          // Start new stroke
          lastPointRef.current = { x, y };
          lastDrawTimeRef.current = now;
          currentStrokeRef.current = [{ x, y }];
        }

        // Continue stroke
        if (now - lastDrawTimeRef.current >= DRAW_INTERVAL) {
          const dist = Math.sqrt(
            Math.pow(x - lastPointRef.current.x, 2) + 
            Math.pow(y - lastPointRef.current.y, 2)
          );

          if (dist >= MIN_MOVE_DISTANCE && dist < MAX_JUMP_DISTANCE) {
            // Draw line segment
            persistentCtx.beginPath();
            persistentCtx.moveTo(lastPointRef.current.x, lastPointRef.current.y);
            persistentCtx.lineTo(x, y);
            persistentCtx.strokeStyle = "#3b82f6";
            persistentCtx.lineWidth = 5;
            persistentCtx.lineCap = "round";
            persistentCtx.lineJoin = "round";
            persistentCtx.stroke();

            currentStrokeRef.current.push({ x, y });
            lastPointRef.current = { x, y };
            lastDrawTimeRef.current = now;
          }
        }

        isDrawingRef.current = true;

        // Green indicator when drawing
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = "#22c55e";
        ctx.fill();

        setHandStatus("✍️ Đang vẽ...");
        setStatusColor("green");

      } else {
        // Not drawing - save stroke if was drawing
        if (isDrawingRef.current && currentStrokeRef.current.length > 1) {
          strokeHistoryRef.current.push({ points: [...currentStrokeRef.current] });
          onStrokeComplete?.(strokeHistoryRef.current);
        }
        
        lastPointRef.current = null;
        isDrawingRef.current = false;
        currentStrokeRef.current = [];

        // Yellow/red indicator
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, 2 * Math.PI);
        ctx.fillStyle = inGrid ? "rgba(249, 158, 11, 0.8)" : "rgba(255, 100, 100, 0.5)";
        ctx.fill();

        setHandStatus(inGrid ? "👆 Giữ SPACE để vẽ" : "⚠️ Đưa tay vào ô");
        setStatusColor(inGrid ? "yellow" : "red");
      }

    } else {
      // No hand detected
      setHandStatus("🖐️ Không thấy tay");
      setStatusColor("red");
      
      if (isDrawingRef.current && currentStrokeRef.current.length > 1) {
        strokeHistoryRef.current.push({ points: [...currentStrokeRef.current] });
        onStrokeComplete?.(strokeHistoryRef.current);
      }
      
      lastPointRef.current = null;
      isDrawingRef.current = false;
      currentStrokeRef.current = [];
      positionHistoryRef.current = [];
    }
  };

  const startDrawing = () => {
    drawingEnabledRef.current = true;
  };

  const stopDrawing = () => {
    drawingEnabledRef.current = false;
    
    if (isDrawingRef.current && currentStrokeRef.current.length > 1) {
      strokeHistoryRef.current.push({ points: [...currentStrokeRef.current] });
      onStrokeComplete?.(strokeHistoryRef.current);
    }
    
    lastPointRef.current = null;
    isDrawingRef.current = false;
    currentStrokeRef.current = [];
  };

  const undoStroke = () => {
    if (strokeHistoryRef.current.length > 0) {
      strokeHistoryRef.current.pop();
      redrawCanvas();
    }
  };

  const clearAll = () => {
    strokeHistoryRef.current = [];
    currentStrokeRef.current = [];
    
    const persistentCanvas = persistentCanvasRef.current;
    if (persistentCanvas) {
      const ctx = persistentCanvas.getContext("2d");
      if (ctx) ctx.clearRect(0, 0, persistentCanvas.width, persistentCanvas.height);
    }
    onClear?.();
  };

  const redrawCanvas = () => {
    const persistentCanvas = persistentCanvasRef.current;
    if (!persistentCanvas) return;

    const ctx = persistentCanvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, persistentCanvas.width, persistentCanvas.height);
    
    strokeHistoryRef.current.forEach((stroke) => {
      if (stroke.points.length < 2) return;
      
      ctx.beginPath();
      ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
      
      for (let i = 1; i < stroke.points.length; i++) {
        ctx.lineTo(stroke.points[i].x, stroke.points[i].y);
      }
      
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 5;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.stroke();
    });
  };

  // Keyboard
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.code === "Space" && cameraOn) {
        e.preventDefault();
        startDrawing();
      }
    };
    const onKeyUp = (e: KeyboardEvent) => {
      if (e.code === "Space") {
        e.preventDefault();
        stopDrawing();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  }, [cameraOn]);

  useEffect(() => {
    return () => { stopCamera(); };
  }, []);

  const statusBg = statusColor === "green" ? "bg-green-500/20 text-green-400" :
                   statusColor === "red" ? "bg-red-500/20 text-red-400" :
                   "bg-yellow-500/20 text-yellow-400";

  return (
    <div className="space-y-4">
      <div className="relative aspect-[4/3] bg-slate-900 rounded-2xl overflow-hidden">
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover opacity-15 grayscale scale-x-[-1]"
          autoPlay playsInline muted
        />
        <canvas
          ref={canvasRef}
          width={640}
          height={480}
          className="absolute inset-0 w-full h-full"
        />

        {!cameraOn && !loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80">
            <Camera className="w-16 h-16 text-slate-500 mb-4" />
            <p className="text-slate-400 text-center px-4">Bật camera để bắt đầu Air Writing</p>
          </div>
        )}

        {loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4" />
            <p className="text-slate-400">Đang tải MediaPipe...</p>
          </div>
        )}

        {cameraOn && (
          <div className={`absolute top-4 left-4 px-3 py-1.5 rounded-full text-sm font-medium flex items-center gap-2 ${statusBg}`}>
            <Hand className="w-4 h-4" />
            {handStatus}
          </div>
        )}

        {error && (
          <div className="absolute bottom-4 left-4 right-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-2 text-red-400 text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            {error}
          </div>
        )}
      </div>

      <div className="flex flex-wrap justify-center gap-3">
        <Button
          onClick={cameraOn ? stopCamera : initCamera}
          variant={cameraOn ? "destructive" : "default"}
          disabled={loading}
          className="gap-2"
        >
          {cameraOn ? <CameraOff className="w-5 h-5" /> : <Camera className="w-5 h-5" />}
          {loading ? "Đang tải..." : cameraOn ? "Tắt Camera" : "Bật Camera"}
        </Button>

        {cameraOn && (
          <>
            <Button
              onMouseDown={startDrawing}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
              onTouchStart={startDrawing}
              onTouchEnd={stopDrawing}
              variant="secondary"
              className="gap-2"
            >
              <Hand className="w-5 h-5" />
              Giữ để vẽ (Space)
            </Button>

            <Button onClick={undoStroke} variant="outline" className="gap-2">
              <Undo className="w-5 h-5" />
              Undo
            </Button>

            <Button onClick={clearAll} variant="outline" className="gap-2">
              <Trash2 className="w-5 h-5" />
              Xóa hết
            </Button>
          </>
        )}
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800 font-medium mb-2">📖 Hướng dẫn:</p>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>☝️ <strong>Vẽ:</strong> Giữ <kbd className="px-1 py-0.5 bg-white rounded text-xs border">Space</kbd> và di chuyển ngón trỏ</li>
          <li>🖐️ <strong>Xóa:</strong> Xòe bàn tay = xóa hết, viết lại từ đầu</li>
          <li>↩️ <strong>Undo:</strong> Hoàn tác nét cuối</li>
        </ul>
      </div>
    </div>
  );
}
