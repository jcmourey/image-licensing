import React, { useState } from 'react';

interface UsedInDropdownProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  onBlur: () => void;
  placeholder?: string;
}

const UsedInDropdown: React.FC<UsedInDropdownProps> = ({
  value,
  options,
  onChange,
  onBlur,
  placeholder = "Enter or select usage information..."
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Handle option selection
  const handleSelectOption = (option: string) => {
    onChange(option);
    setIsOpen(false);
    // Directly save after selection
    onBlur();
  };
  
  // Filtered options based on current value
  const filteredOptions = options.filter(option => 
    !value || option.toLowerCase().includes(value.toLowerCase())
  );
  
  return (
    <div className="relative w-full">
      {/* Input field */}
      <div className="flex items-center w-full">
        <input
          type="text"
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsOpen(true)}
          onBlur={() => {
            // Delay closing dropdown to allow option clicks to register
            setTimeout(() => setIsOpen(false), 200);
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              onBlur(); // Save on Enter
              setIsOpen(false);
            }
          }}
          placeholder={placeholder}
          autoFocus
        />
        
        {/* Dropdown toggle button */}
        <button
          type="button"
          className="absolute right-2 top-1/2 -translate-y-1/2 transform text-gray-500"
          onClick={(e) => {
            e.preventDefault();
            setIsOpen(!isOpen);
          }}
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {isOpen ? (
              <polyline points="18 15 12 9 6 15"></polyline>
            ) : (
              <polyline points="6 9 12 15 18 9"></polyline>
            )}
          </svg>
        </button>
      </div>
      
      {/* Dropdown options */}
      {isOpen && filteredOptions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
          {filteredOptions.map((option, index) => (
            <button
              key={index}
              className="w-full text-left px-4 py-2 cursor-pointer hover:bg-blue-50 text-sm"
              onMouseDown={(e) => {
                e.preventDefault();
                handleSelectOption(option);
              }}
            >
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default UsedInDropdown;
