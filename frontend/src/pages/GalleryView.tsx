import { useQuery } from "@tanstack/react-query";
import { fetchPaintings } from "../api/paintings";
import { useGalleryStore } from "../store/galleryStore";
import GalleryGrid from "../components/GalleryGrid";
import FolderBreadcrumbs from "../components/FolderBreadcrumbs";
import GalleryFilters from "../components/GalleryFilters";
import { useAuthStore } from "../store/authStore";

const GalleryView = () => {
  const { search, folder, tag, format } = useGalleryStore();
  const { user } = useAuthStore();
  const userId = user?.id ?? 1;
  const { data, isLoading } = useQuery({
    queryKey: ["paintings", search, folder, tag, format, userId],
    queryFn: () =>
      fetchPaintings({
        q: search,
        folder,
        tag: tag || undefined,
        format: format === "ALL" ? undefined : format,
        user_id: userId
      })
  });

  return (
    <section>
      <FolderBreadcrumbs />
      <GalleryFilters />
      {isLoading && <p>Loading paintings...</p>}
      {data && <GalleryGrid paintings={data.items} />}
    </section>
  );
};

export default GalleryView;

