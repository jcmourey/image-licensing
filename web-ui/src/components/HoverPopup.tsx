import React, { useState } from "react";

interface HoverPopupLinkProps {
  url: string;
  children: React.ReactNode; // The element to hover over
}

const HoverPopupLink: React.FC<HoverPopupLinkProps> = ({ url, children }) => {
  const [show, setShow] = useState(false);

  return (
    <span
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => {
        console.log('Hover preview imageUrl:', url);
        setShow(true);
      }}
      onMouseLeave={() => setShow(false)}
    >
      <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline font-medium hover:text-blue-800 visited:text-purple-600 transition-colors"
      >
        {children}
      </a>
      {show && (
        <div
          style={{
            position: "absolute",
            top: "1.5em",
            left: 0,
            zIndex: 100,
            background: "white",
            border: "1px solid #ccc",
            padding: 4,
            width: 400,
            height: 300,
            boxShadow: "0 4px 12px rgba(0,0,0,0.16)"
          }}
        >
          <iframe
            src={url}
            title="Link preview"
            width={390}
            height={290}
            style={{ border: "none" }}
          />
        </div>
      )}
    </span>
  );
};

export default HoverPopupLink;
// Usage example:
{/* <HoverPopupLink url={yourUrl}><button>Hover me</button></HoverPopupLink> */}
