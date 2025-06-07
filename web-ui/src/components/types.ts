export interface Image {
  id: string;
  name: string;
  thumbnail_url: string;
  match_count: number;
  license_urls: string[];
  is_approved: boolean;
  match_page_urls: string[];
  match_image_urls: string[];
}
