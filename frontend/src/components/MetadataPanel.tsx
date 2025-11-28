import { useEffect, useState } from "react";
import type { Painting } from "../api/paintings";
import { createPainting, updatePainting } from "../api/paintings";
import { useAuthStore } from "../store/authStore";

type Props = {
  painting?: Painting;
};

const MetadataPanel = ({ painting }: Props) => {
  const [title, setTitle] = useState(painting?.title ?? "");
  const [folder, setFolder] = useState(painting?.folder ?? "");
  const [tags, setTags] = useState(painting?.tags ?? "");
  const [format, setFormat] = useState(painting?.format ?? "PNG");
  const [status, setStatus] = useState<string | null>(null);
  const [lastSaved, setLastSaved] = useState<string | null>(null);
  const { user } = useAuthStore();

  useEffect(() => {
    setTitle(painting?.title ?? "");
    setFolder(painting?.folder ?? "");
    setTags(painting?.tags ?? "");
    setFormat(painting?.format ?? "PNG");
  }, [painting]);

  const save = async () => {
    const canvas = document.querySelector("canvas");
    if (!canvas) return;
    setStatus("Saving...");
    const mime =
      format === "JPEG" ? "image/jpeg" : format === "WEBP" ? "image/webp" : "image/png";
    const blob = await new Promise<Blob | null>((resolve) =>
      canvas.toBlob((result) => resolve(result), mime)
    );

    if (!blob) {
      setStatus("Failed to capture canvas");
      return;
    }
    const data = new FormData();
    const userId = painting?.user_id ?? user?.id ?? 1;
    data.append("user_id", String(userId));
    data.append("title", title);
    data.append("folder", folder);
    data.append("tags", tags);
    data.append("format", format);
    const extension = format === "JPEG" ? "jpg" : format.toLowerCase();
    data.append("image", blob, `${title || "untitled"}.${extension}`);

    try {
      if (painting) {
        await updatePainting(String(painting.id), data);
      } else {
        await createPainting(data);
      }
      const timestamp = new Date().toLocaleTimeString();
      setLastSaved(timestamp);
      setStatus(`Saved at ${timestamp}`);
    } catch (error) {
      setStatus("Save failed");
      console.error(error);
    }
  };

  return (
    <aside className="metadata-panel">
      <h2>Metadata</h2>
      <label>
        Title
        <input value={title} onChange={(event) => setTitle(event.target.value)} />
      </label>
      <label>
        Folder
        <input
          value={folder}
          onChange={(event) => setFolder(event.target.value)}
        />
      </label>
      <label>
        Tags
        <input value={tags} onChange={(event) => setTags(event.target.value)} />
      </label>
      <label>
        Format
        <select value={format} onChange={(event) => setFormat(event.target.value)}>
          <option value="PNG">PNG</option>
          <option value="JPEG">JPEG</option>
          <option value="WEBP">WEBP</option>
        </select>
      </label>
      {painting?.width && painting?.height && (
        <p className="metadata-panel__info">
          {painting.width} × {painting.height} — {painting.format}
        </p>
      )}
      <button onClick={save}>Save painting</button>
      {status && <p className="status">{status}</p>}
      {lastSaved && <p className="metadata-panel__info">Last saved {lastSaved}</p>}
    </aside>
  );
};

export default MetadataPanel;

