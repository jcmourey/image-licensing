import { useState, useEffect } from 'react';

interface ImagePopupProps {
  imageUrl: string;
  alt?: string;
}

const ImagePopup = ({ imageUrl, alt = "Full size image" }: ImagePopupProps) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [visible, setVisible] = useState(false);

  // Update position on mouse move
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Position the popup with an offset from the cursor
      const offset = 20;
      
      // Calculate position to keep popup on screen
      const x = Math.min(e.clientX + offset, window.innerWidth - 320);
      const y = Math.min(e.clientY + offset, window.innerHeight - 320);
      
      setPosition({ x, y });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    setVisible(true);
    
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div 
      className="fixed z-50 bg-white border border-gray-300 shadow-xl rounded p-2"
      style={{
        left: position.x,
        top: position.y,
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.2s',
        maxWidth: '300px',
        maxHeight: '300px'
      }}
    >
      <img 
        src={imageUrl} 
        alt={alt} 
        className="max-w-full max-h-full object-contain"
      />
    </div>
  );
};

export default ImagePopup;
