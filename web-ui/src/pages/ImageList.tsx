import { useEffect, useState } from "react"

interface Image {
    id: string
    name: string
    thumbnail_url: string
    match_count: number
    license_count: number
    license_urls: string[]
    has_creative_commons_license: boolean
}

export default function ImageList() {
  const [images, setImages] = useState<Image[]>([])

  useEffect(() => {
    fetch("/api/images")
      .then(res => res.json())
      .then(setImages)
  }, [])

  return (
    <div className="max-w-7xl py-8 px-6 md:px-10 bg-gray-50 min-h-screen" style={{ marginLeft: "50px" }}>
      <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">Image Collection</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
        {images.map(img => (
          <div 
            key={img.id} 
            className="bg-white rounded-lg shadow-md transition-all duration-300 hover:shadow-lg m-2"
            style={{
              borderLeft: img.has_creative_commons_license ? '4px solid #10B981' : '1px solid #e5e7eb',
              borderTop: '1px solid #e5e7eb',
              borderRight: '1px solid #e5e7eb',
              borderBottom: '1px solid #e5e7eb'
            }}
          >
            <div className="bg-gray-100 flex items-center justify-between" 
                 style={{ 
                   height: '28px', 
                   paddingLeft: '16px', 
                   paddingRight: '16px'
                 }}>
              <h2 className="font-medium text-gray-800 truncate text-xs" 
                  title={img.name}>
                {img.name}
              </h2>
            </div>
            
            <div className="p-5 flex justify-center bg-gray-50">
              <img 
                src={img.thumbnail_url} 
                alt={img.name} 
                className="max-h-48 object-contain rounded shadow-sm"
              />
            </div>
            
            <div className="px-5 py-4 border-t border-gray-100">
              <div className="flex justify-between text-sm text-gray-600 mb-4">
                <div className="px-2 py-1 bg-gray-50 rounded-md">
                  <span className="font-medium">{img.match_count}</span> matches
                </div>
                <div className="px-2 py-1 bg-gray-50 rounded-md">
                  <span className="font-medium">{img.license_count}</span> licenses
                </div>
                <div className="px-2 py-1 bg-gray-50 rounded-md">
                  <span className="font-medium">{img.license_urls.length}</span> URLs
                </div>
              </div>
              
              {img.license_urls && img.license_urls.length > 0 && (
                <div className="mt-4 pt-3 border-t border-gray-100">
                  <h3 className="text-sm font-medium text-gray-700 mb-3 ml-1">
                    License{img.license_urls.length > 1 ? 's' : ''}:
                  </h3>
                  <div className="space-y-3">
                    {img.license_urls.slice(0, 4).map((licenseUrl, index) => (
                      <div key={index} className="text-xs bg-gray-50 rounded-md p-3 border border-gray-100 shadow-sm">
                        <a
                          href={licenseUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 hover:underline flex items-center justify-between"
                        >
                          <span className="inline-block mr-1 max-w-[200px]">
                            {licenseUrl.length > 100 
                              ? `${licenseUrl.substring(0, 50)}...${licenseUrl.substring(licenseUrl.length - 50)}`
                              : licenseUrl}
                          </span>
                        </a>
                      </div>
                    ))}
                    {img.license_urls.length > 4 && (
                      <div className="text-xs text-gray-500 pt-1 pl-2 mt-1">
                        +{img.license_urls.length - 4} more license{img.license_urls.length - 4 > 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}