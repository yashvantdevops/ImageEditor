import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { Painting } from "../api/paintings";
import { useWasmTools } from "../hooks/useWasmTools";
import { importRemoteImage } from "../api/paintings";

type Props = {
  painting?: Painting;
};

const DEFAULT_WIDTH = 1024;
const DEFAULT_HEIGHT = 768;

const CanvasEditor = ({ painting }: Props) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const lastPoint = useRef<{ x: number; y: number } | null>(null);
  const engineRef = useRef<any | null>(null);

  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState("#ff5c5c");
  const [brushSize, setBrushSize] = useState(24);
  const [opacity, setOpacity] = useState(0.85);
  const [softness, setSoftness] = useState(0.5);
  const [isEraser, setIsEraser] = useState(false);
  const [importUrl, setImportUrl] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [fillMode, setFillMode] = useState(false);

  const { bindings, error } = useWasmTools();

  const render = useCallback(() => {
    if (!bindings || !engineRef.current || !canvasRef.current) return;
    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;
    const pixels = engineRef.current.export_pixels();
    const width = engineRef.current.width();
    const height = engineRef.current.height();
    const data = new ImageData(new Uint8ClampedArray(pixels), width, height);
    canvasRef.current.width = width;
    canvasRef.current.height = height;
    ctx.putImageData(data, 0, 0);
  }, [bindings]);

  useEffect(() => {
    if (!bindings) return;
    engineRef.current = new bindings.CanvasEngine(DEFAULT_WIDTH, DEFAULT_HEIGHT);
    render();
  }, [bindings, render]);

  const loadImage = useCallback(
    async (src: string) => {
      if (!bindings || !engineRef.current) return;
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = src;
      await img.decode();
      const temp = document.createElement("canvas");
      temp.width = img.width;
      temp.height = img.height;
      const ctx = temp.getContext("2d");
      if (!ctx) return;
      ctx.drawImage(img, 0, 0);
      const data = ctx.getImageData(0, 0, img.width, img.height);
      engineRef.current.load_pixels(new Uint8Array(data.data), data.width, data.height);
      render();
    },
    [bindings, render]
  );

  useEffect(() => {
    if (painting?.image_url) {
      loadImage(painting.image_url);
    }
  }, [painting, loadImage]);

  const pointerPosition = (event: { clientX: number; clientY: number }) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return { x: 0, y: 0 };
    return {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
  };

  const handlePointerDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!bindings || !engineRef.current) return;
    const { x, y } = pointerPosition(event);
    if (fillMode) {
      floodFillAt(x, y);
      setIsDrawing(false);
      return;
    }
    setIsDrawing(true);
    lastPoint.current = { x, y };
    drawStroke(x, y);
  };

  const handlePointerUp = () => {
    setIsDrawing(false);
    lastPoint.current = null;
  };

  const drawStroke = (x: number, y: number) => {
    if (!bindings || !engineRef.current) return;
    const start = lastPoint.current ?? { x, y };
    const rgb = hexToRgb(color);
    const brush = new bindings.BrushOptions(
      brushSize,
      softness,
      opacity,
      rgb.r,
      rgb.g,
      rgb.b
    );
    engineRef.current.apply_brush(start.x, start.y, x, y, brush, isEraser);
    lastPoint.current = { x, y };
    render();
  };

  const handlePointerMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const { x, y } = pointerPosition(event);
    drawStroke(x, y);
  };

  const touchPoint = (event: React.TouchEvent<HTMLCanvasElement>) => {
    const touch = event.touches[0] || event.changedTouches[0];
    return touch ? pointerPosition(touch) : { x: 0, y: 0 };
  };

  const handleTouchStart = (event: React.TouchEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    if (!bindings || !engineRef.current) return;
    const { x, y } = touchPoint(event);
    if (fillMode) {
      floodFillAt(x, y);
      return;
    }
    setIsDrawing(true);
    lastPoint.current = { x, y };
    drawStroke(x, y);
  };

  const handleTouchMove = (event: React.TouchEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    event.preventDefault();
    const { x, y } = touchPoint(event);
    drawStroke(x, y);
  };

  const handleTouchEnd = (event: React.TouchEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    setIsDrawing(false);
    lastPoint.current = null;
  };

  const applyFilter = (type: number, amount = 0.8) => {
    if (!bindings || !engineRef.current) return;
    engineRef.current.apply_filter(type, amount);
    render();
  };

  const undo = () => {
    if (engineRef.current?.undo()) {
      render();
    }
  };

  const redo = () => {
    if (engineRef.current?.redo()) {
      render();
    }
  };

  const floodFillAt = (x: number, y: number) => {
    if (!bindings || !engineRef.current) return;
    const rgb = hexToRgb(color);
    const brush = new bindings.BrushOptions(brushSize, softness, opacity, rgb.r, rgb.g, rgb.b);
    engineRef.current.flood_fill(Math.floor(x), Math.floor(y), brush);
    render();
  };

  const handleImportUrl = async () => {
    if (!importUrl.trim()) return;
    setStatus("Importing image...");
    try {
      const data = await importRemoteImage({ image_url: importUrl });
      await loadImage(data.data_url);
      setStatus("Image imported");
    } catch (err) {
      console.error(err);
      setStatus("Import failed");
    }
  };

  const handleLocalImport = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setStatus("Importing image...");
    const url = URL.createObjectURL(file);
    await loadImage(url);
    URL.revokeObjectURL(url);
    setStatus("Image imported");
  };

  return (
    <section className="canvas-pane">
      <div className="toolbar">
        <label>
          Brush
          <input type="color" value={color} onChange={(event) => setColor(event.target.value)} />
        </label>
        <label>
          Size
          <input
            type="range"
            min={1}
            max={128}
            value={brushSize}
            onChange={(event) => setBrushSize(Number(event.target.value))}
          />
        </label>
        <label>
          Softness
          <input
            type="range"
            min={0.1}
            max={1}
            step={0.1}
            value={softness}
            onChange={(event) => setSoftness(Number(event.target.value))}
          />
        </label>
        <label>
          Opacity
          <input
            type="range"
            min={0.1}
            max={1}
            step={0.05}
            value={opacity}
            onChange={(event) => setOpacity(Number(event.target.value))}
          />
        </label>
        <button type="button" onClick={() => setIsEraser((prev) => !prev)}>
          {isEraser ? "Disable Eraser" : "Eraser"}
        </button>
        <button
          type="button"
          className={fillMode ? "active" : ""}
          onClick={() => setFillMode((prev) => !prev)}
        >
          {fillMode ? "Exit Fill" : "Fill Mode"}
        </button>
        <button type="button" onClick={undo}>
          Undo
        </button>
        <button type="button" onClick={redo}>
          Redo
        </button>
        <div className="filters">
          <button type="button" onClick={() => applyFilter(bindings?.FilterType.Blur ?? 0, 0.6)}>
            Blur
          </button>
          <button
            type="button"
            onClick={() => applyFilter(bindings?.FilterType.Sharpen ?? 1, 1)}
          >
            Sharpen
          </button>
          <button type="button" onClick={() => applyFilter(bindings?.FilterType.Invert ?? 2, 1)}>
            Invert
          </button>
          <button
            type="button"
            onClick={() => applyFilter(bindings?.FilterType.Grayscale ?? 3, 1)}
          >
            Grayscale
          </button>
        </div>
        {error && <span className="badge warning">{error}</span>}
        {bindings && !error && (
          <span className="badge success">{fillMode ? "Fill active" : "WASM ready"}</span>
        )}
      </div>

      <div className="import-tools">
        <label className="import-link">
          Import from URL
          <input
            type="url"
            placeholder="https://example.com/art.png"
            value={importUrl}
            onChange={(event) => setImportUrl(event.target.value)}
          />
        </label>
        <button type="button" onClick={handleImportUrl}>
          Import
        </button>
        <label className="import-file">
          Import file
          <input type="file" accept="image/*" onChange={handleLocalImport} />
        </label>
        {status && <span className="status">{status}</span>}
      </div>

      <canvas
        ref={canvasRef}
        width={DEFAULT_WIDTH}
        height={DEFAULT_HEIGHT}
        onMouseDown={handlePointerDown}
        onMouseUp={handlePointerUp}
        onMouseMove={handlePointerMove}
        onMouseLeave={handlePointerUp}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onTouchCancel={handleTouchEnd}
      />
    </section>
  );
};

const hexToRgb = (hex: string) => {
  const normalized = hex.replace("#", "");
  const bigint = parseInt(normalized, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255
  };
};

export default CanvasEditor;

